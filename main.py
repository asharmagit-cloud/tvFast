from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection
from routes import state_routes, city_routes, place_routes, test_routes, label_routes, state_standard_routes, city_standard_routes
from config import settings


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
