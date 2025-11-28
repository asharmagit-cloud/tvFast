from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, status
from database import get_database
from models.city import CityModel
from schemas.city import CityCreate, CityUpdate, CityResponse, CityListResponse, CityStandardRequest, CityStandardResponse
from datetime import datetime, timezone
from types import SimpleNamespace
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_objectids(obj):
    if isinstance(obj, dict):
        return {k: convert_objectids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(i) for i in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj


def normalize_response_data(data: dict) -> dict:
    """Normalize response data to match frontend interface:
    - location -> locations (plural)
    - tagLine -> tagline (lowercase)
    - Ensure labels are in format [{name, id}, ...]
    """
    normalized = data.copy()
    
    # Convert location to locations
    if "location" in normalized and "locations" not in normalized:
        normalized["locations"] = normalized.pop("location")
    elif "location" in normalized and "locations" in normalized:
        # If both exist, prefer locations
        normalized.pop("location")
    
    # Convert tagLine to tagline
    if "tagLine" in normalized and "tagline" not in normalized:
        normalized["tagline"] = normalized.pop("tagLine")
    elif "tagLine" in normalized and "tagline" in normalized:
        # If both exist, prefer tagline
        normalized.pop("tagLine")
    
    # Normalize labels to ensure they're in format [{name, id}, ...]
    if "labels" in normalized and normalized["labels"]:
        labels = normalized["labels"]
        if isinstance(labels, list):
            normalized_labels = []
            for label in labels:
                if isinstance(label, dict):
                    # Ensure it has both name and id
                    if "id" in label:
                        normalized_labels.append({
                            "id": str(label.get("id", "")),
                            "name": label.get("name", "")
                        })
                elif isinstance(label, str):
                    # If it's just a string, convert to {id: string, name: ""}
                    normalized_labels.append({
                        "id": label,
                        "name": ""
                    })
            normalized["labels"] = normalized_labels if normalized_labels else None
    
    return normalized


class CityController:
    def __init__(self):
        self.collection_name = "cities"

    async def _enrich_locations_with_names(self, db, cities: List[dict]) -> List[dict]:
        """Batch enrich location names for cities (countries, regions, states)."""
        # Collect unique IDs
        country_ids = set()
        region_ids = set()
        state_ids = set()
        
        for city in cities:
            if city.get("location") and isinstance(city["location"], list):
                for loc in city["location"]:
                    if not isinstance(loc, dict):
                        continue
                    # Country
                    country = loc.get("country")
                    if isinstance(country, dict) and country.get("id") and (country.get("name") is None):
                        try:
                            country_ids.add(ObjectId(str(country["id"])))
                        except Exception:
                            pass
                    # Region
                    region = loc.get("region")
                    if isinstance(region, dict) and region.get("id") and (region.get("name") is None):
                        try:
                            region_ids.add(ObjectId(str(region["id"])))
                        except Exception:
                            pass
                    # State
                    state_ref = loc.get("state")
                    if isinstance(state_ref, dict) and state_ref.get("id") and (state_ref.get("name") is None):
                        try:
                            state_ids.add(ObjectId(str(state_ref["id"])))
                        except Exception:
                            pass
        
        # Batch fetch lookup maps
        countries_map = {}
        regions_map = {}
        states_map = {}
        
        collection_names = await db.list_collection_names()
        
        if country_ids and "countries" in collection_names:
            cursor = db["countries"].find({"_id": {"$in": list(country_ids)}})
            async for doc in cursor:
                countries_map[str(doc.get("_id"))] = doc.get("name")
        
        if region_ids and "regions" in collection_names:
            cursor = db["regions"].find({"_id": {"$in": list(region_ids)}})
            async for doc in cursor:
                regions_map[str(doc.get("_id"))] = doc.get("name")
        
        if state_ids:
            cursor = db["states"].find({"_id": {"$in": list(state_ids)}})
            async for doc in cursor:
                states_map[str(doc.get("_id"))] = doc.get("name")
        
        # Inject names into cities
        for city in cities:
            if city.get("location") and isinstance(city["location"], list):
                for loc in city["location"]:
                    if not isinstance(loc, dict):
                        continue
                    # Country
                    country = loc.get("country")
                    if isinstance(country, dict) and country.get("id"):
                        cid = str(country["id"]) if not isinstance(country["id"], ObjectId) else str(country["id"])
                        cname = countries_map.get(cid)
                        if cname:
                            country["name"] = cname
                            loc["country"] = country
                    # Region
                    region = loc.get("region")
                    if isinstance(region, dict) and region.get("id"):
                        rid = str(region["id"]) if not isinstance(region["id"], ObjectId) else str(region["id"])
                        rname = regions_map.get(rid)
                        if rname:
                            region["name"] = rname
                            loc["region"] = region
                    # State
                    state_ref = loc.get("state")
                    if isinstance(state_ref, dict) and state_ref.get("id"):
                        sid = str(state_ref["id"]) if not isinstance(state_ref["id"], ObjectId) else str(state_ref["id"])
                        sname = states_map.get(sid)
                        if sname:
                            state_ref["name"] = sname
                            loc["state"] = state_ref
        
        return cities

    async def create_city(self, city_data: CityCreate) -> CityResponse:
        """Create a new city"""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Validate state_id
        if not ObjectId.is_valid(city_data.state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        # Check if state exists
        states_collection = db["states"]
        state = await states_collection.find_one({"_id": ObjectId(city_data.state_id)})
        if not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State not found"
            )
        
        # Check if city with same name in same state already exists
        existing_city = await collection.find_one({
            "name": city_data.name,
            "state_id": ObjectId(city_data.state_id)
        })
        if existing_city:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"City '{city_data.name}' already exists in this state"
            )
        
        # Create city model
        city_dict = city_data.model_dump()
        city_dict["state_id"] = ObjectId(city_data.state_id)
        city_model = CityModel(**city_dict)
        city_dict = city_model.model_dump(by_alias=True, exclude={"id"})

        # Insert into database
        result = await collection.insert_one(city_dict)
        
        # Return created city (reuse get_city_by_id logic for proper formatting)
        return await self.get_city_by_id(str(result.inserted_id))

    async def get_city_by_id(self, city_id: str) -> CityResponse:
        """Get city by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(city_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid city ID format"
            )
        
        city = await collection.find_one({"_id": ObjectId(city_id)})
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        
        # Convert ObjectIds to strings
        city = convert_objectids(city)
        
        # Enrich location names if needed
        states_collection = db["states"]
        countries_collection = db["countries"] if "countries" in await db.list_collection_names() else None
        regions_collection = db["regions"] if "regions" in await db.list_collection_names() else None
        
        if city.get("location") and isinstance(city["location"], list):
            for loc in city["location"]:
                if not isinstance(loc, dict):
                    continue
                # Country
                country = loc.get("country")
                if isinstance(country, dict) and country.get("id") and (country.get("name") is None) and countries_collection is not None:
                    country_doc = await countries_collection.find_one({"_id": ObjectId(country["id"])})
                    if country_doc:
                        country["name"] = country_doc.get("name")
                        loc["country"] = country
                # Region
                region = loc.get("region")
                if isinstance(region, dict) and region.get("id") and (region.get("name") is None) and regions_collection is not None:
                    region_doc = await regions_collection.find_one({"_id": ObjectId(region["id"])})
                    if region_doc:
                        region["name"] = region_doc.get("name")
                        loc["region"] = region
                # State
                state_ref = loc.get("state")
                if isinstance(state_ref, dict) and state_ref.get("id") and (state_ref.get("name") is None):
                    state_doc = await states_collection.find_one({"_id": ObjectId(state_ref["id"])})
                    if state_doc:
                        state_ref["name"] = state_doc.get("name")
                        loc["state"] = state_ref
        
        # Extract and convert state_id
        city_id_str = str(city.get("_id")) if city.get("_id") else None
        state_id_val = city.get("state_id")
        
        # Safely extract state id from location if state_id missing
        if not state_id_val and city.get("location") and isinstance(city.get("location"), list) and len(city.get("location")) > 0:
            first_loc = city.get("location")[0]
            if isinstance(first_loc, dict):
                state_obj = first_loc.get("state")
                if isinstance(state_obj, dict) and state_obj.get("id"):
                    state_id_val = state_obj.get("id")
        
        state_id_str = str(state_id_val) if state_id_val else None
        
        # Get state name
        state_name = None
        if state_id_str:
            try:
                state_doc = await states_collection.find_one({"_id": ObjectId(state_id_str)})
                if state_doc:
                    state_name = state_doc.get("name")
            except Exception:
                state_name = None
        
        # Validate required fields
        if not city_id_str or not city.get("name"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="City document missing required fields (id or name)"
            )
        
        if not state_id_str:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="City document missing required state_id field"
            )
        
        # Build response dict
        city_response_dict = {
            "id": city_id_str,
            "name": city.get("name"),
            "state_id": state_id_str,
            "is_active": city.get("is_active", True),
            "locations": city.get("location") or city.get("locations"),  # Use locations (plural)
            "greetingText": city.get("greetingText"),
            "tagline": city.get("tagLine") or city.get("tagline"),  # Use tagline (lowercase)
            "languages": city.get("languages"),
            "description": city.get("description"),
            "images": city.get("images"),
            "emergencyContacts": city.get("emergencyContacts"),
            "safetyInformation": city.get("safetyInformation"),
            "travelTips": city.get("travelTips"),
            "experiences": city.get("experiences"),
            "trending": city.get("trending")
        }
        
        if state_name:
            city_response_dict["state_name"] = state_name
        
        # CityResponse expects _id as alias for id
        response_input = city_response_dict.copy()
        response_input["_id"] = response_input.pop("id")
        
        return CityResponse(**response_input)

    async def get_cities(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search: Optional[str] = None,
        state_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> CityListResponse:
        """Get list of cities with pagination and filtering (minimal fields)"""
        db = await get_database()
        collection = db[self.collection_name]

        # Build filter query
        filter_query = {}
        if search:
            filter_query["name"] = {"$regex": search, "$options": "i"}
        if state_id:
            if not ObjectId.is_valid(state_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state ID format"
                )
            filter_query["state_id"] = ObjectId(state_id)
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        # Get total count
        total = await collection.count_documents(filter_query)
        
        # Get cities with pagination
        cursor = collection.find(filter_query).skip(skip).limit(limit)
        cities = await cursor.to_list(length=limit)
        
        # Convert ObjectIds to strings
        cities = [convert_objectids(city) for city in cities]
        
        # Batch enrich location names (countries, regions, states)
        cities = await self._enrich_locations_with_names(db, cities)
        
        # Collect all state IDs for batch fetching state names
        state_ids_for_names = set()
        for city in cities:
            state_id_val = city.get("state_id")
            if not state_id_val and city.get("location") and isinstance(city.get("location"), list) and len(city.get("location")) > 0:
                first_loc = city.get("location")[0]
                if isinstance(first_loc, dict):
                    state_obj = first_loc.get("state")
                    if isinstance(state_obj, dict) and state_obj.get("id"):
                        state_id_val = state_obj.get("id")
            if state_id_val:
                try:
                    state_ids_for_names.add(ObjectId(str(state_id_val)))
                except Exception:
                    pass
        
        # Batch fetch state names
        states_map = {}
        if state_ids_for_names:
            states_collection = db["states"]
            cursor = states_collection.find({"_id": {"$in": list(state_ids_for_names)}})
            async for doc in cursor:
                states_map[str(doc.get("_id"))] = doc.get("name")
        
        # Build response objects
        city_responses = []
        for city in cities:
            city_id = str(city.get("_id")) if city.get("_id") else None
            state_id_val = city.get("state_id")
            # Safely extract state id from location if state_id missing
            if not state_id_val and city.get("location") and isinstance(city.get("location"), list) and len(city.get("location")) > 0:
                first_loc = city.get("location")[0]
                if isinstance(first_loc, dict):
                    state_obj = first_loc.get("state")
                    if isinstance(state_obj, dict) and state_obj.get("id"):
                        state_id_val = state_obj.get("id")
                    else:
                        state_id_val = None
                else:
                    state_id_val = None
            state_id_str = str(state_id_val) if state_id_val else None
            name = city.get("name")
            state_name = states_map.get(state_id_str) if state_id_str else None
            city_response_dict = {
                "id": city_id,
                "name": name,
                "state_id": state_id_str,
                "is_active": city.get("is_active", True),
                "locations": city.get("location") or city.get("locations"),  # Use locations (plural)
                "greetingText": city.get("greetingText"),
                "tagline": city.get("tagLine") or city.get("tagline"),  # Use tagline (lowercase)
                "languages": city.get("languages"),
                "description": city.get("description"),
                "images": city.get("images"),
                "emergencyContacts": city.get("emergencyContacts"),
                "safetyInformation": city.get("safetyInformation"),
                "travelTips": city.get("travelTips"),
                "experiences": city.get("experiences"),
                "trending": city.get("trending")
            }
            if state_name:
                city_response_dict["state_name"] = state_name
            # Skip documents missing essential fields (id and name). Allow missing state_id.
            if not city_id or not name:
                continue
            city_responses.append(CityResponse(**city_response_dict))

        # Calculate pagination info
        page = (skip // limit) + 1
        has_next = (skip + limit) < total
        has_prev = skip > 0
        
        return CityListResponse(
            cities=city_responses,
            total=total,
            page=page,
            size=limit,
            has_next=has_next,
            has_prev=has_prev
        )

    async def update_city(self, city_id: str, city_data: CityUpdate) -> CityResponse:
        """Update city by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(city_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid city ID format"
            )
        
        # Check if city exists
        existing_city = await collection.find_one({"_id": ObjectId(city_id)})
        if not existing_city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        
        # Validate state_id if provided
        if city_data.state_id:
            if not ObjectId.is_valid(city_data.state_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state ID format"
                )
            
            # Check if state exists
            states_collection = db["states"]
            state = await states_collection.find_one({"_id": ObjectId(city_data.state_id)})
            if not state:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="State not found"
                )
        
        # Check if new name conflicts with existing city in same state
        if city_data.name:
            state_id_to_check = ObjectId(city_data.state_id) if city_data.state_id else existing_city["state_id"]
            name_conflict = await collection.find_one({
                "name": city_data.name,
                "state_id": state_id_to_check,
                "_id": {"$ne": ObjectId(city_id)}
            })
            if name_conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"City '{city_data.name}' already exists in this state"
                )
        
        # Prepare update data
        update_data = {k: v for k, v in city_data.model_dump().items() if v is not None}
        if update_data:
            if "state_id" in update_data:
                update_data["state_id"] = ObjectId(update_data["state_id"])
            update_data["updatedAt"] = datetime.now(timezone.utc)

        # Update city
        await collection.update_one(
            {"_id": ObjectId(city_id)},
            {"$set": update_data}
        )
        
        # Return updated city (reuse get_city_by_id logic)
        return await self.get_city_by_id(city_id)

    async def delete_city(self, city_id: str) -> dict:
        """Delete city by ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(city_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid city ID format"
            )
        
        # Check if city exists
        existing_city = await collection.find_one({"_id": ObjectId(city_id)})
        if not existing_city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        
        # Check if city has places
        places_collection = db["places"]
        places_count = await places_collection.count_documents({"city_id": ObjectId(city_id)})
        if places_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete city. It has {places_count} places associated with it."
            )
        
        # Delete city
        await collection.delete_one({"_id": ObjectId(city_id)})
        
        return {"message": "City deleted successfully"}

    async def get_cities_by_state(self, state_id: str) -> List[CityResponse]:
        """Get all cities by state ID"""
        db = await get_database()
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        cursor = collection.find({"state_id": ObjectId(state_id), "is_active": True})
        cities = await cursor.to_list(length=None)
        
        return [CityResponse(**city) for city in cities]

    async def query_cities_new(self, query) -> CityListResponse:
        """Flexible city query with filter object and offset/size pagination.

        Expected query format (compatible with StateQueryRequest used in states):
        {
            "filter": { "view": "minimal"|"full", "id": ["t_all"] or ["<id>" ...], "state_id": [..], "search": "..", "labels": [..], "label_filter_type": "any"|"all" },
            "offset": 0,
            "size": 10,
            "fetch_all": false
        }
        """
        try:
            db = await get_database()
            if db is None:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
            collection = db[self.collection_name]

            # Build filter query
            filter_query = {}

            # Helper to read attributes from either object (Pydantic model) or dict
            def _fget(obj, name, default=None):
                if obj is None:
                    return default
                if hasattr(obj, name):
                    return getattr(obj, name)
                if isinstance(obj, dict):
                    return obj.get(name, default)
                return default

            filter_obj = getattr(query, "filter", None)
            # If filter_obj is a plain dict inside query (some clients), leave as-is; _fget will handle both

            # Handle IDs filtering (filter.id may be present)
            ids_val = _fget(filter_obj, "id", None)
            if ids_val:
                try:
                    ids = list(ids_val)
                except Exception:
                    ids = None
                if ids:
                    if "t_all" in ids:
                        # no-op: return all
                        pass
                    else:
                        city_object_ids = []
                        for cid in ids:
                            # support dict items like {"id": "..."}
                            cid_val = None
                            if isinstance(cid, dict):
                                cid_val = cid.get("id") or cid.get("_id")
                            else:
                                cid_val = cid
                            if cid_val and ObjectId.is_valid(str(cid_val)):
                                city_object_ids.append(ObjectId(str(cid_val)))
                        if city_object_ids:
                            filter_query["_id"] = {"$in": city_object_ids}
                        else:
                            # no valid ids -> empty result
                            logger.info("No valid IDs provided in filter.id, returning empty result")
                            return CityListResponse(cities=[], total=0, page=1, size=_fget(query, "size", 0), has_next=False, has_prev=False)

            # Handle search
            search_term = _fget(filter_obj, "search", None)
            if search_term:
                filter_query["$or"] = [
                    {"name": {"$regex": search_term, "$options": "i"}},
                    {"tagLine": {"$regex": search_term, "$options": "i"}}
                ]

            # Handle state_id filtering (accept single or list)
            state_id_val = _fget(filter_obj, "state_id", None)
            if state_id_val:
                try:
                    state_ids = list(state_id_val)
                except Exception:
                    state_ids = [state_id_val]
                state_object_ids = []
                for sid in state_ids:
                    # support dict entries
                    sid_val = sid.get("id") if isinstance(sid, dict) else sid
                    if sid_val is None:
                        continue
                    if ObjectId.is_valid(str(sid_val)):
                        state_object_ids.append(ObjectId(str(sid_val)))
                        # Also add as string for matching both formats
                        state_object_ids.append(str(sid_val))
                    else:
                        state_object_ids.append(str(sid_val))
                if state_object_ids:
                    # Combine all state_ids (both ObjectId and string) into single $in
                    filter_query["state_id"] = {"$in": state_object_ids}

            # Handle label filtering if present in filter_obj (labels.id stored as objects in documents)
            labels_val = _fget(filter_obj, "labels", None)
            if labels_val:
                try:
                    label_list = list(labels_val)
                except Exception:
                    label_list = [labels_val]
                label_obj_ids = []
                label_strs = []
                for lid in label_list:
                    # support dict entries like {"id": "..."}
                    lid_val = lid.get("id") if isinstance(lid, dict) else lid
                    if lid_val is None:
                        continue
                    if ObjectId.is_valid(str(lid_val)):
                        label_obj_ids.append(ObjectId(str(lid_val)))
                        label_strs.append(str(lid_val))
                    else:
                        label_strs.append(str(lid_val))
                if label_obj_ids or label_strs:
                    # For 'all' we need both types in each element; Mongo $all requires exact matches, so include both
                    if _fget(filter_obj, "label_filter_type", None) == "all":
                        # Build an $and with two $all clauses if both types present
                        if label_obj_ids and label_strs:
                            # ensure both object and string forms are present
                            filter_query["$and"] = filter_query.get("$and", []) + [
                                {"labels.id": {"$all": label_obj_ids}},
                                {"labels.id": {"$all": label_strs}}
                            ]
                        elif label_obj_ids:
                            filter_query["labels.id"] = {"$all": label_obj_ids}
                        else:
                            filter_query["labels.id"] = {"$all": label_strs}
                    else:
                        # 'any' -> $in; include both object and string lists
                        in_list = []
                        if label_obj_ids:
                            in_list.extend(label_obj_ids)
                        if label_strs:
                            in_list.extend(label_strs)
                        filter_query["labels.id"] = {"$in": in_list}

            # Debug/log the generated filter before querying
            logger.info(f"City query filter: {filter_query}")

            # Get total count
            total = await collection.count_documents(filter_query)
            logger.info(f"City query total matched documents: {total}")

            # Handle pagination / fetch_all
            if getattr(query, "fetch_all", False):
                skip = 0
                limit = total
            else:
                skip = getattr(query, "offset", 0)
                limit = getattr(query, "size", 10)

            # ensure limit is sensible (avoid limit == 0)
            if not limit or limit <= 0:
                if getattr(query, "fetch_all", False):
                    limit = total
                else:
                    limit = 10

            # Projection based on view
            projection = {}
            view = _fget(filter_obj, "view", "full")
            if view == "minimal":
                projection = {"_id": 1, "name": 1, "state_id": 1, "tagLine": 1, "images": 1}

            logger.info(f"Using projection={projection}, skip={skip}, limit={limit}, view={view}")

            cursor = collection.find(filter_query, projection).skip(skip).limit(limit)
            # If fetch_all requested, or limit equals total, get full list via to_list(length=None)
            if getattr(query, "fetch_all", False):
                cities = await cursor.to_list(length=None)
            else:
                cities = await cursor.to_list(length=limit)

            logger.info(f"Fetched {len(cities)} cities from DB (skip={skip}, limit={limit})")

            # Convert ObjectIds to strings
            cities = [convert_objectids(city) for city in cities]
            
            # Batch enrich location names (countries, regions, states)
            cities = await self._enrich_locations_with_names(db, cities)
            
            # Collect all state IDs for batch fetching state names
            state_ids_for_names = set()
            for city in cities:
                state_id_val = city.get("state_id")
                if not state_id_val and city.get("location") and isinstance(city.get("location"), list) and len(city.get("location")) > 0:
                    first_loc = city.get("location")[0]
                    if isinstance(first_loc, dict):
                        state_obj = first_loc.get("state")
                        if isinstance(state_obj, dict) and state_obj.get("id"):
                            state_id_val = state_obj.get("id")
                if state_id_val:
                    try:
                        state_ids_for_names.add(ObjectId(str(state_id_val)))
                    except Exception:
                        pass
            
            # Batch fetch state names
            states_map = {}
            if state_ids_for_names:
                states_collection = db["states"]
                cursor = states_collection.find({"_id": {"$in": list(state_ids_for_names)}})
                async for doc in cursor:
                    states_map[str(doc.get("_id"))] = doc.get("name")

            # Build response objects depending on view
            city_responses = []

            for city in cities:
                # minimal view should include only a subset
                city_id = str(city.get("_id")) if city.get("_id") else None
                state_id_val = city.get("state_id")
                # Safely extract state id from location if state_id missing
                if not state_id_val and city.get("location") and isinstance(city.get("location"), list) and len(city.get("location")) > 0:
                    first_loc = city.get("location")[0]
                    if isinstance(first_loc, dict):
                        state_obj = first_loc.get("state")
                        if isinstance(state_obj, dict) and state_obj.get("id"):
                            state_id_val = state_obj.get("id")
                        else:
                            state_id_val = None
                    else:
                        state_id_val = None
                state_id_str = str(state_id_val) if state_id_val else None

                name = city.get("name")
                state_name = states_map.get(state_id_str) if state_id_str else None

                if view == "minimal":
                    # construct minimal response
                    city_response_dict = {
                        "id": city_id,
                        "name": name,
                        "state_id": state_id_str,
                        "images": city.get("images"),
                        "tagline": city.get("tagLine") or city.get("tagline"),  # Use tagline (lowercase)
                        "is_active": city.get("is_active", True),
                        "locations": city.get("location") or city.get("locations")  # Use locations (plural)
                    }
                else:
                    # full view - include available fields
                    city_response_dict = {
                        "id": city_id,
                        "name": name,
                        "state_id": state_id_str,
                        "is_active": city.get("is_active", True),
                        "locations": city.get("location") or city.get("locations"),  # Use locations (plural)
                        "greetingText": city.get("greetingText"),
                        "tagline": city.get("tagLine") or city.get("tagline"),  # Use tagline (lowercase)
                        "languages": city.get("languages"),
                        "description": city.get("description"),
                        "images": city.get("images"),
                        "emergencyContacts": city.get("emergencyContacts"),
                        "safetyInformation": city.get("safetyInformation"),
                        "travelTips": city.get("travelTips"),
                        "experiences": city.get("experiences"),
                        "trending": city.get("trending")
                    }

                if state_name:
                    city_response_dict["state_name"] = state_name

                # Skip documents missing essential fields (id and name)
                if not city_id or not name:
                    continue

                # CityResponse Pydantic model expects alias _id for id - CityResponse config sets populate_by_name
                # Provide mapping expected by CityResponse: alias for id is "_id"
                # Use a copy where key "_id" maps to id value to satisfy the schema
                response_input = city_response_dict.copy()
                response_input["_id"] = response_input.pop("id")

                try:
                    city_responses.append(CityResponse(**response_input))
                except Exception as e:
                    logger.exception(f"Failed to build CityResponse for city {city_id}: {e}")
                    continue

            # Pagination info
            if limit and limit > 0:
                page = (skip // limit) + 1
            else:
                page = 1
            has_next = (skip + limit) < total if limit and limit > 0 else False
            has_prev = skip > 0

            return CityListResponse(
                cities=city_responses,
                total=total,
                page=page,
                size=limit,
                has_next=has_next,
                has_prev=has_prev
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error in query_cities_new: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def query_cities_standard(self, request: CityStandardRequest, view: str = "minimal") -> CityStandardResponse:
        """Standard city query endpoint with filters format"""
        try:
            from schemas.state import StateQueryRequest, StateQueryFilter
            # Convert standard request to StateQueryRequest format (cities use same format as states)
            query = StateQueryRequest(
                filter=StateQueryFilter(
                    view=view,
                    id=request.filters.id
                ),
                offset=request.filters.from_,
                size=request.filters.size,
                fetch_all=False
            )
            
            # Use existing query_cities_new method
            result = await self.query_cities_new(query)
            
            # Convert to standard response format
            return CityStandardResponse(
                result=result.cities,
                total_count=result.total
            )
        except Exception as e:
            logger.exception(f"Error in query_cities_standard: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to query cities: {str(e)}"
            )
