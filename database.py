from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config import settings
from typing import Optional


class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None


db = Database()


async def get_database():
    """Return database instance"""
    return db.database


async def connect_to_mongo():
    """Create database connection"""
    try:
        # Create async client
        db.client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        # Select your database name (for example, from settings)
        db.database = db.client[settings.database_name]

        # Test the connection
        await db.client.admin.command("ping")
        print("Connected to MongoDB successfully")

    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        db.client = None
        db.database = None
    except Exception as e:
        print(f"Unexpected MongoDB error: {e}")
        db.client = None
        db.database = None


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        db.client = None
        db.database = None
        print("Disconnected from MongoDB")
