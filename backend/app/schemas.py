"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# System Settings
class SystemSettingsBase(BaseModel):
    plex_url: Optional[str] = None
    plex_token: Optional[str] = None
    radarr_url: Optional[str] = None
    radarr_api_key: Optional[str] = None
    sonarr_url: Optional[str] = None
    sonarr_api_key: Optional[str] = None
    language: str = "en"
    theme: str = "light"
    auth_enabled: bool = False
    auth_password: Optional[str] = None


class SystemSettingsResponse(BaseModel):
    id: int
    plex_url: Optional[str]
    radarr_url: Optional[str]
    sonarr_url: Optional[str]
    language: str
    theme: str
    auth_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestConnectionRequest(BaseModel):
    url: Optional[str] = None
    token_or_key: Optional[str] = None
    service_type: Optional[str] = None  # "plex", "radarr", "sonarr" (optional, not used anymore)


class TestConnectionResponse(BaseModel):
    success: bool
    message: str


# Libraries
class LibraryResponse(BaseModel):
    id: int
    plex_id: str
    title: str
    library_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Rules
class Condition(BaseModel):
    field: str
    operator: str
    value: Any


class Action(BaseModel):
    type: str
    delay_days: Optional[int] = None
    collection_name: Optional[str] = None
    title_format: Optional[str] = None


class RuleCreate(BaseModel):
    library_id: int
    name: str
    enabled: bool = True
    dry_run: bool = True
    logic: str = "AND"
    conditions: List[Condition]
    immediate_actions: List[Action]
    delayed_actions: List[Action]


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None
    dry_run: Optional[bool] = None
    logic: Optional[str] = None
    conditions: Optional[List[Condition]] = None
    immediate_actions: Optional[List[Action]] = None
    delayed_actions: Optional[List[Action]] = None


class RuleResponse(BaseModel):
    id: int
    library_id: int
    name: str
    enabled: bool
    dry_run: bool
    logic: str
    conditions: List[Dict[str, Any]]
    immediate_actions: List[Dict[str, Any]]
    delayed_actions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    library: LibraryResponse

    class Config:
        from_attributes = True


# Candidates
class CandidateResponse(BaseModel):
    id: int
    rule_id: int
    plex_key: str
    item_type: str
    item_title: str
    season_number: Optional[int] = None
    show_title: Optional[str] = None  # For TV shows
    episode_count: Optional[int] = None  # Total episodes in season
    last_watched_episode_title: Optional[str] = None
    last_watched_episode_number: Optional[int] = None
    last_watched_episode_date: Optional[datetime] = None
    reason: str
    actions: List[Dict[str, Any]]
    scheduled_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    cancelled: bool
    rule: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Action Logs
class ActionLogResponse(BaseModel):
    id: int
    rule_id: Optional[int]
    plex_key: str
    item_type: str
    item_title: str
    action_type: str
    action_status: str
    details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Tasks
class ScanResponse(BaseModel):
    success: bool
    message: str
    candidates_count: int

