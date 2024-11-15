# core/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

class Database:
    _instance = None
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')
    DATABASE_URL = f"sqlite:///{DB_PATH}"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._initialize()
        return cls._instance

    @classmethod
    def _initialize(cls):
        # Initialize the engine and session
        cls.engine = create_engine(cls.DATABASE_URL, echo=False)
        cls.Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=cls.engine))
        cls.Base = declarative_base()

    @classmethod
    def get_session(cls):
        """Provides a new session instance."""
        return cls.Session()

# Base class for models, to be used in model definitions
Base = Database().Base
