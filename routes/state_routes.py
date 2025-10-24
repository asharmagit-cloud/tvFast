from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from controllers.state_controller import StateController
from schemas.state import StateCreate, StateUpdate, StateResponse, StateListResponse, StateQuery, StateAllQuery, StateQueryRequest, StateQueryRequestLegacy, StateQueryResponse

router = APIRouter(prefix="/states", tags=["States"])

# Initialize controller
state_controller = StateController()


@router.post("/", response_model=StateResponse, status_code=status.HTTP_201_CREATED)
async def create_state(state_data: StateCreate):
    """
    Create a new state.
    
    - **name**: State name (required)
    - **code**: State code (required, unique)
    - **country**: Country name (default: India)
    - **is_active**: Whether state is active (default: True)
    """
    return await state_controller.create_state(state_data)


@router.get("/", response_model=StateListResponse)
async def get_states(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in name or code"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """
    Get list of states with pagination and filtering.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 10, max: 100)
    - **search**: Search term for name or code
    - **is_active**: Filter by active status
    """
    return await state_controller.get_states(skip, limit, search, is_active)


@router.post("/search", response_model=StateListResponse)
async def search_states(query: StateQuery):
    """
    Search states with POST body. Accepts the same parameters as the GET endpoint.
    
    Body:
    - skip: Number of records to skip (default: 0)
    - limit: Number of records to return (default: 10, max: 100)
    - search: Search term for name or code
    - is_active: Filter by active status
    """
    return await state_controller.get_states(
        skip=query.skip,
        limit=query.limit,
        search=query.search,
        is_active=query.is_active
    )


@router.get("/all", response_model=List[StateResponse])
async def get_all_states():
    """
    Get all states from the states collection without pagination.
    
    Returns all states in the database.
    """
    return await state_controller.get_all_states()


@router.post("/all", response_model=List[StateResponse])
async def get_all_states_post(query: StateAllQuery):
    """
    Return a paginated array of states using POST body with skip and limit.
    """
    return await state_controller.get_states_page(skip=query.skip, limit=query.limit)


@router.get("/code/{code}", response_model=StateResponse)
async def get_state_by_code(code: str):
    """
    Get a state by code.
    
    - **code**: State code (required)
    """
    return await state_controller.get_state_by_code(code)


@router.get("/{state_id}", response_model=StateResponse)
async def get_state(state_id: str):
    """
    Get a state by ID.
    
    - **state_id**: State ID (required)
    """
    return await state_controller.get_state_by_id(state_id)


@router.put("/{state_id}", response_model=StateResponse)
async def update_state(state_id: str, state_data: StateUpdate):
    """
    Update a state by ID.
    
    - **state_id**: State ID (required)
    - **state_data**: State data to update
    """
    return await state_controller.update_state(state_id, state_data)


@router.delete("/{state_id}")
async def delete_state(state_id: str):
    """
    Delete a state by ID.
    
    - **state_id**: State ID (required)
    
    Note: State cannot be deleted if it has cities associated with it.
    """
    return await state_controller.delete_state(state_id)


@router.post("/query", response_model=StateQueryResponse)
async def query_states(query: StateQueryRequest):
    """
    Flexible state query endpoint with new filter-based format:
    
    **Request Body Format:**
    ```json
    {
      "filter": {
        "view": "minimal",  // "minimal" | "full"
        "id": ["t_all"]     // ["t_all"] for all states OR ["<id1>", "<id2>", ...] for specific states
      },
      "offset": 0,          // Starting index (default: 0)
      "size": 10,           // Number of items to return (default: 10)
      "fetch_all": false    // Get all data without pagination (default: false)
    }
    ```
    
    **View Options:**
    - **minimal**: Returns id, name, tagLine, labels (with id & name), images
    - **full**: Complete state data (for detail view)
    
    **ID Filtering:**
    - **["t_all"]**: Get all states
    - **["<id1>", "<id2>", ...]**: Get specific states by their IDs
    
    **Pagination:**
    - **offset**: Starting index (default: 0)
    - **size**: Items per page (default: 10)
    - **fetch_all**: Get all data without pagination (default: false)
    """
    return await state_controller.query_states_new(query)


@router.post("/query/legacy", response_model=StateQueryResponse)
async def query_states_legacy(query: StateQueryRequestLegacy):
    """
    Legacy flexible state query endpoint (for backward compatibility):
    - Multiple templates (minimal, page, full)
    - Pagination with metadata
    - Label filtering (OR/AND logic)
    - Single state retrieval by ID
    - Fetch all minimal data option
    
    **Template Options:**
    - **minimal**: Returns id, name, tagLine, labels (with id & name), images
    - **page**: Full state data (for page display)
    - **full**: Complete state data (for detail view)
    
    **Filtering:**
    - **labels**: Array of label IDs to filter by
    - **label_filter_type**: "any" (OR logic) or "all" (AND logic)
    - **search**: Search in name or tagLine
    
    **Pagination:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 10)
    - **fetch_all**: Get all minimal data without pagination
    
    **Single State:**
    - **id**: Get specific state by ID (returns array with one item)
    """
    return await state_controller.query_states(query)
