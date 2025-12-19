from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json
from typing import Any


def remove_id_from_dict(obj: Any) -> Any:
    """Recursively remove '_id' keys from dictionaries"""
    if isinstance(obj, dict):
        # Create a new dict without '_id' key
        result = {}
        for key, value in obj.items():
            if key != '_id':
                result[key] = remove_id_from_dict(value)
        return result
    elif isinstance(obj, list):
        return [remove_id_from_dict(item) for item in obj]
    else:
        return obj


class RemoveIdMiddleware(BaseHTTPMiddleware):
    """Middleware to remove '_id' field from all JSON responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Check if response has JSON content type
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                # Read response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                # Parse JSON
                data = json.loads(body.decode('utf-8'))
                
                # Remove '_id' from the response recursively
                cleaned_data = remove_id_from_dict(data)
                
                # Create new response with cleaned data
                return JSONResponse(
                    content=cleaned_data,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type="application/json"
                )
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                # If it's not valid JSON or can't be processed, return original response
                return response
        
        return response
