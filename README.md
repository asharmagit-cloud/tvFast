# FastTV API

A FastAPI application for managing states, cities, and places with MongoDB integration. This application follows industry standards with separate models, controllers, routes, and response schemas. It uses Pydantic v2 and async Motor for MongoDB.

## Features

- **States Management**: Create, read, update, and delete states
- **Cities Management**: Create, read, update, and delete cities with state relationships
- **Places Management**: Create, read, update, and delete places with city and state relationships
- **Geospatial Search**: Find places within a radius of given coordinates
- **Pagination**: Built-in pagination for all list endpoints
- **Search & Filtering**: Search and filter capabilities across all entities
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **MongoDB Integration**: Async MongoDB operations with Motor driver
- **Location Enrichment**: State `location[].country` and `location[].region` are enriched with `name` from `countries` and `regions` collections

## Project Structure

```
fastTV/
├── controllers/          # Business logic controllers
│   ├── __init__.py
│   ├── state_controller.py
│   ├── city_controller.py
│   └── place_controller.py
├── models/              # Database models (Pydantic v2)
│   ├── __init__.py
│   ├── state.py
│   ├── city.py
│   └── place.py
├── schemas/             # Pydantic schemas for request/response
│   ├── __init__.py
│   ├── state.py
│   ├── city.py
│   └── place.py
├── routes/              # API routes
│   ├── __init__.py
│   ├── state_routes.py
│   ├── city_routes.py
│   └── place_routes.py
├── config.py            # Application configuration
├── database.py          # Database connection setup (Motor)
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastTV
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Update the `MONGODB_URL` in `config.py` if needed

5. **Run the application**
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health
- **State Query API**: See `STATE_QUERY_API_README.md` for detailed documentation and examples

## API Endpoints

### States
- `GET /api/v1/states` - List states with pagination and optional search/filter
- `POST /api/v1/states` - Create a new state
- `GET /api/v1/states/{state_id}` - Get state by ID
- `PUT /api/v1/states/{state_id}` - Update state by ID
- `DELETE /api/v1/states/{state_id}` - Delete state by ID
- `GET /api/v1/states/code/{code}` - Get state by code
- `GET /api/v1/states/all` - Get all states (array, no metadata)
- `POST /api/v1/states/all` - Get paginated array of states using POST body: `{ "skip": 0, "limit": 10 }`
- `POST /api/v1/states/query` - **NEW**: Flexible state query with templates, filtering, and pagination

### Cities
- `GET /api/v1/cities` - List all cities with pagination and filtering
- `POST /api/v1/cities` - Create a new city
- `GET /api/v1/cities/{city_id}` - Get city by ID
- `PUT /api/v1/cities/{city_id}` - Update city by ID
- `DELETE /api/v1/cities/{city_id}` - Delete city by ID
- `GET /api/v1/cities/state/{state_id}` - Get cities by state ID

### Places
- `GET /api/v1/places` - List all places with pagination and filtering
- `POST /api/v1/places` - Create a new place
- `GET /api/v1/places/{place_id}` - Get place by ID
- `PUT /api/v1/places/{place_id}` - Update place by ID
- `DELETE /api/v1/places/{place_id}` - Delete place by ID
- `GET /api/v1/places/city/{city_id}` - Get places by city ID
- `GET /api/v1/places/state/{state_id}` - Get places by state ID
- `GET /api/v1/places/nearby/search` - Search places within radius

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=fasttv_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Data Models

### State
- `name`: string (required)
- `location`: array of `{ country: { id, name? }, region: { id, name? } }`
- `greetingText`, `tagLine`: optional strings
- `languages`: array of strings
- `images`: `{ banner?, card?, others?[] }`
- `labels`: array of `{ id, name? }`
- `emergencyContacts`: object of string values
- `safetyInformation`, `travelTips`: arrays of strings
- `experiences`: groups of ObjectId arrays
- `trending`: `{ places?: ObjectId[], cities?: ObjectId[] }`
- `createdAt`, `updatedAt`: ISO datetimes

### City
- `name`: City name (required)
- `slug`: string (required)
- `location`: array of `{ country: { id }, state: { id }, city: { id }, region: { id } }`
- `labels`: array of `{ id }`
- `tips`: array of string
- `bestTimeToVisit`, `localLegend`, `difficultyLevel`: optional strings
- `entryInfo`: object `{ type?, fee?, duration? }`
- `images`, `description`, `geo`, `ratings`: objects
- `createdAt`, `updatedAt`: ISO datetimes

### Place
- `name`: Place name (required)
- `slug`: string (required)
- `location`: array `{ country:{id}, state:{id}, city:{id}, region:{id} }`
- `labels`: array `{ id }`
- `tips`: string[]
- `bestTimeToVisit`, `localLegend`, `difficultyLevel`: strings
- `entryInfo`: `{ type?, fee?, duration? }`
- `images`: `{ banner?, card?, others?[] }`
- `description`: `{ overview?, short?, long?, history? }`
- `geo`: `{ type: 'Point', coordinates: [lng, lat] }`
- `ratings`: `{ average?: number, count?: number }`
- `createdAt`, `updatedAt`: ISO datetimes

## Features

### Pagination
All list endpoints support pagination with `skip` and `limit` parameters.

### Search and Filtering
- Search across multiple fields using the `search` parameter
- Filter by active status using the `is_active` parameter
- Filter cities by state using the `state_id` parameter
- Filter places by city, state, or category

### POST Pagination (States)
- Use POST to paginate array results without metadata:
  - `POST /api/v1/states/all`
  - Body: `{ "skip": 0, "limit": 10 }`
  - Returns: `StateResponse[]`

### State Query API (NEW)
A powerful flexible query endpoint for states with multiple templates and filtering options:

- **Endpoint**: `POST /api/v1/states/query`
- **Templates**: 
  - `minimal`: Essential fields (id, name, tagLine, labels, images)
  - `page`: Coming soon
  - `full`: Coming soon
- **Features**:
  - Pagination with metadata
  - Search in name and tagLine
  - Label filtering (OR/AND logic)
  - Single state retrieval by ID
  - Fetch all data without pagination
- **Documentation**: See `STATE_QUERY_API_README.md` for complete examples

**Quick Example**:
```json
{
  "template": "minimal",
  "page": 1,
  "limit": 10,
  "search": "Maharashtra",
  "labels": ["label_id_1", "label_id_2"],
  "label_filter_type": "any"
}

// Basic minimal data with pagination
// POST /api/v1/states/query
{
  "template": "minimal",
  "page": 1,
  "limit": 10
}

// Get all minimal data at once
// POST /api/v1/states/query
{
  "template": "minimal",
  "fetch_all": true
}

// Search for specific states
// POST /api/v1/states/query
{
  "template": "minimal",
  "search": "Maharashtra",
  "page": 1,
  "limit": 5
}
```

### Geospatial Search
The places endpoint includes geospatial search functionality to find places within a specified radius of given coordinates.

### Data Validation
- Comprehensive input validation using Pydantic models
- Proper error handling with meaningful error messages
- Data type validation and constraints

### API Documentation
- Auto-generated OpenAPI/Swagger documentation
- Detailed endpoint descriptions and examples
- Request/response schema documentation

## Test Utilities

- `GET /api/v1/test/mongo/simple` - ping MongoDB
- `GET /api/v1/test/mongo` - full read/write test
- `GET /api/v1/test/mongo/collections` - list collections and counts

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Code Structure
- **Models**: Database models using Pydantic with MongoDB ObjectId support
- **Schemas**: Separate request/response schemas for API validation
- **Controllers**: Business logic and database operations
- **Routes**: API endpoint definitions with proper documentation
- **Database**: MongoDB connection and configuration

## License

This project is licensed under the MIT License.
