import csv
import json
import logging
from pathlib import Path
from app.services.base_service import BaseService
from app.repositories.session_repository import SessionRepository

logger = logging.getLogger(__name__)

class DataService(BaseService):
    """Handles data import, export, and deletion."""
    
    def __init__(self, db=None):
        super().__init__(db)
        self.session_repo = SessionRepository()

    def export_csv(self, filepath: str) -> bool:
        """Exports all sessions to a CSV file."""
        try:
            with self.db.get_session() as session:
                sessions = self.session_repo.get_all(session)
                
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'SubjectID', 'StartTime', 'EndTime', 'DurationSeconds', 'SessionType', 'Status', 'Topic', 'Notes'])
                
                for s in sessions:
                    writer.writerow([
                        s.id,
                        s.subject_id,
                        s.start_time.isoformat() if s.start_time else "",
                        s.end_time.isoformat() if s.end_time else "",
                        s.duration_seconds,
                        s.session_type,
                        s.status,
                        s.topic,
                        s.notes
                    ])
            return True
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            return False
            
    def export_json(self, filepath: str) -> bool:
        """Exports all sessions to a JSON file."""
        try:
            with self.db.get_session() as session:
                sessions = self.session_repo.get_all(session)
                
            data = []
            for s in sessions:
                data.append({
                    "id": s.id,
                    "subject_id": s.subject_id,
                    "start_time": s.start_time.isoformat() if s.start_time else None,
                    "end_time": s.end_time.isoformat() if s.end_time else None,
                    "duration_seconds": s.duration_seconds,
                    "session_type": s.session_type,
                    "status": s.status,
                    "topic": s.topic,
                    "notes": s.notes
                })
                
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            return False

    def export_ml_dataset(self, filepath: str) -> bool:
        """Exports a feature-engineered dataset for Machine Learning."""
        try:
            from app.ml.dataset import DatasetGenerator
            with self.db.get_session() as session:
                sessions = self.session_repo.get_all(session)
            
            return DatasetGenerator.export_to_csv(sessions, filepath)
        except Exception as e:
            logger.error(f"Failed to export ML dataset: {e}")
            return False

    def wipe_all_data(self) -> bool:
        """Wipes all data from the database."""
        try:
            with self.db.get_session() as session:
                from app.database.models import StudySession
                session.query(StudySession).delete()
                session.commit()
                logger.warning("All study sessions have been deleted.")
            return True
        except Exception as e:
            logger.error(f"Failed to wipe data: {e}")
            return False
