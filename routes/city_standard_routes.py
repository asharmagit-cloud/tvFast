from fastapi import APIRouter, Query, status
from controllers.city_controller import CityController
from schemas.city import CityStandardRequest, CityStandardResponse

router = APIRouter(prefix="/city", tags=["Cities"])

# Initialize controller
city_controller = CityController()


@router.post("/", response_model=CityStandardResponse)
async def query_city_standard(
    request: CityStandardRequest,
    view: str = Query(default="minimal", description="View type: 'minimal' or 'full'")
):
    """
    Standard city query endpoint with filters format.
    
    **Request Body:**
    ```json
    {
      "filters": {
        "id": ["t_all"],  // Array of city IDs or ["t_all"] for all cities
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
    return await city_controller.query_cities_standard(request, view)

