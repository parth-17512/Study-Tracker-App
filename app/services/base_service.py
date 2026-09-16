import logging
from app.database.database import Database

class BaseService:
    def __init__(self, db: Database = None):
        from app.database.database import db as global_db
        self.db = db or global_db
        self.logger = logging.getLogger(self.__class__.__name__)
