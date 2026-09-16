from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import NoteNode
from app.repositories.base_repository import BaseRepository

class NoteRepository(BaseRepository[NoteNode]):
    def __init__(self):
        super().__init__(NoteNode)
        
    def get_root_nodes(self, session: Session) -> List[NoteNode]:
        """Fetch nodes that have no parent."""
        return session.query(NoteNode).filter(NoteNode.parent_id == None).all()
        
    def search_notes(self, session: Session, query: str) -> List[NoteNode]:
        """Search notes by title or content."""
        from sqlalchemy import or_
        wildcard = f"%{query}%"
        return session.query(NoteNode).filter(
            NoteNode.is_folder == False,
            or_(
                NoteNode.name.ilike(wildcard),
                NoteNode.content.ilike(wildcard)
            )
        ).all()

    def get_favorites(self, session: Session) -> List[NoteNode]:
        """Fetch all favorite notes."""
        return session.query(NoteNode).filter(NoteNode.is_favorite == True).all()

    def get_recent_notes(self, session: Session, limit: int = 10) -> List[NoteNode]:
        """Fetch recently updated notes."""
        return session.query(NoteNode).filter(NoteNode.is_folder == False).order_by(NoteNode.updated_at.desc()).limit(limit).all()
