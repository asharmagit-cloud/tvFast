from fastapi import APIRouter, HTTPException, status
from typing import List
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/labels", tags=["Labels"])


@router.get("/")
async def get_all_labels():
    """
    Get all labels from the database.
    
    Returns a list of all labels with their id and name.
    """
    try:
        db = await get_database()
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to obtain database connection"
            )
        
        collection = db["labels"]
        cursor = collection.find({})
        labels = await cursor.to_list(length=None)
        
        # Convert ObjectIds to strings
        result = []
        for label in labels:
            result.append({
                "id": str(label.get("_id")),
                "name": label.get("name", "")
            })
        
        return {"labels": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch labels: {str(e)}"
        )

