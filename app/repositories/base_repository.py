from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from app.database.database import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, session: Session, id: int) -> Optional[T]:
        return session.query(self.model).filter(self.model.id == id).first()

    def get_all(self, session: Session) -> List[T]:
        return session.query(self.model).all()

    def create(self, session: Session, obj_in: dict) -> T:
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        session.flush() # Flush to get the ID, commit happens in the service layer context manager
        return db_obj

    def update(self, session: Session, db_obj: T, obj_in: dict) -> T:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        session.flush()
        return db_obj

    def delete(self, session: Session, id: int) -> bool:
        obj = session.get(self.model, id)
        if obj:
            session.delete(obj)
            session.flush()
            return True
        return False
