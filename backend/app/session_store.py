from typing import Dict
from models.knowledge_base import User, UserSession

# Shared session store for all routers
users_db: Dict[int, User] = {}
sessions_db: Dict[str, UserSession] = {}
active_sessions: Dict[str, User] = {}
connected_clients: Dict[int, any] = {}