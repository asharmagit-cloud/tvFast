from fastapi import APIRouter, HTTPException, status
from database import get_database
from bson import ObjectId
import asyncio

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/mongo")
async def test_mongo_connection():
    """
    Test MongoDB connection and return connection status.
    
    This endpoint tests:
    - Database connection
    - Basic read/write operations
    - Collection access
    """
    try:
        # Get database connection
        db = await get_database()
        
        # Test basic connection by pinging the database
        await db.command("ping")
        
        # Test collection access
        test_collection = db["connection_test"]
        
        # Test write operation
        test_doc = {
            "test": "connection_test",
            "timestamp": "2023-01-01T00:00:00Z",
            "status": "success"
        }
        
        # Insert test document
        result = await test_collection.insert_one(test_doc)
        test_id = result.inserted_id
        
        # Test read operation
        retrieved_doc = await test_collection.find_one({"_id": test_id})
        
        # Test count operation
        doc_count = await test_collection.count_documents({})
        
        # Clean up test document
        await test_collection.delete_one({"_id": test_id})
        
        return {
            "status": "success",
            "message": "MongoDB connection is working properly",
            "database_name": db.name,
            "tests_passed": {
                "ping": True,
                "write": True,
                "read": True,
                "count": True,
                "delete": True
            },
            "document_count": doc_count,
            "connection_details": {
                "database": db.name,
                "collections_accessible": True
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"MongoDB connection failed: {str(e)}",
            "error_type": type(e).__name__,
            "tests_passed": {
                "ping": False,
                "write": False,
                "read": False,
                "count": False,
                "delete": False
            },
            "troubleshooting": {
                "check_mongodb_running": "Make sure MongoDB is running on localhost:27017",
                "check_connection_string": "Verify MONGODB_URL in your environment variables",
                "check_firewall": "Ensure no firewall is blocking port 27017",
                "check_mongodb_service": "Try starting MongoDB service manually"
            }
        }



    



@router.get("/mongo/collections")
async def test_mongo_collections():
    """
    Test MongoDB collections access and list available collections.
    """
    try:
        db = await get_database()
        
        # List all collections
        collections = await db.list_collection_names()
        
        # Get collection stats
        collection_stats = {}
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            collection_stats[collection_name] = {
                "document_count": count,
                "accessible": True
            }
        
        return {
            "status": "success",
            "message": "Collections accessed successfully",
            "database_name": db.name,
            "collections": collections,
            "collection_stats": collection_stats
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to access collections: {str(e)}",
            "error_type": type(e).__name__
        }


# make a route to disply all the collections in the database
@router.get("/mongo/collections/all")
async def test_mongo_collections_all():
    """
    Test MongoDB collections access and list available collections.
    """
    try:
        db = await get_database()

        print(db.name)
        
        # List all collections
        collections = await db.list_collection_names()
        print(collections)
        return {
            "status": "success",
            "message": "Collections accessed successfully",
            "database_name": db.name,
            "collections": collections
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to access collections: {str(e)}",
            "error_type": type(e).__name__
        }
