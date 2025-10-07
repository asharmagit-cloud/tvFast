from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from controllers.place_controller import PlaceController
from schemas.place import PlaceCreate, PlaceUpdate, PlaceResponse, PlaceListResponse

router = APIRouter(prefix="/places", tags=["Places"])

# Initialize controller
place_controller = PlaceController()


@router.post("/", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
async def create_place(place_data: PlaceCreate):
    """
    Create a new place.
    
    - **name**: Place name (required)
    - **description**: Place description (optional)
    - **city_id**: City ID (required)
    - **city_name**: City name (required)
    - **state_id**: State ID (required)
    - **state_name**: State name (required)
    - **state_code**: State code (required)
    - **address**: Place address (optional)
    - **latitude**: Latitude coordinate (optional)
    - **longitude**: Longitude coordinate (optional)
    - **category**: Place category (optional)
    - **tags**: List of tags (optional)
    - **is_active**: Whether place is active (default: True)
    """
    return await place_controller.create_place(place_data)


@router.get("/{place_id}", response_model=PlaceResponse)
async def get_place(place_id: str):
    """
    Get a place by ID.
    
    - **place_id**: Place ID (required)
    """
    return await place_controller.get_place_by_id(place_id)


@router.get("/", response_model=PlaceListResponse)
async def get_places(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in name, description, city name, or state name"),
    city_id: Optional[str] = Query(None, description="Filter by city ID"),
    state_id: Optional[str] = Query(None, description="Filter by state ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """
    Get list of places with pagination and filtering.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 10, max: 100)
    - **search**: Search term for name, description, city name, or state name
    - **city_id**: Filter by city ID
    - **state_id**: Filter by state ID
    - **category**: Filter by category
    - **is_active**: Filter by active status
    """
    return await place_controller.get_places(skip, limit, search, city_id, state_id, category, is_active)


@router.put("/{place_id}", response_model=PlaceResponse)
async def update_place(place_id: str, place_data: PlaceUpdate):
    """
    Update a place by ID.
    
    - **place_id**: Place ID (required)
    - **place_data**: Place data to update
    """
    return await place_controller.update_place(place_id, place_data)


@router.delete("/{place_id}")
async def delete_place(place_id: str):
    """
    Delete a place by ID.
    
    - **place_id**: Place ID (required)
    """
    return await place_controller.delete_place(place_id)


@router.get("/city/{city_id}", response_model=List[PlaceResponse])
async def get_places_by_city(city_id: str):
    """
    Get all places by city ID.
    
    - **city_id**: City ID (required)
    """
    return await place_controller.get_places_by_city(city_id)


@router.get("/state/{state_id}", response_model=List[PlaceResponse])
async def get_places_by_state(state_id: str):
    """
    Get all places by state ID.
    
    - **state_id**: State ID (required)
    """
    return await place_controller.get_places_by_state(state_id)


@router.get("/nearby/search", response_model=List[PlaceResponse])
async def search_places_nearby(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    radius_km: float = Query(10.0, ge=0.1, le=1000, description="Search radius in kilometers"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    Search for places within a specified radius of given coordinates.
    
    - **latitude**: Latitude coordinate (required)
    - **longitude**: Longitude coordinate (required)
    - **radius_km**: Search radius in kilometers (default: 10.0, max: 1000)
    - **limit**: Maximum number of results (default: 20, max: 100)
    """
    return await place_controller.search_places_nearby(latitude, longitude, radius_km, limit)
