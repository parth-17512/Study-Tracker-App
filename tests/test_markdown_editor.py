import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from app.ui.components.markdown_editor import MarkdownEditor

# We need a QApplication instance to test widgets
app = QApplication.instance() or QApplication(sys.argv)

def test_markdown_editor_auto_numbering():
    editor = MarkdownEditor()
    editor.setPlainText("1. First")
    
    # Move to end
    cursor = editor.textCursor()
    cursor.movePosition(cursor.MoveOperation.End)
    editor.setTextCursor(cursor)
    
    # Simulate Enter
    event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key_Return, Qt.NoModifier)
    editor.keyPressEvent(event)
    
    # Simulate typing
    editor.insertPlainText("Second")
    
    # Simulate Enter again
    editor.keyPressEvent(event)
    editor.insertPlainText("Third")
    
    assert editor.toPlainText() == "1. First\n2. Second\n3. Third"
    
def test_markdown_editor_insertion():
    editor = MarkdownEditor()
    editor.setPlainText("1. First\n2. Second\n3. Third")
    
    # Position cursor at end of "First"
    cursor = editor.textCursor()
    cursor.setPosition(8)
    editor.setTextCursor(cursor)
    
    # Simulate Enter
    event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key_Return, Qt.NoModifier)
    editor.keyPressEvent(event)
    
    editor.insertPlainText("New item")
    
    assert editor.toPlainText() == "1. First\n2. New item\n3. Second\n4. Third"

def test_markdown_editor_nested_lists():
    editor = MarkdownEditor()
    editor.setPlainText("1. First\n   1. Nested A\n   2. Nested B\n2. Second")
    
    # Position cursor at end of "Nested A" (index 8 + 1 + 14 = 23)
    cursor = editor.textCursor()
    cursor.setPosition(23)
    editor.setTextCursor(cursor)
    
    event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key_Return, Qt.NoModifier)
    editor.keyPressEvent(event)
    
    editor.insertPlainText("Nested inserted")
    
    expected = "1. First\n   1. Nested A\n   2. Nested inserted\n   3. Nested B\n2. Second"
    assert editor.toPlainText() == expected

def test_markdown_editor_exit_list_on_empty():
    editor = MarkdownEditor()
    editor.setPlainText("1. First")
    
    cursor = editor.textCursor()
    cursor.movePosition(cursor.MoveOperation.End)
    editor.setTextCursor(cursor)
    
    event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key_Return, Qt.NoModifier)
    editor.keyPressEvent(event)
    
    # Now it should be "1. First\n2. "
    # Press enter again on empty list item
    editor.keyPressEvent(event)
    
    # Should exit list, leaving an empty line
    assert editor.toPlainText() == "1. First\n\n"
