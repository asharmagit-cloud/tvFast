from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection
from routes import state_routes, city_routes, place_routes, test_routes, label_routes, state_standard_routes, city_standard_routes
from config import settings
from typing import Any
import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

def remove_id_from_dict(obj: Any) -> Any:
    """Recursively remove '_id', 'createdAt', and 'updatedAt' keys from dictionaries and ensure 'id' is first"""
    if isinstance(obj, dict):
        result = {}
        id_value = None
        for key, value in obj.items():
            # Skip _id, createdAt, updatedAt, created_at, updated_at
            if key not in ('_id', 'createdAt', 'updatedAt', 'created_at', 'updated_at'):
                if key == 'id':
                    # Store id to put it first
                    id_value = remove_id_from_dict(value)
                else:
                    result[key] = remove_id_from_dict(value)
        
        # Put 'id' first if it exists
        if id_value is not None:
            ordered_result = {'id': id_value}
            ordered_result.update(result)
            return ordered_result
        return result
    elif isinstance(obj, list):
        return [remove_id_from_dict(item) for item in obj]
    else:
        return obj


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


# Create FastAPI application
app = FastAPI(
    title="FastTV API",
    description="A FastAPI application for managing states, cities, and places with MongoDB",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware to remove _id from all JSON responses
class RemoveIdMiddleware(BaseHTTPMiddleware):
    """Middleware to remove '_id' field from all JSON responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Check if response has JSON content type
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                # Read the response body
                if hasattr(response, 'body_iterator'):
                    body = b""
                    async for chunk in response.body_iterator:
                        body += chunk
                    
                    # Parse and clean JSON
                    if body:
                        data = json.loads(body.decode('utf-8'))
                        cleaned_data = remove_id_from_dict(data)
                        
                        # Create new headers without Content-Length (let FastAPI recalculate it)
                        new_headers = {k: v for k, v in response.headers.items() if k.lower() != 'content-length'}
                        
                        # Return new JSONResponse with cleaned data
                        return JSONResponse(
                            content=cleaned_data,
                            status_code=response.status_code,
                            headers=new_headers
                        )
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError, ValueError) as e:
                # If processing fails, return original response
                logger.debug(f"Could not process response to remove _id: {e}", exc_info=True)
                pass
        
        return response

# Add middleware to remove _id from responses (must be before CORS)
app.add_middleware(RemoveIdMiddleware)

# Add CORS middleware
# In production, use specific origins from environment variable
allowed_origins = settings.allowed_origins.split(",") if settings.allowed_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(state_routes.router, prefix="/api/v1")
app.include_router(city_routes.router, prefix="/api/v1")
app.include_router(place_routes.router, prefix="/api/v1")
app.include_router(test_routes.router, prefix="/api/v1")
app.include_router(label_routes.router, prefix="/api/v1")
# Standard format endpoints (singular)
app.include_router(state_standard_routes.router, prefix="/api/v1")
app.include_router(city_standard_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    from database import db
    try:
        # Check database connection
        if db.database is None:
            return {"status": "unhealthy", "database": "disconnected"}
        
        # Try a simple database operation
        await db.database.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "service": "FastTV API"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to FastTV API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "states": "/api/v1/states",
            "cities": "/api/v1/cities",
            "places": "/api/v1/places"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    from database import db
    try:
        # Check database connection
        if db.database is None:
            return {"status": "unhealthy", "database": "disconnected"}
        
        # Try a simple database operation
        await db.database.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "service": "FastTV API",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
