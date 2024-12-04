# core/db.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Date
from .db import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    pincode = Column(String, nullable=True)

    cases = relationship('Case', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Case(Base):
    __tablename__ = 'cases'

    case_id = Column(String, primary_key=True, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship('User', back_populates='cases')
    statements = relationship('StatementInfo', back_populates='case', cascade="all, delete-orphan")
    entities = relationship('Entity', back_populates='case', cascade="all, delete-orphan")
    merged_groups = relationship('MergedGroup', back_populates='case', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Case(case_id='{self.case_id}', title='{self.title}', user_id={self.user_id})>"


class StatementInfo(Base):
    __tablename__ = 'statements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey('cases.case_id'), nullable=False)
    account_name = Column(String, nullable=False)
    account_number = Column(String(50), nullable=False)
    ifsc_code = Column(String(50), nullable=False)
    bank_name = Column(String, nullable=False)
    local_filename = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    case = relationship('Case', back_populates='statements')

    def __repr__(self):
        return f"<Statement(id={self.id}, case_id='{self.case_id}')>"
    

class Entity(Base):
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey('cases.case_id'), nullable=False)
    name = Column(String, nullable=False)
    merged_group_id = Column(Integer, ForeignKey('merged_groups.id'), nullable=True)
    role = Column(String, nullable=True)  # E.g., "Plaintiff", "Defendant", "Witness"

    case = relationship('Case', back_populates='entities')
    merged_group = relationship('MergedGroup', back_populates='entities')

    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}', case_id='{self.case_id}')>"
    

class MergedGroup(Base):
    __tablename__ = 'merged_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    merged_group_name = Column(String, nullable=False)
    case_id = Column(String, ForeignKey('cases.case_id'), nullable=False)

    entities = relationship('Entity', back_populates='merged_group', cascade="all, delete-orphan")
    case = relationship('Case', back_populates='merged_groups')

    def __repr__(self):
        return f"<MergedGroup(id={self.id}, case_id='{self.case_id}')>"

