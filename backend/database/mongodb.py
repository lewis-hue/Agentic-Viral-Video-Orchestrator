import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = "viralish"

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

async def get_database():
    return database