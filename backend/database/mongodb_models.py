from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CommentStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    DELETED = "deleted"

class ChatMessageStatus(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"

class Comment(BaseModel):
    id: Optional[str] = None
    user_id: int
    username: str
    role: Optional[str] = None
    title: str
    description: str
    category: str
    status: CommentStatus = CommentStatus.OPEN
    priority: str = "medium"
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    assigned_to: Optional[int] = None
    response: Optional[str] = None
    resolved_by: Optional[int] = None

class ChatMessage(BaseModel):
    id: Optional[str] = None
    user_id: int
    username: str
    role: Optional[str] = None
    message: str
    status: ChatMessageStatus = ChatMessageStatus.ACTIVE
    timestamp: datetime = datetime.now()

class NotificationType(str, Enum):
    NEW_COMMENT = "new_comment"
    NEW_CHAT = "new_chat"
    FAILED_TASK = "failed_task"
    SUCCESSFUL_TASK = "successful_task"
    VERSION_UPDATE = "version_update"
    DOCUMENT_CHANGE = "document_change"

class Notification(BaseModel):
    id: Optional[str] = None
    user_id: Optional[int] = None  # None for global notifications
    type: NotificationType
    title: str
    message: str
    read: bool = False
    timestamp: datetime = datetime.now()
    action_url: Optional[str] = None

class OnlineUser(BaseModel):
    user_id: int
    username: str
    role: str
    last_seen: datetime = datetime.now()