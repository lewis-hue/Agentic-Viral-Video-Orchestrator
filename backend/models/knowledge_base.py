from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    AI_ENGINEER = "ai_engineer"
    MARKETING_DESIGNER = "marketing_designer"

class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    role: UserRole
    created_at: datetime
    is_active: bool = True
    profile_picture: Optional[str] = None

class VideoPrivacy(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"

class Video(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    file_path: str
    thumbnail_path: Optional[str] = None
    owner_id: int
    privacy: VideoPrivacy = VideoPrivacy.PUBLIC
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    view_count: int = 0
    is_deleted: bool = False

class ViralTip(BaseModel):
    id: int
    category: str  # e.g., "Hook", "Storytelling", "Visuals", "Hashtags"
    tip: str
    description: str
    example: Optional[str] = None

class KnowledgeBase(BaseModel):
    tips: List[ViralTip]

class UserSession(BaseModel):
    user_id: int
    session_token: str
    expires_at: datetime
    created_at: datetime

class CommentStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Comment(BaseModel):
    id: int
    user_id: int
    username: str
    title: str
    description: str
    category: str  # "feature", "bug", "improvement", "ui", "performance"
    status: CommentStatus = CommentStatus.OPEN
    priority: str = "medium"  # "low", "medium", "high", "critical"
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[int] = None  # User ID of assigned team member
    response: Optional[str] = None
    resolved_by: Optional[int] = None

class ChatMessage(BaseModel):
    id: int
    user_id: int
    username: str
    message: str
    timestamp: datetime

class FeedbackStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Feedback(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    category: str
    priority: str = "medium"
    status: FeedbackStatus = FeedbackStatus.OPEN
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[int] = None
    implementation_notes: Optional[str] = None
    version_implemented: Optional[str] = None