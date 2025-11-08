# State Query API Documentation

## Overview

The State Query API provides a flexible POST endpoint `/api/v1/states/query` that supports multiple templates, filtering, pagination, and search capabilities for state data retrieval.

## Base URL
```
POST /api/v1/states/query
```

## Request Schema

### 1. Request Body (Get All States):
```json
{
  "filter": {
    "view": "minimal",             // Required: "minimal" | "full"
    "id": ["t_all"]                // Special identifier to get all states
  },
  "from": 0,                       // Optional: Starting index (default: 0)
  "size": 10                       // Optional: Number of items to return (default: 10)
}
```

### 2. Request Body (Get Specific States):
```json
{
  "filter": {
    "view": "minimal",             // Required: "minimal" | "full"
    "id": ["<id1>", "<id2>", "<id3>", "..."]  // Array of specific state IDs
  },
  "from": 0,                       // Optional: Starting index (default: 0)
  "size": 10                       // Optional: Number of items to return (default: 10)
}
```

## Response Schema

```json
{
  "states": [                      // Array of state objects
    {
      "id": "string",
      "name": "string",
      "tagLine": "string",
      "labels": [                  // Only in minimal template
        {
          "id": "string",
          "name": "string"
        }
      ],
      "images": {                  // Only in minimal template
        "banner": "string",
        "card": "string",
        "others": ["string"]
      }
    }
  ],
  "total": 36,                     // Total number of records
  "page": 1,                       // Current page number
  "limit": 10,                     // Items per page
  "total_pages": 4,                // Total number of pages
  "has_next": true,                // Has next page
  "has_prev": false,               // Has previous page
  "next_count": 10                 // Items in next page
}
```

## Template Types

### 1. Minimal Template
Returns essential fields for listing/card views:
- `id`: State ID
- `name`: State name
- `tagLine`: State tagline
- `labels`: Array of labels with id and name
- `images`: Image URLs (banner, card, others)

### 2. Page Template (Coming Soon)
Returns fields optimized for page display:
- All minimal fields
- Additional fields for page rendering

### 3. Full Template (Coming Soon)
Returns complete state data:
- All available fields
- Complete state information

## Query Examples

### 1. Basic Pagination
Get first page with 10 items:
```json
{
  "template": "minimal",
  "page": 1,
  "limit": 10
}
```

### 2. Fetch All Data
Get all minimal data without pagination:
```json
{
  "template": "minimal",
  "fetch_all": true
}
```

### 3. Single State by ID
Get specific state by ID:
```json
{
  "template": "minimal",
  "id": "68dc1021e2dc335296605a38"
}
```

### 4. Search by Name or TagLine
Search for states containing "Maharashtra":
```json
{
  "template": "minimal",
  "search": "Maharashtra",
  "page": 1,
  "limit": 5
}
```

### 5. Filter by Single Label (OR Logic)
Get states with Heritage label:
```json
{
  "template": "minimal",
  "labels": ["68d90c36fc0c58520c6cf223"],
  "label_filter_type": "any",
  "page": 1,
  "limit": 10
}
```

### 6. Filter by Multiple Labels (OR Logic)
Get states with Heritage OR Adventure labels:
```json
{
  "template": "minimal",
  "labels": [
    "68d90c36fc0c58520c6cf223",
    "68d90c36fc0c58520c6cf224"
  ],
  "label_filter_type": "any",
  "page": 1,
  "limit": 10
}
```

### 7. Filter by Multiple Labels (AND Logic)
Get states with BOTH Heritage AND Adventure labels:
```json
{
  "template": "minimal",
  "labels": [
    "68d90c36fc0c58520c6cf223",
    "68d90c36fc0c58520c6cf224"
  ],
  "label_filter_type": "all",
  "page": 1,
  "limit": 10
}
```

### 8. Combined Search and Label Filter
Search for "gateway" AND filter by Heritage label:
```json
{
  "template": "minimal",
  "search": "gateway",
  "labels": ["68d90c36fc0c58520c6cf223"],
  "label_filter_type": "any",
  "page": 1,
  "limit": 5
}
```

### 9. Large Page Size
Get 50 items per page:
```json
{
  "template": "minimal",
  "page": 1,
  "limit": 50
}
```

### 10. Second Page
Get second page with 5 items:
```json
{
  "template": "minimal",
  "page": 2,
  "limit": 5
}
```

### 11. Search with Pagination
Search for "gateway" with pagination:
```json
{
  "template": "minimal",
  "search": "gateway",
  "page": 1,
  "limit": 10
}
```

### 12. Label Filter with Search
Filter by Adventure label and search for "mountain":
```json
{
  "template": "minimal",
  "labels": ["68d90c36fc0c58520c6cf224"],
  "label_filter_type": "any",
  "search": "mountain",
  "page": 1,
  "limit": 10
}
```

## Testing with Different Tools

### 1. Swagger UI
Visit: `http://localhost:8000/docs`
- Navigate to `/api/v1/states/query`
- Click "Try it out"
- Paste any query example
- Click "Execute"

### 2. cURL
```bash
curl -X POST "http://localhost:8000/api/v1/states/query" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "minimal",
    "page": 1,
    "limit": 5
  }'
```

### 3. PowerShell (Windows)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/states/query" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"template": "minimal", "page": 1, "limit": 5}'
```

### 4. Postman/Insomnia
- Method: POST
- URL: `http://localhost:8000/api/v1/states/query`
- Headers: `Content-Type: application/json`
- Body: Any query example from above

## Response Examples

### Successful Response
```json
{
  "states": [
    {
      "id": "68dc1021e2dc335296605a38",
      "name": "Maharashtra",
      "tagLine": "Gateway to the Western Ghats",
      "labels": [
        {
          "id": "68d90c36fc0c58520c6cf223",
          "name": "Heritage"
        }
      ],
      "images": {
        "banner": "https://example.com/banner.jpg",
        "card": "https://example.com/card.jpg",
        "others": ["https://example.com/img1.jpg"]
      }
    }
  ],
  "total": 36,
  "page": 1,
  "limit": 10,
  "total_pages": 4,
  "has_next": true,
  "has_prev": false,
  "next_count": 10
}
```

### Empty Response
```json
{
  "states": [],
  "total": 0,
  "page": 1,
  "limit": 10,
  "total_pages": 0,
  "has_next": false,
  "has_prev": false,
  "next_count": 0
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid state ID format"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Features

### ✅ Implemented
- ✅ Minimal template with id, name, tagLine, labels, images
- ✅ Pagination with metadata (total, page, limit, has_next, etc.)
- ✅ Search in name and tagLine
- ✅ Label filtering (OR/AND logic)
- ✅ Single state retrieval by ID
- ✅ Fetch all data without pagination
- ✅ ObjectId serialization (uses `id` not `_id`)

### 🚧 Coming Soon
- 🚧 Page template implementation
- 🚧 Full template implementation
- 🚧 Advanced filtering options
- 🚧 Sorting capabilities

## Notes

1. **ID Field**: All responses use `id` field (not `_id`) for consistency
2. **Labels**: Label objects include both `id` and `name` for easy display
3. **Pagination**: Page numbers start from 1 (not 0)
4. **Search**: Case-insensitive search in name and tagLine fields
5. **Filtering**: Label filtering supports both OR and AND logic
6. **Performance**: Uses MongoDB projection to fetch only required fields

## Database Collections Used

- `states`: Main state data
- `labels`: Label reference data (for enriching label names)
- `countries`: Country reference data
- `regions`: Region reference data

## Rate Limiting

Currently no rate limiting implemented. Consider adding rate limiting for production use.

## Version

- API Version: 1.0.0
- Last Updated: October 2025
- FastAPI Version: Latest
- MongoDB: Latest
