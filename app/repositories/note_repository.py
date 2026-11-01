from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
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
        return session.query(NoteNode).options(joinedload(NoteNode.parent)).filter(
            NoteNode.is_folder == False,
            or_(
                NoteNode.name.ilike(wildcard),
                NoteNode.content.ilike(wildcard)
            )
        ).all()

    def get_favorites(self, session: Session) -> List[NoteNode]:
        """Fetch all favorite notes."""
        return session.query(NoteNode).options(joinedload(NoteNode.parent)).filter(
            NoteNode.is_favorite == True
        ).all()

    def get_recent_notes(self, session: Session, limit: int = 10) -> List[NoteNode]:
        """Fetch recently updated notes."""
        return (
            session.query(NoteNode)
            .options(joinedload(NoteNode.parent))
            .filter(NoteNode.is_folder == False)
            .order_by(NoteNode.updated_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_date_range(self, session: Session, start_date: datetime, end_date: datetime, filter_by: str = "created_or_updated") -> List[NoteNode]:
        """Fetch notes created or updated within a specific datetime range."""
        from sqlalchemy import or_
        query = session.query(NoteNode).filter(NoteNode.is_folder == False)
        if filter_by == "created":
            query = query.filter(NoteNode.created_at >= start_date, NoteNode.created_at <= end_date)
        elif filter_by == "updated":
            query = query.filter(NoteNode.updated_at >= start_date, NoteNode.updated_at <= end_date)
        else:
            query = query.filter(
                or_(
                    (NoteNode.created_at >= start_date) & (NoteNode.created_at <= end_date),
                    (NoteNode.updated_at >= start_date) & (NoteNode.updated_at <= end_date)
                )
            )
        return query.order_by(NoteNode.created_at.desc()).all()
