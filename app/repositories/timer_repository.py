from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import ActiveTimer
from app.repositories.base_repository import BaseRepository

class TimerRepository(BaseRepository[ActiveTimer]):
    def __init__(self):
        super().__init__(ActiveTimer)
        
    def get_active(self, session: Session) -> Optional[ActiveTimer]:
        """Get the single active timer record if it exists (id=1)."""
        return session.query(ActiveTimer).filter(ActiveTimer.id == 1).first()
        
    def save_active(self, session: Session, timer_data: dict) -> ActiveTimer:
        """Create or update the single active timer record."""
        active = self.get_active(session)
        if active:
            # Update existing
            for key, value in timer_data.items():
                setattr(active, key, value)
        else:
            # Create new with id=1
            timer_data['id'] = 1
            active = ActiveTimer(**timer_data)
            session.add(active)
            
        session.flush()
        return active
        
    def clear_active(self, session: Session) -> bool:
        """Clear the active timer state."""
        return self.delete(session, 1)
