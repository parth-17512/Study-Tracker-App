from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    sessions = relationship("StudySession", back_populates="subject", cascade="all, delete-orphan")

class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, default=0)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)
    topic = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    session_type = Column(String(50), nullable=False) # 'stopwatch', 'countdown'
    status = Column(String(50), nullable=False, index=True) # 'completed', 'cancelled', 'interrupted'
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    subject = relationship("Subject", back_populates="sessions")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    goal_type = Column(String(50), nullable=False) # 'daily', 'weekly', 'monthly'
    target_seconds = Column(Integer, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(255), primary_key=True, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

class ActiveTimer(Base):
    __tablename__ = "active_timer"
    
    id = Column(Integer, primary_key=True) # Will only ever have id=1
    mode = Column(String(50), nullable=False) # 'stopwatch', 'countdown'
    state = Column(String(50), nullable=False) # 'RUNNING', 'PAUSED'
    start_time = Column(DateTime(timezone=True), nullable=False)
    target_end_time = Column(DateTime(timezone=True), nullable=True) # for countdown
    target_duration = Column(Integer, nullable=True)
    paused_at = Column(DateTime(timezone=True), nullable=True)
    accumulated_elapsed_seconds = Column(Integer, default=0)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    topic = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

class NoteNode(Base):
    __tablename__ = "note_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("note_nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    is_folder = Column(Boolean, default=False, nullable=False)
    content = Column(Text, nullable=True) # Text content for files
    is_favorite = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    children = relationship("NoteNode", back_populates="parent", cascade="all, delete-orphan")
    parent = relationship("NoteNode", back_populates="children", remote_side=[id])

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="New Chat")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    session = relationship("ChatSession", back_populates="messages")

class UserXPLog(Base):
    __tablename__ = "user_xp_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False) # e.g. +10, -10
    reason = Column(String(255), nullable=False) # e.g. "Completed 1 hour session"
    created_at = Column(DateTime(timezone=True), default=utc_now)

