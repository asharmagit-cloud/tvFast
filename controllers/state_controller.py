from typing import List, Optional, Any
from bson import ObjectId
from fastapi import HTTPException, status
from database import get_database
from models.state import StateModel
from datetime import datetime
from schemas.state import StateCreate, StateUpdate, StateResponse, StateListResponse, StateQueryRequest, StateMinimalResponse, StateQueryResponse


class StateController:
    def __init__(self):
        self.collection_name = "states"

    def _convert_object_ids(self, obj: Any) -> Any:
        """Recursively convert ObjectId instances to strings for JSON serialization."""
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, list):
            return [self._convert_object_ids(item) for item in obj]
        if isinstance(obj, dict):
            return {key: self._convert_object_ids(value) for key, value in obj.items()}
        return obj

    async def _enrich_locations_with_names(self, db, states: List[dict]) -> List[dict]:
        """Attach country/region names to location items using referenced collections."""
        # Collect unique ids
        country_ids = set()
        region_ids = set()
        for s in states:
            for loc in s.get("location", []) or []:
                country = (loc or {}).get("country")
                region = (loc or {}).get("region")

                # Country id may be stored as: {"id": ...}, or directly as a string/ObjectId
                if country:
                    cid_val = None
                    if isinstance(country, dict):
                        cid_val = country.get("id")
                    else:
                        cid_val = country
                    if cid_val:
                        try:
                            country_ids.add(ObjectId(str(cid_val)))
                        except Exception:
                            # invalid id format, log for debugging
                            print(f"⚠️ Invalid country id format for state '{s.get('name')}', value: {cid_val}")

                # Region id may be stored similarly
                if region:
                    rid_val = None
                    if isinstance(region, dict):
                        rid_val = region.get("id")
                    else:
                        rid_val = region
                    if rid_val:
                        try:
                            region_ids.add(ObjectId(str(rid_val)))
                        except Exception:
                            print(f"⚠️ Invalid region id format for state '{s.get('name')}', value: {rid_val}")

        # Fetch lookup maps
        countries_map = {}
        regions_map = {}
        if country_ids:
            # only request the name field to reduce payload
            cursor = db["countries"].find({"_id": {"$in": list(country_ids)}}, {"name": 1})
            docs = await cursor.to_list(length=None)
            for doc in docs:
                countries_map[str(doc.get("_id"))] = doc.get("name")
            missing_countries = {str(cid) for cid in country_ids} - set(countries_map.keys())
            if missing_countries:
                print(f"⚠️ Missing country documents for IDs: {sorted(missing_countries)}")
        if region_ids:
            cursor = db["regions"].find({"_id": {"$in": list(region_ids)}}, {"name": 1})
            docs = await cursor.to_list(length=None)
            for doc in docs:
                regions_map[str(doc.get("_id"))] = doc.get("name")
            missing_regions = {str(rid) for rid in region_ids} - set(regions_map.keys())
            if missing_regions:
                print(f"⚠️ Missing region documents for IDs: {sorted(missing_regions)}")

        # Inject names
        for s in states:
            for loc in s.get("location", []) or []:
                country = (loc or {}).get("country")
                if country:
                    # normalize id value
                    if isinstance(country, dict):
                        cid_val = country.get("id")
                    else:
                        cid_val = country
                    if cid_val:
                        cid = str(cid_val) if not isinstance(cid_val, ObjectId) else str(cid_val)
                        cname = countries_map.get(cid)
                        # explicitly set name (could be None)
                        country_obj = country if isinstance(country, dict) else {"id": cid_val}
                        country_obj["name"] = cname if cname is not None else None
                        # ensure loc.country references the object with name
                        loc["country"] = country_obj
                region = (loc or {}).get("region")
                if region:
                    if isinstance(region, dict):
                        rid_val = region.get("id")
                    else:
                        rid_val = region
                    if rid_val:
                        rid = str(rid_val) if not isinstance(rid_val, ObjectId) else str(rid_val)
                        rname = regions_map.get(rid)
                        region_obj = region if isinstance(region, dict) else {"id": rid_val}
                        region_obj["name"] = rname if rname is not None else None
                        loc["region"] = region_obj
        return states

    async def _enrich_labels_with_names(self, db, states: List[dict]) -> List[dict]:
        """Attach label names to label items using referenced collections."""
        # Collect unique label ids
        label_ids = set()
        for s in states:
            for label in s.get("labels", []) or []:
                if isinstance(label, dict) and label.get("id"):
                    try:
                        label_ids.add(ObjectId(str(label["id"])))
                    except Exception:
                        pass

        # Fetch lookup map
        labels_map = {}
        if label_ids:
            cursor = db["labels"].find({"_id": {"$in": list(label_ids)}})
            for doc in await cursor.to_list(length=None):
                labels_map[str(doc.get("_id"))] = doc.get("name")

        # Inject names
        for s in states:
            for label in s.get("labels", []) or []:
                if isinstance(label, dict) and label.get("id"):
                    lid = str(label["id"]) if not isinstance(label["id"], ObjectId) else str(label["id"])
                    lname = labels_map.get(lid)
                    if lname:
                        label["name"] = lname
        return states

    async def create_state(self, state_data: StateCreate) -> StateResponse:
        """Create a new state"""
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
        collection = db[self.collection_name]
        
        # Check if state with same code already exists
        existing_state = await collection.find_one({"code": state_data.code})
        if existing_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"State with code '{state_data.code}' already exists"
            )
        
        # Create state model
        state_model = StateModel(**state_data.model_dump())
        state_dict = state_model.model_dump(by_alias=True, exclude={"id"})

        # Insert into database
        result = await collection.insert_one(state_dict)
        
        # Fetch the created state
        created_state = await collection.find_one({"_id": result.inserted_id})
        created_state = self._convert_object_ids(created_state)
        if created_state and created_state.get("_id") and not created_state.get("id"):
            created_state["id"] = created_state["_id"]
        return StateResponse(**created_state)

    async def get_state_by_id(self, state_id: str) -> StateResponse:
        """Get state by ID"""
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        state = await collection.find_one({"_id": ObjectId(state_id)})
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        # Enrich referenced names for location and labels before converting ids
        try:
            enriched = await self._enrich_locations_with_names(db, [state])
            enriched = await self._enrich_labels_with_names(db, enriched)
            state = enriched[0] if enriched else state
        except Exception:
            # If enrichment fails for any reason, continue with original document
            pass

        state = self._convert_object_ids(state)
        if state and state.get("_id") and not state.get("id"):
            state["id"] = state["_id"]
        return StateResponse(**state)

    async def get_states(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> StateListResponse:
        """Get list of states with pagination and filtering"""
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
        collection = db[self.collection_name]
        
        # Build filter query
        filter_query = {}
        if search:
            filter_query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"code": {"$regex": search, "$options": "i"}}
            ]
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        # Get total count
        total = await collection.count_documents(filter_query)
        
        # Get states with pagination
        cursor = collection.find(filter_query).skip(skip).limit(limit)
        states = await cursor.to_list(length=limit)
        # Enrich names from referenced collections (locations first)
        states = await self._enrich_locations_with_names(db, states)
        states = await self._enrich_labels_with_names(db, states)
        states = [self._convert_object_ids(s) for s in states]
        for s in states:
            if s.get("_id") and not s.get("id"):
                s["id"] = s["_id"]
        
        # Convert to response models
        state_responses = [StateResponse(**state) for state in states]
        
        # Calculate pagination info
        page = (skip // limit) + 1
        has_next = (skip + limit) < total
        has_prev = skip > 0
        
        return StateListResponse(
            states=state_responses,
            total=total,
            page=page,
            size=limit,
            has_next=has_next,
            has_prev=has_prev
        )

    async def update_state(self, state_id: str, state_data: StateUpdate) -> StateResponse:
        """Update state by ID"""
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        # Check if state exists
        existing_state = await collection.find_one({"_id": ObjectId(state_id)})
        if not existing_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        
        # Check if new code conflicts with existing state
        if state_data.code:
            code_conflict = await collection.find_one({
                "code": state_data.code,
                "_id": {"$ne": ObjectId(state_id)}
            })
            if code_conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"State with code '{state_data.code}' already exists"
                )
        
        # Prepare update data
        update_data = {k: v for k, v in state_data.model_dump().items() if v is not None}
        if update_data:
            # set updatedAt explicitly instead of instantiating StateModel without required fields
            update_data["updatedAt"] = datetime.utcnow()

        # Update state
        await collection.update_one(
            {"_id": ObjectId(state_id)},
            {"$set": update_data}
        )
        
        # Return updated state
        updated_state = await collection.find_one({"_id": ObjectId(state_id)})
        updated_state = self._convert_object_ids(updated_state)
        if updated_state and updated_state.get("_id") and not updated_state.get("id"):
            updated_state["id"] = updated_state["_id"]
        return StateResponse(**updated_state)

    async def delete_state(self, state_id: str) -> dict:
        """Delete state by ID"""
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
        collection = db[self.collection_name]
        
        if not ObjectId.is_valid(state_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state ID format"
            )
        
        # Check if state exists
        existing_state = await collection.find_one({"_id": ObjectId(state_id)})
        if not existing_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        
        # Check if state has cities
        cities_collection = db["cities"]
        cities_count = await cities_collection.count_documents({"state_id": ObjectId(state_id)})
        if cities_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete state. It has {cities_count} cities associated with it."
            )
        
        # Delete state
        await collection.delete_one({"_id": ObjectId(state_id)})
        
        return {"message": "State deleted successfully"}

    async def get_state_by_code(self, code: str) -> StateResponse:
        """Get state by code"""
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
        collection = db[self.collection_name]
        
        state = await collection.find_one({"code": code.upper()})
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        # Enrich location and labels
        try:
            enriched = await self._enrich_locations_with_names(db, [state])
            enriched = await self._enrich_labels_with_names(db, enriched)
            state = enriched[0] if enriched else state
        except Exception:
            pass

        state = self._convert_object_ids(state)
        if state and state.get("_id") and not state.get("id"):
            state["id"] = state["_id"]
        return StateResponse(**state)

    async def get_all_states(self) -> List[StateResponse]:
        """Get all states from the collection without pagination"""
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
        collection = db[self.collection_name]
        
        cursor = collection.find({})
        states = await cursor.to_list(length=None)
        states = await self._enrich_locations_with_names(db, states)
        states = await self._enrich_labels_with_names(db, states)
        states = [self._convert_object_ids(s) for s in states]
        for s in states:
            if s.get("_id") and not s.get("id"):
                s["id"] = s["_id"]
        
        return [StateResponse(**state) for state in states]

    async def get_states_page(self, skip: int, limit: int) -> List[StateResponse]:
        """Return a page (array) of states without metadata, for POST /all use case"""
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
        collection = db[self.collection_name]
        cursor = collection.find({}).skip(skip).limit(limit)
        states = await cursor.to_list(length=limit)
        states = await self._enrich_locations_with_names(db, states)
        states = await self._enrich_labels_with_names(db, states)
        states = [self._convert_object_ids(s) for s in states]
        for s in states:
            if s.get("_id") and not s.get("id"):
                s["id"] = s["_id"]
        return [StateResponse(**state) for state in states]

    async def query_states(self, query: StateQueryRequest) -> StateQueryResponse:
        """Flexible state query with templates, filtering, and pagination"""
        db = await get_database()
        if db is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
        collection = db[self.collection_name]
        
        # Build filter query
        filter_query = {}
        
        # Handle single state by ID
        if query.id:
            if not ObjectId.is_valid(query.id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state ID format"
                )
            filter_query["_id"] = ObjectId(query.id)
        
        # Handle search
        if query.search:
            filter_query["$or"] = [
                {"name": {"$regex": query.search, "$options": "i"}},
                {"tagLine": {"$regex": query.search, "$options": "i"}}
            ]
        
        # Handle label filtering
        if query.labels:
            label_object_ids: List[ObjectId] = []
            for label_id in query.labels:
                if ObjectId.is_valid(label_id):
                    label_object_ids.append(ObjectId(label_id))


            if label_object_ids:
                if query.label_filter_type == "all":
                    filter_query["labels.id"] = {"$all": list(label_object_ids)}
                else:  # "any" (OR logic)
                    filter_query["labels.id"] = {"$in": list(label_object_ids)}

        # Get total count
        total = await collection.count_documents(filter_query)
        
        # Handle fetch_all for minimal data
        if query.fetch_all and query.template == "minimal":
            cursor = collection.find(filter_query)
            states = await cursor.to_list(length=None)
            # Enrich locations and labels
            states = await self._enrich_locations_with_names(db, states)
            states = await self._enrich_labels_with_names(db, states)
            
            # Convert to minimal response format
            minimal_states = []
            for state in states:
                state_id = str(state.get("_id"))
                # Convert ObjectIds in labels to strings
                labels = []
                for label in state.get("labels", []):
                    if isinstance(label, dict):
                        label_copy = label.copy()
                        if "id" in label_copy and isinstance(label_copy["id"], ObjectId):
                            label_copy["id"] = str(label_copy["id"])
                        labels.append(label_copy)
                
                minimal_state = {
                    "id": state_id,
                    "name": state.get("name", ""),
                    "tagLine": state.get("tagLine"),
                    "labels": labels,
                    "images": state.get("images")
                }
                minimal_states.append(StateMinimalResponse(**minimal_state))
            
            return StateQueryResponse(
                states=minimal_states,
                total=total,
                page=1,
                limit=total,
                total_pages=1,
                has_next=False,
                has_prev=False,
                next_count=0
            )
        
        # Handle pagination
        skip = (query.page - 1) * query.limit
        
        # Projection based on template
        projection = {}
        if query.template == "minimal":
            projection = {
                "_id": 1,
                "name": 1,
                "tagLine": 1,
                "labels": 1,
                "images": 1
            }
        
        # Get states with projection
        cursor = collection.find(filter_query, projection).skip(skip).limit(query.limit)
        states = await cursor.to_list(length=query.limit)
        # Enrich locations and labels
        states = await self._enrich_locations_with_names(db, states)
        states = await self._enrich_labels_with_names(db, states)
        
        # Convert to response format based on template
        response_data = []
        if query.template == "minimal":
            for state in states:
                state_id = str(state.get("_id"))
                # Convert ObjectIds in labels to strings
                labels = []
                for label in state.get("labels", []):
                    if isinstance(label, dict):
                        label_copy = label.copy()
                        if "id" in label_copy and isinstance(label_copy["id"], ObjectId):
                            label_copy["id"] = str(label_copy["id"])
                        labels.append(label_copy)
                
                minimal_state = {
                    "id": state_id,
                    "name": state.get("name", ""),
                    "tagLine": state.get("tagLine"),
                    "labels": labels,
                    "images": state.get("images")
                }
                response_data.append(StateMinimalResponse(**minimal_state))
        else:
            # For other templates, use full StateResponse (will be implemented later)
            states = [self._convert_object_ids(s) for s in states]
            for s in states:
                if s.get("_id") and not s.get("id"):
                    s["id"] = s["_id"]
            response_data = [StateResponse(**state) for state in states]
        
        # Calculate pagination metadata
        total_pages = (total + query.limit - 1) // query.limit
        has_next = query.page < total_pages
        has_prev = query.page > 1
        next_count = min(query.limit, total - (query.page * query.limit)) if has_next else 0
        
        return StateQueryResponse(
            states=response_data,
            total=total,
            page=query.page,
            limit=query.limit,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            next_count=next_count
        )

    async def query_states_new(self, query: StateQueryRequest) -> StateQueryResponse:
        """New flexible state query with filter object and from/size pagination"""
        try:
            db = await get_database()
            if db is None:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain database connection")
            collection = db[self.collection_name]
            
            # Build filter query
            filter_query = {}
            
            # Handle state IDs filtering
            if query.filter.id:
                # Check if it's the special "t_all" case
                if "t_all" in query.filter.id:
                    # Get all states - no additional filter needed
                    pass
                else:
                    # Filter by specific state IDs
                    state_object_ids = []
                    for state_id in query.filter.id:
                        if ObjectId.is_valid(state_id):
                            state_object_ids.append(ObjectId(state_id))
                    
                    if state_object_ids:
                        filter_query["_id"] = {"$in": state_object_ids}
                    else:
                        # No valid IDs provided, return empty result
                        return StateQueryResponse(
                            states=[],
                            total=0,
                            page=1,
                            limit=query.size,
                            total_pages=0,
                            has_next=False,
                            has_prev=False,
                            next_count=0
                        )
            
            # Get total count
            total = await collection.count_documents(filter_query)
            
            # Handle fetch_all parameter
            if query.fetch_all:
                # Get all data without pagination
                skip = 0
                limit = total  # Set limit to total count to get all records
            else:
                # Handle pagination with offset/size
                skip = query.offset
                limit = query.size
            
            # Projection based on view type
            projection = {}
            if query.filter.view == "minimal":
                projection = {
                    "_id": 1,
                    "name": 1,
                    "tagLine": 1,
                    "labels": 1,
                    "images": 1
                }
            
            # Get states with projection
            cursor = collection.find(filter_query, projection).skip(skip).limit(limit)
            states = await cursor.to_list(length=limit)
            # Enrich locations and labels
            states = await self._enrich_locations_with_names(db, states)
            states = await self._enrich_labels_with_names(db, states)
            
            # Convert to response format based on view type
            response_data = []
            if query.filter.view == "minimal":
                for state in states:
                    state_id = str(state.get("_id"))
                    # Convert ObjectIds in labels to strings
                    labels = []
                    for label in state.get("labels", []):
                        if isinstance(label, dict):
                            label_copy = label.copy()
                            if "id" in label_copy and isinstance(label_copy["id"], ObjectId):
                                label_copy["id"] = str(label_copy["id"])
                            labels.append(label_copy)
                    
                    minimal_state = {
                        "id": state_id,
                        "name": state.get("name", ""),
                        "tagLine": state.get("tagLine"),
                        "labels": labels,
                        "images": state.get("images")
                    }
                    response_data.append(StateMinimalResponse(**minimal_state))
            else:
                # For full view, use complete StateResponse
                states = [self._convert_object_ids(s) for s in states]
                for s in states:
                    if s.get("_id") and not s.get("id"):
                        s["id"] = s["_id"]
                response_data = [StateResponse(**state) for state in states]
            
            # Calculate pagination metadata
            if query.fetch_all:
                # For fetch_all, return all data in single page
                page = 1
                total_pages = 1
                has_next = False
                has_prev = False
                next_count = 0
            else:
                # Normal pagination
                page = (skip // limit) + 1
                total_pages = (total + limit - 1) // limit
                has_next = (skip + limit) < total
                has_prev = skip > 0
                next_count = min(limit, total - (skip + limit)) if has_next else 0
            
            return StateQueryResponse(
                states=response_data,
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev,
                next_count=next_count
            )
        except Exception as e:
            import traceback
            error_detail = f"Internal server error: {str(e)}\nTraceback: {traceback.format_exc()}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )
