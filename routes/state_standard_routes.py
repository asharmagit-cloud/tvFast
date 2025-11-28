from fastapi import APIRouter, Query, status
from controllers.state_controller import StateController
from schemas.state import StateStandardRequest, StateStandardResponse

router = APIRouter(prefix="/state", tags=["States"])

# Initialize controller
state_controller = StateController()


@router.post("/", response_model=StateStandardResponse)
async def query_state_standard(
    request: StateStandardRequest,
    view: str = Query(default="minimal", description="View type: 'minimal' or 'full'")
):
    """
    Standard state query endpoint with filters format.
    
    **Request Body:**
    ```json
    {
      "filters": {
        "id": ["t_all"],  // Array of state IDs or ["t_all"] for all states
        "from": 0,        // Starting index for pagination
        "size": 10         // Number of items to return
      }
    }
    ```
    
    **Query Parameters:**
    - **view**: 'minimal' (default) or 'full'
    
    **Response:**
    ```json
    {
      "result": [{}, {}...],
      "total_count": total
    }
    ```
    """
    return await state_controller.query_states_standard(request, view)

