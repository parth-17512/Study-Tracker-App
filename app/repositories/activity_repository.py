from datetime import datetime
from typing import Optional

from app.database.models import ActivityBlock


class ActivityRepository:
    def create(self, session, payload):
        block = ActivityBlock(**payload)
        session.add(block)
        session.flush()
        return block

    def get_by_id(self, session, block_id: int) -> Optional[ActivityBlock]:
        return session.query(ActivityBlock).filter(ActivityBlock.id == block_id).first()

    def get_by_date_range(self, session, start_time: datetime, end_time: datetime):
        return session.query(ActivityBlock).filter(
            ActivityBlock.start_time < end_time,
            ActivityBlock.end_time > start_time,
        ).order_by(ActivityBlock.start_time.asc()).all()

    def update(self, block, payload):
        for field, value in payload.items():
            setattr(block, field, value)
        return block

    def delete(self, session, block_id: int) -> bool:
        block = self.get_by_id(session, block_id)
        if block is None:
            return False
        session.delete(block)
        return True
