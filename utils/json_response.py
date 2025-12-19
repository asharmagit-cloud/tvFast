from fastapi.responses import JSONResponse
from typing import Any
import json


def remove_id_from_dict(obj: Any) -> Any:
    """Recursively remove '_id' keys from dictionaries"""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key != '_id':
                result[key] = remove_id_from_dict(value)
        return result
    elif isinstance(obj, list):
        return [remove_id_from_dict(item) for item in obj]
    else:
        return obj


class CleanJSONResponse(JSONResponse):
    """JSONResponse that automatically removes _id from all responses"""
    
    def render(self, content: Any) -> bytes:
        # Remove _id from content before rendering
        cleaned_content = remove_id_from_dict(content)
        return super().render(cleaned_content)
