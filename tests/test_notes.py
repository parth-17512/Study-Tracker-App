import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base, Database
from app.services.note_service import NoteService

# In-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

class MockDatabase(Database):
    def __init__(self):
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

@pytest.fixture
def note_service():
    mock_db = MockDatabase()
    return NoteService(db_override=mock_db)

def test_folder_creation(note_service):
    folder = note_service.create_node("My Folder", is_folder=True)
    assert folder.id is not None
    assert folder.name == "My Folder"
    assert folder.is_folder is True
    
def test_nested_folders_and_notes(note_service):
    parent = note_service.create_node("Parent", is_folder=True)
    child_folder = note_service.create_node("Child", is_folder=True, parent_id=parent.id)
    note = note_service.create_node("Note 1", is_folder=False, parent_id=child_folder.id)
    
    assert child_folder.parent_id == parent.id
    assert note.parent_id == child_folder.id
    
    tree = note_service.get_all_nodes()
    assert len(tree) == 3

def test_note_editing_and_persistence(note_service):
    note = note_service.create_node("My Note", is_folder=False)
    
    # Initial content should be empty string
    assert note.content == ""
    
    # Edit content
    markdown_text = "# Hello\nThis is a **test**."
    success = note_service.update_node_content(note.id, markdown_text)
    assert success is True
    
    # Fetch again to verify persistence
    updated_note = note_service.get_note(note.id)
    assert updated_note.content == markdown_text

def test_note_movement(note_service):
    folder1 = note_service.create_node("Folder 1", is_folder=True)
    folder2 = note_service.create_node("Folder 2", is_folder=True)
    note = note_service.create_node("Note", is_folder=False, parent_id=folder1.id)
    
    assert note.parent_id == folder1.id
    
    success = note_service.move_node(note.id, folder2.id)
    assert success is True
    
    moved_note = note_service.get_note(note.id)
    assert moved_note.parent_id == folder2.id

def test_invalid_circular_folder_movement(note_service):
    parent = note_service.create_node("Parent", is_folder=True)
    child = note_service.create_node("Child", is_folder=True, parent_id=parent.id)
    
    # Cannot move parent into its own child
    success = note_service.move_node(parent.id, child.id)
    assert success is False
    
    # Cannot move folder into itself
    success = note_service.move_node(parent.id, parent.id)
    assert success is False

def test_search_notes(note_service):
    folder = note_service.create_node("Machine Learning", is_folder=True)
    note1 = note_service.create_node("Linear Regression", is_folder=False, parent_id=folder.id)
    note2 = note_service.create_node("Neural Networks", is_folder=False, parent_id=folder.id)
    
    note_service.update_node_content(note1.id, "Fits a line.")
    note_service.update_node_content(note2.id, "Deep learning topic.")
    
    # Search by title
    results = note_service.search_notes("Linear")
    assert len(results) == 1
    assert results[0].id == note1.id
    
    # Search by content
    results = note_service.search_notes("Deep")
    assert len(results) == 1
    assert results[0].id == note2.id

def test_auto_save_mock_method_exists(note_service):
    success = note_service.update_node_content(999, "Nonexistent note")
    assert success is False

def test_markdown_persistence(note_service):
    note = note_service.create_node("MD Note", is_folder=False)
    md_content = "## Header\n- Bullet 1\n- Bullet 2\n\n```python\nprint('hello')\n```"
    note_service.update_node_content(note.id, md_content)
    
    fetched = note_service.get_note(note.id)
    assert fetched.content == md_content
