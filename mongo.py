import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure

async def test_async_mongo_connection():
    # 🔒 Replace <password> with your actual password (URL-encoded if needed)
    uri = "mongodb+srv://manishtravhoo_db_user:S5NnimoeXGz24nxU@travhoo-web.agcc3gy.mongodb.net/?retryWrites=true&w=majority&appName=travhoo-web"

    print("🔍 Testing MongoDB connection asynchronously...\n")

    client = None
    try:
        # Initialize async client
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)

        # Ping command to test connectivity
        await client.admin.command("ping")

        print("✅ Successfully connected to MongoDB Atlas (AsyncIOMotorClient)!")
        dbs = await client.list_database_names()
        print(f"📦 Databases available: {dbs}")

    except OperationFailure as e:
        print(f"❌ Authentication failed: {e}")
        print("➡️ Check your username or password.")
    except ConnectionFailure as e:
        print(f"❌ Could not connect to MongoDB: {e}")
        print("➡️ Possible causes: wrong URI, cluster not reachable, or network/firewall issue.")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
    finally:
        if client:
            client.close()
        print("\n✅ Test completed.")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_async_mongo_connection())
