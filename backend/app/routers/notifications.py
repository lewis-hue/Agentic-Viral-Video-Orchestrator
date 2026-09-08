from fastapi import APIRouter, Depends, HTTPException, status
from database.mongodb_models import Notification, OnlineUser
from database.mongodb import get_database
from models.knowledge_base import User, UserRole
from app.session_store import active_sessions
from datetime import datetime
from .auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_notifications(current_user: User = Depends(get_current_user)):
    db = await get_database()
    notifications = await db.notifications.find().sort("timestamp", -1).to_list(length=None)
    # Convert ObjectId to str for JSON serialization
    return [{**n, '_id': str(n['_id'])} for n in notifications]

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    db = await get_database()
    await db.notifications.update_one({"_id": notification_id}, {"$set": {"read": True}})
    return {"message": "Notification marked as read"}

@router.put("/read-all")
async def mark_all_read(current_user: User = Depends(get_current_user)):
    db = await get_database()
    await db.notifications.update_many({"read": False}, {"$set": {"read": True}})
    return {"message": "All notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    db = await get_database()
    await db.notifications.delete_one({"_id": notification_id})
    return {"message": "Notification deleted"}

@router.delete("/")
async def clear_all_notifications(current_user: User = Depends(get_current_user)):
    db = await get_database()
    await db.notifications.delete_many({})
    return {"message": "All notifications cleared"}

@router.get("/online-users")
async def get_online_users(current_user: User = Depends(get_current_user)):
    db = await get_database()
    # Get online users from active sessions
    online_users = []
    for token, user in active_sessions.items():
        online_users.append({
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "last_seen": datetime.now()
        })
    return online_users