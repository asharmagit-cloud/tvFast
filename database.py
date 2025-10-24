try:
    from motor.motor_asyncio import AsyncIOMotorClient
except Exception as e:
    # Provide a clear, actionable error to help the developer fix version mismatches
    raise ImportError(
        "Failed to import Motor AsyncIOMotorClient. This often indicates an incompatible combination of `motor` and `pymongo` in the virtual environment.\n"
        "Detected error: {0!s}\n\n"
        "Suggested fix (run in your project venv):\n"
        "  pip uninstall -y bson pymongo motor\n"
        "  pip install 'pymongo==4.6.0' 'motor==3.3.2'\n\n"
        "After installing, restart your application. If you intentionally need a newer pymongo, upgrade `motor` to a compatible release instead.\n"
        "See https://motor.readthedocs.io/ and PyMongo release notes for compatibility details.".format(e)
    ) from e

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
