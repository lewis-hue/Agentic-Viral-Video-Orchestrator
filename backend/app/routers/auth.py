from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import hashlib
from models.knowledge_base import User, UserRole, UserSession
from app.session_store import users_db, sessions_db, active_sessions

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

# Request/Response models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole

class UserLogin(BaseModel):
    username: str
    password: str

# Authentication endpoints
@router.post("/register")
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

@router.post("/login")
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

@router.get("/me")
async def get_current_user_info(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        # Return a default user if no token
        return {
            "id": 0,
            "username": "guest",
            "email": "guest@viralish.com",
            "role": "GUEST",
            "created_at": datetime.now(),
            "is_active": True
        }
    return get_current_user(authorization)

@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    # Remove from active sessions
    for token, user in active_sessions.items():
        if user.id == current_user.id:
            del active_sessions[token]
            break

    return {"message": "Logged out successfully"}

# Initialize with default users
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