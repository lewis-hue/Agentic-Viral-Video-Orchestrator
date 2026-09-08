from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Header, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import hashlib
from models.knowledge_base import User, UserRole
from database.mongodb_models import ChatMessage, ChatMessageStatus
from database.mongodb import get_database
from app.session_store import users_db, sessions_db, active_sessions
from app.websocket_manager import connected_clients, broadcast_to_clients
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Note: Authentication functions are in auth.py and shared via session_store

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

def get_current_user_from_token(token: str) -> User:
    logger.info(f"Checking token: {token}")
    logger.info(f"Active sessions: {list(active_sessions.keys())}")
    logger.info(f"Sessions DB: {list(sessions_db.keys())}")

    # First check active sessions for performance
    if token in active_sessions:
        logger.info("Token found in active_sessions")
        return active_sessions[token]

    # If not in active sessions, check sessions_db and validate expiration
    if token in sessions_db:
        session = sessions_db[token]
        if datetime.now() > session.expires_at:
            # Session expired, remove it
            del sessions_db[token]
            logger.info("Session expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired"
            )

        # Session is valid, restore to active_sessions
        user = users_db.get(session.user_id)
        if user and user.is_active:
            active_sessions[token] = user
            logger.info("Token restored to active_sessions")
            return user
        else:
            logger.info("User not active or not found")

    logger.info("Token not found")
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

class MessageCreate(BaseModel):
    message: str


# Chat endpoints
@router.get("/messages")
async def get_messages(current_user: User = Depends(get_current_user)):
    db = await get_database()
    messages = await db.chat_messages.find({"status": {"$ne": ChatMessageStatus.DELETED}}).sort("timestamp", 1).to_list(length=None)
    # Convert ObjectId to str for JSON serialization
    return [{**msg, '_id': str(msg['_id'])} for msg in messages]

@router.post("/messages")
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    db = await get_database()
    message = ChatMessage(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role.value,
        message=message_data.message
    )
    result = await db.chat_messages.insert_one(message.dict())
    message.id = str(result.inserted_id)

    # Broadcast to all connected clients
    for client in connected_clients.values():
        await client.send_text(json.dumps({
            "type": "new_message",
            "message": {
                "id": message.id,
                "user_id": message.user_id,
                "username": current_user.username,
                "message": message.message,
                "status": message.status.value,
                "timestamp": message.timestamp.isoformat()
            }
        }))

    # Add notification for new chat message
    notification = {
        "type": "new_chat",
        "title": "New Chat Message",
        "message": f"{current_user.username}: {message_data.message[:50]}...",
        "timestamp": datetime.now(),
        "action_url": "#chat"
    }
    await db.notifications.insert_one(notification)

    return {"message": "Message sent successfully"}

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user)
):
    db = await get_database()
    message = await db.chat_messages.find_one({"_id": message_id})
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    # Only admins can delete any message, or users can delete their own
    if current_user.role != UserRole.ADMIN and message["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Soft delete: set status to DELETED
    await db.chat_messages.update_one({"_id": message_id}, {"$set": {"status": ChatMessageStatus.DELETED}})

    # Broadcast deletion to all connected clients
    await broadcast_to_clients({
        "type": "message_deleted",
        "message_id": message_id
    })

    return {"message": "Message deleted successfully"}


# WebSocket endpoint for real-time chat
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("WebSocket connection attempt")
    # Get token from query params
    token = websocket.query_params.get("token")
    logger.info(f"Token from query: {token}")

    if not token:
        logger.info("No token provided")
        await websocket.close(code=4001, reason="No token provided")
        return

    try:
        current_user = get_current_user_from_token(token)
        logger.info(f"User authenticated: {current_user.username}")
    except HTTPException as e:
        logger.info(f"Authentication failed: {e.detail}")
        await websocket.close(code=4001, reason=e.detail)
        return

    await websocket.accept()
    logger.info("WebSocket accepted")
    client_id = id(websocket)
    connected_clients[client_id] = websocket

    try:
        # Send recent messages
        db = await get_database()
        recent_messages = await db.chat_messages.find({"status": {"$ne": ChatMessageStatus.DELETED}}).sort("timestamp", -1).limit(10).to_list(length=10)
        for msg in recent_messages:
            await websocket.send_text(json.dumps({
                "type": "message",
                "message": {
                    "id": str(msg["_id"]),
                    "user_id": msg["user_id"],
                    "username": msg["username"],
                    "role": msg.get("role", "user"),
                    "message": msg["message"],
                    "status": msg.get("status", ChatMessageStatus.ACTIVE.value),
                    "timestamp": msg["timestamp"].isoformat()
                }
            }))

        # Send current online users list to the new client
        online_users_list = [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role.value
            }
            for user in active_sessions.values()
        ]
        await websocket.send_text(json.dumps({
            "type": "online_users",
            "online_users": online_users_list
        }))

        # Broadcast user joined and online users list
        await broadcast_to_clients({
            "type": "user_joined",
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "role": current_user.role.value
            },
            "online_users": online_users_list
        })

        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                if message_data["type"] == "message":
                    # Handle new message
                    db = await get_database()
                    message = ChatMessage(
                        user_id=current_user.id,
                        username=current_user.username,
                        message=message_data["message"]
                    )
                    result = await db.chat_messages.insert_one(message.dict())
                    message.id = str(result.inserted_id)

                    # Broadcast to all clients
                    await broadcast_to_clients({
                        "type": "new_message",
                        "message": {
                            "id": message.id,
                            "user_id": message.user_id,
                            "username": current_user.username,
                            "role": current_user.role.value,
                            "message": message.message,
                            "status": message.status.value,
                            "timestamp": message.timestamp.isoformat()
                        }
                    })

                    # Add notification
                    notification = {
                        "type": "new_chat",
                        "title": "New Chat Message",
                        "message": f"{current_user.username}: {message_data['message'][:50]}...",
                        "timestamp": datetime.now(),
                        "action_url": "#chat"
                    }
                    await db.notifications.insert_one(notification)

                elif message_data["type"] == "typing_start":
                    # Broadcast typing start
                    await broadcast_to_clients({
                        "type": "typing_start",
                        "user_id": current_user.id
                    })

                elif message_data["type"] == "typing_stop":
                    # Broadcast typing stop
                    await broadcast_to_clients({
                        "type": "typing_stop",
                        "user_id": current_user.id
                    })
                elif message_data["type"] == "delete_message":
                    # Handle delete message
                    message_id = message_data["message_id"]
                    db = await get_database()
                    message = await db.chat_messages.find_one({"_id": message_id})
                    if message and (current_user.role == UserRole.ADMIN or message["user_id"] == current_user.id):
                        await db.chat_messages.update_one({"_id": message_id}, {"$set": {"status": ChatMessageStatus.DELETED}})
                        await broadcast_to_clients({
                            "type": "message_deleted",
                            "message_id": message_id
                        })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                break

    except WebSocketDisconnect:
        del connected_clients[client_id]
        # Broadcast user left and updated online users list
        online_users_list = [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role.value
            }
            for user in active_sessions.values()
        ]
        await broadcast_to_clients({
            "type": "user_left",
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "role": current_user.role.value
            },
            "online_users": online_users_list
        })