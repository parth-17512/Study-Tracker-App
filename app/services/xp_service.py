import logging
from typing import List, Tuple
from sqlalchemy import func
from app.database.database import Database
from app.database.models import UserXPLog, StudySession

logger = logging.getLogger(__name__)

class XPService:
    def __init__(self, db_override: Database = None):
        self.db = db_override or Database()

    def get_total_xp(self) -> int:
        with self.db.get_session() as session:
            total = session.query(func.sum(UserXPLog.amount)).scalar()
            return total or 0

    def add_xp(self, amount: int, reason: str) -> bool:
        if amount == 0:
            return False
            
        with self.db.get_session() as session:
            try:
                log_entry = UserXPLog(amount=amount, reason=reason)
                session.add(log_entry)
                return True
            except Exception as e:
                logger.error(f"Failed to add XP: {e}")
                return False

    def calculate_level(self, total_xp: int) -> Tuple[int, int, int]:
        """
        Returns (current_level, current_level_xp, next_level_xp_requirement)
        Using a simple scaling formula for levels: Level = (XP / 100) + 1
        (Every 100 XP is a level)
        """
        current_level = (total_xp // 100) + 1
        current_level_xp = total_xp % 100
        next_level_req = 100
        return current_level, current_level_xp, next_level_req

    def process_session_completion(self, duration_seconds: int) -> int:
        """
        Called when a study session is completed.
        Awards XP based on duration (+10 XP per hour).
        Returns the awarded XP amount.
        """
        # Calculate full hours. Or maybe scale it proportionally?
        # Let's do 1 XP per 6 minutes (which is 10 XP per 60 mins).
        minutes = duration_seconds // 60
        xp_to_award = minutes // 6
        
        if xp_to_award > 0:
            self.add_xp(xp_to_award, f"Completed a {minutes} minute study session.")
            
        return xp_to_award
