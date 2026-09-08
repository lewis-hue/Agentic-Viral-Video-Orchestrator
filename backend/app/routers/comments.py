from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import hashlib
from models.knowledge_base import User, UserRole
from database.mongodb_models import Comment, CommentStatus
from database.mongodb import get_database
from app.session_store import users_db, sessions_db, active_sessions
from app.websocket_manager import broadcast_to_clients
import asyncio
import json

router = APIRouter()

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_session_token() -> str:
    return secrets.token_urlsafe(32)

def get_current_user(authorization: str = Header(...)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    token = authorization.replace("Bearer ", "")

    # First check active sessions for performance
    if token in active_sessions:
        return active_sessions[token]

    # If not in active sessions, check sessions_db and validate expiration
    if token in sessions_db:
        session = sessions_db[token]
        if datetime.now() > session.expires_at:
            # Session expired, remove it
            del sessions_db[token]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired"
            )

        # Session is valid, restore to active_sessions
        user = users_db.get(session.user_id)
        if user and user.is_active:
            active_sessions[token] = user
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session"
    )

def require_role(allowed_roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    return role_checker

# Request/Response models
class CommentCreate(BaseModel):
    title: str
    description: str
    category: str
    priority: str = "medium"

class CommentUpdate(BaseModel):
    status: Optional[CommentStatus] = None
    assigned_to: Optional[int] = None
    response: Optional[str] = None


# Endpoints
@router.post("/")
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user)
):
    db = await get_database()
    comment = Comment(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role.value,
        title=comment_data.title,
        description=comment_data.description,
        category=comment_data.category,
        priority=comment_data.priority
    )
    result = await db.comments.insert_one(comment.dict())
    comment.id = str(result.inserted_id)

    # Add notification for new comment
    notification = {
        "type": "new_comment",
        "title": "New Comment",
        "message": f"{current_user.username} submitted a new comment: {comment.title}",
        "timestamp": datetime.now(),
        "action_url": "#comments"
    }
    await db.notifications.insert_one(notification)

    # Broadcast to all connected clients
    await broadcast_to_clients({
        "type": "new_comment",
        "comment": {
            "id": str(result.inserted_id),
            "user_id": current_user.id,
            "username": current_user.username,
            "role": current_user.role.value,
            "title": comment.title,
            "description": comment.description,
            "category": comment.category,
            "priority": comment.priority,
            "status": comment.status.value,
            "created_at": comment.created_at.isoformat()
        }
    })

    # Return the comment from DB with ObjectId converted
    inserted_comment = await db.comments.find_one({"_id": result.inserted_id})
    return {**inserted_comment, 'id': str(inserted_comment['_id']), '_id': str(inserted_comment['_id'])}

@router.get("/")
async def get_all_comments(current_user: User = Depends(get_current_user)):
    # Only admins and AI engineers can see all comments
    if current_user.role not in [UserRole.ADMIN, UserRole.AI_ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    db = await get_database()
    comments = await db.comments.find({"status": {"$ne": CommentStatus.DELETED}}).to_list(length=None)
    # Convert ObjectId to str for JSON serialization
    return [{**c, 'id': str(c['_id']), '_id': str(c['_id'])} for c in comments]

@router.get("/my")
async def get_my_comments(current_user: User = Depends(get_current_user)):
    # Users can see their own comments
    db = await get_database()
    comments = await db.comments.find({"user_id": current_user.id, "status": {"$ne": CommentStatus.DELETED}}).to_list(length=None)
    # Convert ObjectId to str for JSON serialization
    return [{**c, 'id': str(c['_id']), '_id': str(c['_id'])} for c in comments]

@router.get("/{comment_id}")
async def get_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    db = await get_database()
    comment = await db.comments.find_one({"_id": comment_id})
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Users can only see their own comments, unless they're admin/engineer
    if comment["user_id"] != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.AI_ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Convert ObjectId to str for JSON serialization
    return {**comment, 'id': str(comment['_id']), '_id': str(comment['_id'])}

@router.put("/{comment_id}")
async def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_user)
):
    db = await get_database()
    comment = await db.comments.find_one({"_id": comment_id})
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Only admins and AI engineers can update comments
    if current_user.role not in [UserRole.ADMIN, UserRole.AI_ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and AI engineers can update comments"
        )

    update_data = comment_update.dict(exclude_unset=True)
    if "status" in update_data and update_data["status"] == CommentStatus.RESOLVED:
        update_data["resolved_by"] = current_user.id
    update_data["updated_at"] = datetime.now()

    await db.comments.update_one({"_id": comment_id}, {"$set": update_data})
    updated_comment = await db.comments.find_one({"_id": comment_id})
    # Convert ObjectId to str for JSON serialization
    return {**updated_comment, 'id': str(updated_comment['_id']), '_id': str(updated_comment['_id'])}

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    db = await get_database()
    comment = await db.comments.find_one({"_id": comment_id})
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Only admins can delete comments, or users can delete their own
    if current_user.role != UserRole.ADMIN and comment["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Soft delete: set status to DELETED
    await db.comments.update_one({"_id": comment_id}, {"$set": {"status": CommentStatus.DELETED}})

    return {"message": "Comment deleted successfully"}