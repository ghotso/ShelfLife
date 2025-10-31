"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    plex_url = Column(String, nullable=True)
    plex_token_encrypted = Column(Text, nullable=True)
    radarr_url = Column(String, nullable=True)
    radarr_api_key_encrypted = Column(Text, nullable=True)
    sonarr_url = Column(String, nullable=True)
    sonarr_api_key_encrypted = Column(Text, nullable=True)
    language = Column(String, default="en")
    theme = Column(String, default="light")
    auth_enabled = Column(Boolean, default=False)
    auth_password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Library(Base):
    __tablename__ = "libraries"
    
    id = Column(Integer, primary_key=True, index=True)
    plex_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    library_type = Column(String, nullable=False)  # "movie" or "show"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    rules = relationship("Rule", back_populates="library", cascade="all, delete-orphan")


class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey("libraries.id"), nullable=False)
    name = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    dry_run = Column(Boolean, default=True)
    logic = Column(String, default="AND")  # "AND" or "OR"
    conditions_json = Column(Text, nullable=False)  # JSON string
    actions_json = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    library = relationship("Library", back_populates="rules")
    candidates = relationship("Candidate", back_populates="rule", cascade="all, delete-orphan")


class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    plex_key = Column(String, nullable=False)
    item_type = Column(String, nullable=False)  # "movie" or "season"
    item_title = Column(String, nullable=False)
    season_number = Column(Integer, nullable=True)  # For TV shows
    show_title = Column(String, nullable=True)  # For TV shows - the show name
    episode_count = Column(Integer, nullable=True)  # Total number of episodes in season
    last_watched_episode_title = Column(String, nullable=True)  # Title of last watched episode
    last_watched_episode_number = Column(Integer, nullable=True)  # Episode number
    last_watched_episode_date = Column(DateTime, nullable=True)  # When episode was watched
    reason = Column(Text, nullable=False)  # Why this item was marked
    actions_json = Column(Text, nullable=False)  # Actions to be taken
    scheduled_date = Column(DateTime, nullable=True)  # When action should execute
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled = Column(Boolean, default=False)  # Cancelled due to watched again
    
    rule = relationship("Rule", back_populates="candidates")


class ActionLog(Base):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    plex_key = Column(String, nullable=False)
    item_type = Column(String, nullable=False)
    item_title = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    action_status = Column(String, nullable=False)  # "success", "failed", "dry_run"
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

