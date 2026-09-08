import json
import asyncio

# In-memory storage for connected clients
connected_clients = {}

# Helper function for safe broadcasting
async def broadcast_to_clients(message: dict):
    failed_clients = []
    for client_id, client in list(connected_clients.items()):
        try:
            await client.send_text(json.dumps(message))
        except Exception:
            failed_clients.append(client_id)
    for client_id in failed_clients:
        del connected_clients[client_id]