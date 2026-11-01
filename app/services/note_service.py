from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timezone
from app.database.database import Database
from app.database.models import NoteNode
from app.services.rag_service import RAGService
from app.utils.time_utils import to_local_time

class NoteService:
    def __init__(self, db_override: Database = None):
        self.db = db_override or Database()
        from app.repositories.note_repository import NoteRepository
        self.repository = NoteRepository()
        self.rag = RAGService()

    def get_all_nodes(self) -> List[NoteNode]:
        """Get all nodes as a flat list. Useful for building a tree in-memory."""
        with self.db.get_session() as session:
            nodes = self.repository.get_all(session)
            session.expunge_all()
            return nodes

    def create_node(self, name: str, is_folder: bool, parent_id: Optional[int] = None) -> NoteNode:
        with self.db.get_session() as session:
            node_data = {
                "name": name,
                "is_folder": is_folder,
                "parent_id": parent_id,
                "content": "" if not is_folder else None
            }
            node = self.repository.create(session, node_data)
            session.commit()
            session.refresh(node)
            session.expunge(node)
            return node

    def update_node_content(self, node_id: int, content: str) -> bool:
        with self.db.get_session() as session:
            node = self.repository.get(session, node_id)
            if not node or node.is_folder:
                return False
            self.repository.update(session, node, {"content": content})
            session.commit()
            
            # Sync to RAG
            self.rag.ingest_note(node.id, node.name, content)
            
            return True

    def rename_node(self, node_id: int, new_name: str) -> bool:
        with self.db.get_session() as session:
            node = self.repository.get(session, node_id)
            if not node:
                return False
            self.repository.update(session, node, {"name": new_name})
            session.commit()
            return True

    def move_node(self, node_id: int, new_parent_id: Optional[int]) -> bool:
        """Move a node to a new parent, checking for circular references."""
        with self.db.get_session() as session:
            node = self.repository.get(session, node_id)
            if not node:
                return False
            
            if new_parent_id is not None:
                if new_parent_id == node_id:
                    return False # Cannot move into itself
                    
                # Check for circular reference
                curr = self.repository.get(session, new_parent_id)
                while curr is not None:
                    if curr.id == node_id:
                        return False # Cannot move into a descendant
                    if curr.parent_id is None:
                        break
                    curr = self.repository.get(session, curr.parent_id)
                    
            self.repository.update(session, node, {"parent_id": new_parent_id})
            session.commit()
            return True

    def delete_node(self, node_id: int) -> bool:
        with self.db.get_session() as session:
            success = self.repository.delete(session, node_id)
            session.commit()
            if success:
                self.rag.remove_note(node_id)
            return success

    def toggle_favorite(self, node_id: int, is_favorite: bool) -> bool:
        with self.db.get_session() as session:
            node = self.repository.get(session, node_id)
            if not node:
                return False
            self.repository.update(session, node, {"is_favorite": is_favorite})
            session.commit()
            return True

    # --- AI Integration Methods (Phase requirements) ---
    
    def get_note(self, node_id: int) -> Optional[NoteNode]:
        with self.db.get_session() as session:
            node = self.repository.get(session, node_id)
            if node:
                session.expunge(node)
            return node

    def search_notes(self, query: str) -> List[NoteNode]:
        with self.db.get_session() as session:
            nodes = self.repository.search_notes(session, query)
            session.expunge_all()
            return nodes

    def get_notes_by_folder(self, folder_id: int) -> List[NoteNode]:
        with self.db.get_session() as session:
            nodes = session.query(NoteNode).filter(NoteNode.parent_id == folder_id).all()
            session.expunge_all()
            return nodes

    def get_recent_notes(self, limit: int = 10) -> List[NoteNode]:
        with self.db.get_session() as session:
            nodes = self.repository.get_recent_notes(session, limit)
            session.expunge_all()
            return nodes

    def get_favorite_notes(self) -> List[NoteNode]:
        with self.db.get_session() as session:
            nodes = self.repository.get_favorites(session)
            session.expunge_all()
            return nodes

    def _resolve_tz(self, tz):
        if tz is not None:
            return tz
        return datetime.now().astimezone().tzinfo

    def _parse_date(self, d: Union[str, date, datetime]) -> date:
        if isinstance(d, datetime):
            return d.date()
        if isinstance(d, date):
            return d
        if isinstance(d, str):
            # Try YYYY-MM-DD
            try:
                return datetime.strptime(d.strip()[:10], "%Y-%m-%d").date()
            except Exception:
                pass
        return datetime.now().date()

    def get_notes_by_date(self, target_date: Union[str, date, datetime], tz=None, filter_by: str = "created_or_updated") -> List[Dict[str, Any]]:
        """
        Retrieves notes created or updated on a target date, respecting local timezone.
        Returns serialized dicts with folder metadata.
        """
        d = self._parse_date(target_date)
        return self.get_notes_by_date_range(d, d, tz=tz, filter_by=filter_by)

    def get_notes_by_date_range(self, start_date: Union[str, date, datetime], end_date: Union[str, date, datetime], tz=None, filter_by: str = "created_or_updated") -> List[Dict[str, Any]]:
        """
        Retrieves notes created or updated between start_date and end_date (inclusive), respecting local timezone.
        """
        s_date = self._parse_date(start_date)
        e_date = self._parse_date(end_date)

        target_tz = self._resolve_tz(tz)

        start_local = datetime(s_date.year, s_date.month, s_date.day, 0, 0, 0, tzinfo=target_tz)
        end_local = datetime(e_date.year, e_date.month, e_date.day, 23, 59, 59, 999999, tzinfo=target_tz)

        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)

        with self.db.get_session() as session:
            nodes = self.repository.get_by_date_range(session, start_utc, end_utc, filter_by=filter_by)
            results = []
            for node in nodes:
                folder_name = node.parent.name if node.parent else "Root"
                created_local = to_local_time(node.created_at, tz=target_tz)
                updated_local = to_local_time(node.updated_at, tz=target_tz)
                results.append({
                    "id": node.id,
                    "name": node.name,
                    "content": node.content or "",
                    "folder": folder_name,
                    "is_favorite": node.is_favorite,
                    "created_at": created_local.isoformat() if created_local else None,
                    "updated_at": updated_local.isoformat() if updated_local else None,
                    "date": created_local.strftime("%Y-%m-%d") if created_local else None
                })
            return results
