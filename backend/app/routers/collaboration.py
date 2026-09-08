from fastapi import APIRouter, HTTPException, Depends, status, Header, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import hashlib
import json
from models.knowledge_base import User, UserRole, Video, VideoPrivacy, UserSession, Feedback, FeedbackStatus
from app.session_store import users_db, sessions_db, active_sessions, connected_clients

router = APIRouter()

# In-memory storage (in production, use a database)
videos_db = {}
feedback_db = {}

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
    if token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    return active_sessions[token]

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
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class VideoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    privacy: VideoPrivacy = VideoPrivacy.PUBLIC
    tags: List[str] = []

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    privacy: Optional[VideoPrivacy] = None
    tags: Optional[List[str]] = None

class BulkVideoOperation(BaseModel):
    video_ids: List[int]
    operation: str  # "delete", "make_private", "make_public"

class FeedbackCreate(BaseModel):
    title: str
    description: str
    category: str
    priority: str = "medium"

class FeedbackUpdate(BaseModel):
    status: Optional[FeedbackStatus] = None
    assigned_to: Optional[int] = None
    implementation_notes: Optional[str] = None
    version_implemented: Optional[str] = None

# Authentication endpoints
@router.post("/auth/register")
async def register_user(user_data: UserCreate):
    # Check if user already exists
    for user in users_db.values():
        if user.username == user_data.username or user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )

    # Create new user
    user_id = len(users_db) + 1
    hashed_password = hash_password(user_data.password)
    new_user = User(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        created_at=datetime.now(),
        is_active=True
    )

    users_db[user_id] = new_user

    return {"message": "User created successfully", "user_id": user_id}

@router.post("/auth/login")
async def login_user(credentials: UserLogin):
    # Find user
    user = None
    for u in users_db.values():
        if u.username == credentials.username:
            user = u
            break

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )

    # Create session
    session_token = create_session_token()
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=datetime.now() + timedelta(hours=24),
        created_at=datetime.now()
    )

    sessions_db[session_token] = session
    active_sessions[session_token] = user

    return {
        "message": "Login successful",
        "session_token": session_token,
        "user": user,
        "expires_at": session.expires_at
    }

@router.post("/auth/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    # Remove from active sessions
    for token, user in active_sessions.items():
        if user.id == current_user.id:
            del active_sessions[token]
            break

    return {"message": "Logout successful"}

@router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# User management endpoints (Admin only)
@router.get("/users", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def get_all_users():
    return list(users_db.values())

@router.get("/users/{user_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return users_db[user_id]

@router.put("/users/{user_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def update_user(user_id: int, user_update: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user = users_db[user_id]
    update_data = user_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}", dependencies=[Depends(require_role([UserRole.ADMIN]))])
async def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Soft delete - mark as inactive
    users_db[user_id].is_active = False

    # Remove user sessions
    for token, user in active_sessions.items():
        if user.id == user_id:
            del active_sessions[token]

    return {"message": "User deleted successfully"}

# Video management endpoints
@router.post("/videos")
async def create_video(
    video_data: VideoCreate,
    current_user: User = Depends(get_current_user)
):
    video_id = len(videos_db) + 1
    new_video = Video(
        id=video_id,
        title=video_data.title,
        description=video_data.description,
        file_path="",  # This would be set when file is uploaded
        owner_id=current_user.id,
        privacy=video_data.privacy,
        tags=video_data.tags,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    videos_db[video_id] = new_video
    return {"message": "Video created successfully", "video_id": video_id}

@router.get("/videos")
async def get_videos(
    current_user: User = Depends(get_current_user),
    privacy_filter: Optional[str] = None
):
    videos = []

    for video in videos_db.values():
        if video.is_deleted:
            continue

        # Check privacy permissions
        if video.privacy == VideoPrivacy.PRIVATE and video.owner_id != current_user.id:
            # Only owner can see private videos
            if current_user.role not in [UserRole.ADMIN]:
                continue

        if video.privacy == VideoPrivacy.UNLISTED:
            # Only owner and admins can see unlisted videos
            if current_user.role not in [UserRole.ADMIN] and video.owner_id != current_user.id:
                continue

        # Marketing/Designer role restrictions
        if current_user.role == UserRole.MARKETING_DESIGNER:
            # They can only view, not see sensitive user details
            video_info = {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "privacy": video.privacy,
                "tags": video.tags,
                "created_at": video.created_at,
                "view_count": video.view_count,
                "owner_username": users_db.get(video.owner_id, {}).username if video.owner_id in users_db else "Unknown"
            }
        else:
            video_info = video.dict()

        videos.append(video_info)

    return videos

@router.get("/videos/{video_id}")
async def get_video(
    video_id: int,
    current_user: User = Depends(get_current_user)
):
    if video_id not in videos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    video = videos_db[video_id]

    if video.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    # Check privacy permissions
    if video.privacy == VideoPrivacy.PRIVATE and video.owner_id != current_user.id:
        if current_user.role not in [UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    if video.privacy == VideoPrivacy.UNLISTED:
        if current_user.role not in [UserRole.ADMIN] and video.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    return video

@router.put("/videos/{video_id}")
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    current_user: User = Depends(get_current_user)
):
    if video_id not in videos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    video = videos_db[video_id]

    # Check permissions
    if video.owner_id != current_user.id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Marketing/Designer cannot edit videos
    if current_user.role == UserRole.MARKETING_DESIGNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Marketing/Designer role cannot edit videos"
        )

    update_data = video_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(video, field, value)

    video.updated_at = datetime.now()

    return {"message": "Video updated successfully"}

@router.delete("/videos/{video_id}")
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user)
):
    if video_id not in videos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    video = videos_db[video_id]

    # Check permissions
    if video.owner_id != current_user.id and current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Marketing/Designer cannot delete videos
    if current_user.role == UserRole.MARKETING_DESIGNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Marketing/Designer role cannot delete videos"
        )

    # Soft delete
    video.is_deleted = True
    video.updated_at = datetime.now()

    return {"message": "Video deleted successfully"}

@router.post("/videos/bulk")
async def bulk_video_operation(
    operation_data: BulkVideoOperation,
    current_user: User = Depends(get_current_user)
):
    # Only admins can perform bulk operations
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform bulk operations"
        )

    # Marketing/Designer cannot be affected by bulk operations that delete
    if operation_data.operation == "delete":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bulk delete operations are not allowed"
        )

    affected_videos = []

    for video_id in operation_data.video_ids:
        if video_id in videos_db:
            video = videos_db[video_id]

            if operation_data.operation == "make_private":
                video.privacy = VideoPrivacy.PRIVATE
            elif operation_data.operation == "make_public":
                video.privacy = VideoPrivacy.PUBLIC

            video.updated_at = datetime.now()
            affected_videos.append(video_id)

    return {
        "message": f"Bulk operation '{operation_data.operation}' completed",
        "affected_videos": affected_videos
    }

# Analytics endpoints (Admin and AI Engineer can see all, Marketing/Designer can see limited)
@router.get("/analytics/users")
async def get_user_analytics(current_user: User = Depends(get_current_user)):
    # AI Engineer cannot see logged in users and vital details
    if current_user.role == UserRole.AI_ENGINEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI Engineers cannot access user analytics"
        )

    if current_user.role not in [UserRole.ADMIN, UserRole.MARKETING_DESIGNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    total_users = len([u for u in users_db.values() if u.is_active])
    users_by_role = {}
    for user in users_db.values():
        if user.is_active:
            role = user.role.value
            users_by_role[role] = users_by_role.get(role, 0) + 1

    return {
        "total_users": total_users,
        "users_by_role": users_by_role,
        "active_sessions": len(active_sessions)
    }

@router.get("/analytics/videos")
async def get_video_analytics(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.AI_ENGINEER, UserRole.MARKETING_DESIGNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    total_videos = len([v for v in videos_db.values() if not v.is_deleted])
    videos_by_privacy = {}
    for video in videos_db.values():
        if not video.is_deleted:
            privacy = video.privacy.value
            videos_by_privacy[privacy] = videos_by_privacy.get(privacy, 0) + 1

    # Marketing/Designer gets limited analytics
    if current_user.role == UserRole.MARKETING_DESIGNER:
        return {
            "total_videos": total_videos,
            "videos_by_privacy": videos_by_privacy
        }

    # Admin and AI Engineer get full analytics
    videos_by_owner = {}
    for video in videos_db.values():
        if not video.is_deleted:
            owner_id = video.owner_id
            videos_by_owner[owner_id] = videos_by_owner.get(owner_id, 0) + 1

    return {
        "total_videos": total_videos,
        "videos_by_privacy": videos_by_privacy,
        "videos_by_owner": videos_by_owner,
        "total_view_count": sum(v.view_count for v in videos_db.values() if not v.is_deleted)
    }

# Feedback/Improvement System endpoints
@router.post("/feedback")
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user)
):
    feedback_id = len(feedback_db) + 1
    new_feedback = Feedback(
        id=feedback_id,
        user_id=current_user.id,
        title=feedback_data.title,
        description=feedback_data.description,
        category=feedback_data.category,
        priority=feedback_data.priority,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    feedback_db[feedback_id] = new_feedback
    return {"message": "Feedback submitted successfully", "feedback_id": feedback_id}

@router.get("/feedback")
async def get_all_feedback(current_user: User = Depends(get_current_user)):
    # Only admins and AI engineers can see all feedback
    if current_user.role not in [UserRole.ADMIN, UserRole.AI_ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    feedback_list = []
    for feedback in feedback_db.values():
        feedback_info = feedback.dict()
        feedback_info["submitted_by"] = users_db.get(feedback.user_id, {}).username if feedback.user_id in users_db else "Unknown"
        feedback_info["assigned_to_name"] = users_db.get(feedback.assigned_to, {}).username if feedback.assigned_to and feedback.assigned_to in users_db else None
        feedback_list.append(feedback_info)

    return feedback_list

@router.get("/feedback/my")
async def get_my_feedback(current_user: User = Depends(get_current_user)):
    # Users can see their own feedback
    user_feedback = []
    for feedback in feedback_db.values():
        if feedback.user_id == current_user.id:
            user_feedback.append(feedback)

    return user_feedback

@router.get("/feedback/{feedback_id}")
async def get_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user)
):
    if feedback_id not in feedback_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )

    feedback = feedback_db[feedback_id]

    # Users can only see their own feedback, unless they're admin/engineer
    if feedback.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.AI_ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    feedback_info = feedback.dict()
    feedback_info["submitted_by"] = users_db.get(feedback.user_id, {}).username if feedback.user_id in users_db else "Unknown"
    feedback_info["assigned_to_name"] = users_db.get(feedback.assigned_to, {}).username if feedback.assigned_to and feedback.assigned_to in users_db else None

    return feedback_info

@router.put("/feedback/{feedback_id}")
async def update_feedback(
    feedback_id: int,
    feedback_update: FeedbackUpdate,
    current_user: User = Depends(get_current_user)
):
    if feedback_id not in feedback_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )

    feedback = feedback_db[feedback_id]

    # Only admins and AI engineers can update feedback status
    if current_user.role not in [UserRole.ADMIN, UserRole.AI_ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and AI engineers can update feedback"
        )

    update_data = feedback_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)

    feedback.updated_at = datetime.now()

    return {"message": "Feedback updated successfully"}

@router.delete("/feedback/{feedback_id}")
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user)
):
    if feedback_id not in feedback_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )

    feedback = feedback_db[feedback_id]

    # Only admins can delete feedback, or users can delete their own
    if current_user.role != UserRole.ADMIN and feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    del feedback_db[feedback_id]

    return {"message": "Feedback deleted successfully"}

@router.get("/feedback/stats")
async def get_feedback_stats(current_user: User = Depends(get_current_user)):
    # Only admins and AI engineers can see feedback statistics
    if current_user.role not in [UserRole.ADMIN, UserRole.AI_ENGINEER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    total_feedback = len(feedback_db)
    status_counts = {}
    category_counts = {}
    priority_counts = {}

    for feedback in feedback_db.values():
        # Count by status
        status = feedback.status.value
        status_counts[status] = status_counts.get(status, 0) + 1

        # Count by category
        category = feedback.category
        category_counts[category] = category_counts.get(category, 0) + 1

        # Count by priority
        priority = feedback.priority
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    return {
        "total_feedback": total_feedback,
        "by_status": status_counts,
        "by_category": category_counts,
        "by_priority": priority_counts
    }

# Initialize with default users for each role
@router.on_event("startup")
async def create_default_users():
    if not users_db:
        # Admin user
        admin_user = User(
            id=1,
            username="admin",
            email="admin@viralish.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
            created_at=datetime.now(),
            is_active=True
        )
        users_db[1] = admin_user

        # AI Engineer user
        ai_engineer_user = User(
            id=2,
            username="ai_engineer",
            email="ai.engineer@viralish.com",
            hashed_password=hash_password("ai_engineer123"),
            role=UserRole.AI_ENGINEER,
            created_at=datetime.now(),
            is_active=True
        )
        users_db[2] = ai_engineer_user

        # Marketing/Designer user
        marketing_user = User(
            id=3,
            username="marketing_designer",
            email="marketing@viralish.com",
            hashed_password=hash_password("marketing123"),
            role=UserRole.MARKETING_DESIGNER,
            created_at=datetime.now(),
            is_active=True
        )
        users_db[3] = marketing_user

        print("Default users created:")
        print("Admin: admin/admin123")
        print("AI Engineer: ai_engineer/ai_engineer123")
        print("Marketing/Designer: marketing_designer/marketing123")

# WebSocket endpoint for presence
@router.websocket("/ws/presence")
async def websocket_presence_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Validate token first before accepting connection
    if not token or token not in active_sessions:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    current_user = active_sessions[token]
    client_id = id(websocket)
    connected_clients[client_id] = websocket

    try:
        # Accept the connection after validation
        await websocket.accept()

        # Send current online users with their tokens
        online_sessions = list(active_sessions.items())  # list of (token, user)
        await websocket.send_text(json.dumps({
            "type": "presence_update",
            "users": [{"id": u.id, "username": u.username, "token": token} for token, u in online_sessions]
        }))

        while True:
            data = await websocket.receive_text()
            # For now, just echo back or handle simple messages
            message_data = json.loads(data)
            if message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        if client_id in connected_clients:
            del connected_clients[client_id]
    except Exception as e:
        print(f"An error occurred: {e}")
        if client_id in connected_clients:
            del connected_clients[client_id]
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)