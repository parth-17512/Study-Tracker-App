from typing import List, Optional
from app.database.database import Database
from app.database.models import ChatSession, ChatMessage
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db_override: Database = None):
        self.db = db_override or Database()

    def get_all_sessions(self) -> List[ChatSession]:
        with self.db.get_session() as session:
            sessions = session.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
            session.expunge_all()
            return sessions

    def create_session(self, title: str = "New Chat") -> ChatSession:
        with self.db.get_session() as session:
            new_session = ChatSession(title=title)
            session.add(new_session)
            session.commit()
            session.refresh(new_session)
            session.expunge(new_session)
            return new_session

    def delete_session(self, session_id: int) -> bool:
        with self.db.get_session() as session:
            db_session = session.query(ChatSession).filter(ChatSession.id == session_id).first()
            if db_session:
                session.delete(db_session)
                session.commit()
                return True
            return False

    def rename_session(self, session_id: int, new_title: str) -> bool:
        with self.db.get_session() as session:
            db_session = session.query(ChatSession).filter(ChatSession.id == session_id).first()
            if db_session:
                db_session.title = new_title
                session.commit()
                return True
            return False

    def get_messages(self, session_id: int) -> List[ChatMessage]:
        with self.db.get_session() as session:
            messages = session.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
            session.expunge_all()
            return messages

    def add_message(self, session_id: int, role: str, content: str) -> Optional[ChatMessage]:
        with self.db.get_session() as session:
            # check if session exists
            db_session = session.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not db_session:
                return None
                
            new_msg = ChatMessage(session_id=session_id, role=role, content=content)
            session.add(new_msg)
            db_session.updated_at = new_msg.created_at # touch session
            session.commit()
            session.refresh(new_msg)
            session.expunge(new_msg)
            return new_msg
