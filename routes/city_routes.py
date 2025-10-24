from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from controllers.city_controller import CityController
from schemas.city import CityCreate, CityUpdate, CityResponse, CityListResponse
from schemas.state import StateQueryRequest

router = APIRouter(prefix="/cities", tags=["Cities"])

# Initialize controller
city_controller = CityController()


@router.post("/", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(city_data: CityCreate):
    """
    Create a new city.
    
    - **name**: City name (required)
    - **state_id**: State ID (required)
    - **state_name**: State name (required)
    - **state_code**: State code (required)
    - **is_active**: Whether city is active (default: True)
    """
    return await city_controller.create_city(city_data)


@router.get("/{city_id}", response_model=CityResponse)
async def get_city(city_id: str):
    """
    Get a city by ID.
    
    - **city_id**: City ID (required)
    """
    return await city_controller.get_city_by_id(city_id)


@router.get("/", response_model=CityListResponse)
async def get_cities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in name or state name"),
    state_id: Optional[str] = Query(None, description="Filter by state ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """
    Get list of cities with pagination and filtering.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 10, max: 100)
    - **search**: Search term for name or state name
    - **state_id**: Filter by state ID
    - **is_active**: Filter by active status
    """
    return await city_controller.get_cities(skip, limit, search, state_id, is_active)


@router.put("/{city_id}", response_model=CityResponse)
async def update_city(city_id: str, city_data: CityUpdate):
    """
    Update a city by ID.
    
    - **city_id**: City ID (required)
    - **city_data**: City data to update
    """
    return await city_controller.update_city(city_id, city_data)


@router.delete("/{city_id}")
async def delete_city(city_id: str):
    """
    Delete a city by ID.
    
    - **city_id**: City ID (required)
    
    Note: City cannot be deleted if it has places associated with it.
    """
    return await city_controller.delete_city(city_id)


@router.get("/state/{state_id}", response_model=List[CityResponse])
async def get_cities_by_state(state_id: str):
    """
    Get all cities by state ID.
    
    - **state_id**: State ID (required)
    """
    return await city_controller.get_cities_by_state(state_id)


@router.post("/query", response_model=CityListResponse)
async def query_cities(query: StateQueryRequest):
    """
    Flexible city query endpoint with comprehensive filter support.
    
    **Request Body Format:**
    ```json
    {
      "filter": {
        "view": "minimal",         // "minimal" | "full"
        "id": ["t_all"],           // ["t_all"] for all cities OR ["<id1>", "<id2>", ...] for specific cities
        "state_id": ["<state_id>"], // Optional: filter by state IDs
        "search": "Mumbai",        // Optional: regex search on name and tagLine
        "labels": ["<label_id>"],  // Optional: filter by labels
        "label_filter_type": "any" // "any" | "all" - how to match labels
      },
      "offset": 0,                 // Starting index for pagination
      "size": 10,                  // Number of items to return
      "fetch_all": false           // Set to true to get all matching records
    }
    ```
    
    **Examples:**
    - Get all cities (minimal view): `{"filter": {"view": "minimal", "id": ["t_all"]}, "fetch_all": true}`
    - Paginated results: `{"filter": {"id": ["t_all"]}, "offset": 0, "size": 20}`
    - Filter by state: `{"filter": {"state_id": ["<state_id>"]}, "offset": 0, "size": 10}`
    - Search by name: `{"filter": {"search": "Mumbai"}, "offset": 0, "size": 10}`
    """
    return await city_controller.query_cities_new(query)
