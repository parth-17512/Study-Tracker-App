import os
import csv
import json
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, StudySession
from app.services.data_service import DataService
from app.repositories.session_repository import SessionRepository

@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    
    # Add dummy data
    db_session = Session()
    s1 = StudySession(
        topic="Math",
        notes="Calculus homework",
        status="COMPLETED",
        session_type="POMODORO",
        start_time=datetime.now(timezone.utc),
        duration_seconds=3600
    )
    db_session.add(s1)
    db_session.commit()
    db_session.close()
    
    # Create a mock database object
    class MockDB:
        def get_session(self):
            return Session()
            
    return MockDB()

@pytest.fixture
def data_service(memory_db):
    service = DataService(db=memory_db)
    return service

def test_export_csv(data_service, tmp_path):
    csv_file = tmp_path / "export.csv"
    assert data_service.export_csv(str(csv_file)) is True
    
    assert csv_file.exists()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Header + 1 row
        assert len(rows) == 2
        assert rows[0][0] == "ID"
        assert rows[1][7] == "Math" # Topic column
        
def test_export_json(data_service, tmp_path):
    json_file = tmp_path / "export.json"
    assert data_service.export_json(str(json_file)) is True
    
    assert json_file.exists()
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["topic"] == "Math"
        assert data[0]["notes"] == "Calculus homework"

