from typing import List, Optional, Any
from bson import ObjectId
from fastapi import HTTPException, status
from database import get_database
from models.state import StateModel
from schemas.state import StateCreate, StateUpdate, StateResponse, StateListResponse, StateQueryRequest, StateQueryRequestLegacy, StateMinimalResponse, StateQueryResponse
import logging

logger = logging.getLogger(__name__)


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
                country = (loc or {}).get("country") or {}
                region = (loc or {}).get("region") or {}
                if isinstance(country, dict) and country.get("id"):
                    try:
                        country_ids.add(ObjectId(str(country["id"])))
                    except Exception:
                        pass
                if isinstance(region, dict) and region.get("id"):
                    try:
                        region_ids.add(ObjectId(str(region["id"])))
                    except Exception:
                        pass

        # Fetch lookup maps
        countries_map = {}
        regions_map = {}
        if country_ids:
            cursor = db["countries"].find({"_id": {"$in": list(country_ids)}})
            for doc in await cursor.to_list(length=None):
                countries_map[str(doc.get("_id"))] = doc.get("name")
        if region_ids:
            cursor = db["regions"].find({"_id": {"$in": list(region_ids)}})
            for doc in await cursor.to_list(length=None):
                regions_map[str(doc.get("_id"))] = doc.get("name")

        # Inject names
        for s in states:
            for loc in s.get("location", []) or []:
                country = (loc or {}).get("country")
                if isinstance(country, dict) and country.get("id"):
                    cid = str(country["id"]) if not isinstance(country["id"], ObjectId) else str(country["id"])
                    cname = countries_map.get(cid)
                    if cname:
                        country["name"] = cname
                region = (loc or {}).get("region")
                if isinstance(region, dict) and region.get("id"):
                    rid = str(region["id"]) if not isinstance(region["id"], ObjectId) else str(region["id"])
                    rname = regions_map.get(rid)
                    if rname:
                        region["name"] = rname
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

    async def _enrich_experiences_with_activities(self, db, state: dict) -> dict:
        """Populate experiences ObjectIds with actual activity data."""
        if not state.get("experiences"):
            logger.info("No experiences found in state")
            return state
        
        experiences = state.get("experiences", {})
        logger.info(f"Enriching experiences for categories: {list(experiences.keys())}")
        # Check if activities collection exists
        collection_names = await db.list_collection_names()
        logger.info(f"Available collections: {collection_names}")
        if "activities" not in collection_names:
            logger.error("Activities collection not found in database!")
            return state
        
        activities_collection = db["activities"]
        logger.info("Activities collection found, proceeding with enrichment")
        
        # Collect all activity IDs from all experience categories
        # Also track which ones are already objects vs IDs
        all_activity_ids = []
        needs_population = {}  # category -> list of (index, activity_id_str)
        
        for category, activity_list in experiences.items():
            if isinstance(activity_list, list):
                logger.info(f"Processing category {category} with {len(activity_list)} items")
                for idx, aid in enumerate(activity_list):
                    # Check if already an object with name field
                    if isinstance(aid, dict) and aid.get("name"):
                        # Already populated, skip
                        logger.debug(f"Category {category}, index {idx}: Already populated")
                        continue
                    
                    # It's an ID (ObjectId or string), needs population
                    try:
                        activity_id = None
                        activity_id_str = None
                        
                        if isinstance(aid, ObjectId):
                            activity_id = aid
                            activity_id_str = str(aid)
                            logger.debug(f"Category {category}, index {idx}: Found ObjectId {activity_id_str}")
                        elif isinstance(aid, str) and ObjectId.is_valid(aid):
                            # String format ObjectId - convert to ObjectId for query
                            activity_id = ObjectId(aid)
                            activity_id_str = aid
                            logger.debug(f"Category {category}, index {idx}: Found string ObjectId {activity_id_str}, converted to ObjectId")
                        elif isinstance(aid, dict) and aid.get("id"):
                            aid_val = aid.get("id")
                            if isinstance(aid_val, ObjectId):
                                activity_id = aid_val
                                activity_id_str = str(aid_val)
                            elif isinstance(aid_val, str) and ObjectId.is_valid(aid_val):
                                activity_id = ObjectId(aid_val)
                                activity_id_str = aid_val
                        else:
                            logger.warning(f"Category {category}, index {idx}: Invalid activity ID format: type={type(aid)}, value={aid}")
                            continue
                        
                        if activity_id and activity_id_str:
                            all_activity_ids.append(activity_id)
                            if category not in needs_population:
                                needs_population[category] = []
                            needs_population[category].append((idx, activity_id_str))
                            logger.debug(f"Category {category}, index {idx}: Added activity ID {activity_id_str} to population list")
                    except Exception as e:
                        logger.error(f"Error processing activity ID in category {category}, index {idx}: {e}, type: {type(aid)}, value: {aid}")
                        import traceback
                        logger.error(traceback.format_exc())
                        continue
        
        if not all_activity_ids:
            # All experiences are already populated or empty
            logger.warning("No activity IDs to populate - experiences may already be populated or empty")
            logger.warning(f"Experiences structure: {list(experiences.keys())}")
            for cat, exp_list in experiences.items():
                if isinstance(exp_list, list) and len(exp_list) > 0:
                    logger.warning(f"  {cat}: {len(exp_list)} items, first item type = {type(exp_list[0])}, value = {exp_list[0]}")
            return state
        
        logger.info(f"Fetching {len(all_activity_ids)} activities for experience population")
        
        # Fetch all activities in one query
        activities_map = {}
        try:
            cursor = activities_collection.find({"_id": {"$in": all_activity_ids}})
            activity_count = 0
            async for activity in cursor:
                activity_count += 1
                activity_id = str(activity.get("_id"))
                # Get activity name (required field)
                activity_name = activity.get("name", "")
                if not activity_name:
                    # Skip activities without names
                    logger.warning(f"Activity {activity_id} has no name field, skipping")
                    continue
                
                logger.info(f"Populating activity: {activity_name} (ID: {activity_id})")
                
                # Get activity description - handle both string and object formats
                activity_description = activity.get("description", "")
                desc_short = ""
                desc_long = ""
                if isinstance(activity_description, dict):
                    desc_short = activity_description.get("short", activity_description.get("overview", ""))
                    desc_long = activity_description.get("long", desc_short)
                elif activity_description:
                    desc_short = str(activity_description)
                    desc_long = desc_short
                
                # Get activity images - handle both object and array formats
                activity_images = activity.get("images", {})
                banner_image = ""
                card_image = ""
                if isinstance(activity_images, dict):
                    banner_image = activity_images.get("banner", "") or activity_images.get("card", "")
                    card_image = activity_images.get("card", banner_image)
                elif isinstance(activity_images, list) and len(activity_images) > 0:
                    # Handle array format - could be array of strings or objects
                    first_image = activity_images[0]
                    if isinstance(first_image, dict):
                        banner_image = first_image.get("url", first_image.get("banner", first_image.get("card", "")))
                    elif isinstance(first_image, str):
                        banner_image = first_image
                    card_image = banner_image
                
                # Get type from labels if available, otherwise use category name
                activity_type = category  # Default to category name
                labels = activity.get("labels", [])
                if labels and isinstance(labels, list) and len(labels) > 0:
                    # Try to get label name
                    label_ref = labels[0]
                    if isinstance(label_ref, dict) and label_ref.get("id"):
                        label_id = label_ref.get("id")
                        try:
                            label_obj_id = ObjectId(str(label_id)) if not isinstance(label_id, ObjectId) else label_id
                            label_doc = await db["labels"].find_one({"_id": label_obj_id})
                            if label_doc and label_doc.get("name"):
                                activity_type = label_doc.get("name", category)
                        except Exception:
                            pass
                
                # Get additional activity fields
                best_time_to_do = activity.get("bestTimeToDo", "") or activity.get("bestTimeToVisit", "")
                difficulty_level = activity.get("difficultyLevel", "")
                duration = activity.get("duration", "")
                
                # Convert activity to Experience format
                activity_data = {
                    "name": activity_name,
                    "type": activity_type,
                    "description": {
                        "short": desc_short,
                        "long": desc_long
                    },
                    "images": {
                        "banner": banner_image or "/images/default.jpg",
                        "card": card_image or banner_image or "/images/default.jpg"
                    },
                    "locations": [],
                    "bestTimeToDo": best_time_to_do,
                    "difficultyLevel": difficulty_level,
                    "duration": duration
                }
                activities_map[activity_id] = activity_data
                logger.debug(f"Mapped activity {activity_id}: {activity_name}")
            
            logger.info(f"Fetched {activity_count} activities, mapped {len(activities_map)} experiences")
        except Exception as e:
            logger.exception(f"Error fetching activities: {e}")
            return state
        
        # Replace ObjectIds with populated activity data
        enriched_experiences = {}
        for category, activity_list in experiences.items():
            if isinstance(activity_list, list):
                enriched_list = []
                for aid in activity_list:
                    # If already an object with name, keep it as is
                    if isinstance(aid, dict) and aid.get("name"):
                        enriched_list.append(aid)
                        continue
                    
                    # Otherwise, try to populate from activities_map
                    try:
                        activity_id_str = None
                        if isinstance(aid, ObjectId):
                            activity_id_str = str(aid)
                        elif isinstance(aid, str) and ObjectId.is_valid(aid):
                            activity_id_str = aid
                        elif isinstance(aid, dict) and aid.get("id"):
                            aid_val = aid.get("id")
                            if isinstance(aid_val, ObjectId):
                                activity_id_str = str(aid_val)
                            elif isinstance(aid_val, str) and ObjectId.is_valid(aid_val):
                                activity_id_str = aid_val
                        
                        if activity_id_str and activity_id_str in activities_map:
                            # Add category type to the experience
                            exp_data = activities_map[activity_id_str].copy()
                            if not exp_data.get("type"):
                                exp_data["type"] = category
                            enriched_list.append(exp_data)
                            logger.debug(f"Added enriched experience: {exp_data.get('name')} to category {category}")
                        else:
                            logger.warning(f"Activity ID {activity_id_str} not found in activities_map for category {category}")
                    except Exception as e:
                        logger.warning(f"Error enriching activity in category {category}: {e}")
                        continue
                if enriched_list:
                    enriched_experiences[category] = enriched_list
        
        if enriched_experiences:
            state["experiences"] = enriched_experiences
            logger.info(f"Enriched experiences: {list(enriched_experiences.keys())} with {sum(len(v) for v in enriched_experiences.values())} total experiences")
        else:
            logger.warning("No experiences were enriched - check if activities exist in database")
        
        return state

    async def create_state(self, state_data: StateCreate) -> StateResponse:
        """Create a new state"""
        db = await get_database()
        collection = db[self.collection_name]
        
        # Check if state with same code already exists
        existing_state = await collection.find_one({"code": state_data.code})
        if existing_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"State with code '{state_data.code}' already exists"
            )
        
        # Create state model
        state_model = StateModel(**state_data.dict())
        state_dict = state_model.dict(by_alias=True, exclude={"id"})
        
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
        
        # Log experiences before enrichment - check raw MongoDB response
        if state.get("experiences"):
            logger.info(f"State experiences BEFORE enrichment: {list(state.get('experiences', {}).keys())}")
            for cat, exps in state.get("experiences", {}).items():
                if isinstance(exps, list) and len(exps) > 0:
                    first_item = exps[0]
                    logger.info(f"  {cat}: {len(exps)} items, first item type = {type(first_item)}, value = {first_item}")
                    # Check if it's an ObjectId or string
                    if isinstance(first_item, ObjectId):
                        logger.info(f"    First item is ObjectId: {first_item}")
                    elif isinstance(first_item, str):
                        logger.info(f"    First item is string: {first_item}")
                        if ObjectId.is_valid(first_item):
                            logger.info(f"    String is a valid ObjectId")
                        else:
                            logger.warning(f"    String is NOT a valid ObjectId")
                    else:
                        logger.warning(f"    First item is unexpected type: {type(first_item)}")
        
        # Enrich location names
        states = await self._enrich_locations_with_names(db, [state])
        state = states[0] if states else state
        
        # Enrich label names
        states = await self._enrich_labels_with_names(db, [state])
        state = states[0] if states else state
        
        # Enrich experiences with activity data
        logger.info("Starting experience enrichment...")
        state = await self._enrich_experiences_with_activities(db, state)
        logger.info("Experience enrichment completed")
        
        # Log experiences after enrichment for debugging
        if state.get("experiences"):
            logger.info(f"State experiences after enrichment: {list(state.get('experiences', {}).keys())}")
            for cat, exps in state.get("experiences", {}).items():
                if isinstance(exps, list):
                    logger.info(f"  {cat}: {len(exps)} experiences")
                    if len(exps) > 0:
                        first_exp = exps[0]
                        if isinstance(first_exp, dict):
                            logger.info(f"    First experience name: {first_exp.get('name', 'NO NAME')}")
        
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
        # Enrich names from referenced collections
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
        update_data = {k: v for k, v in state_data.dict().items() if v is not None}
        if update_data:
            update_data["updated_at"] = StateModel().updated_at
        
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
        collection = db[self.collection_name]
        
        state = await collection.find_one({"code": code.upper()})
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )
        state = self._convert_object_ids(state)
        if state and state.get("_id") and not state.get("id"):
            state["id"] = state["_id"]
        return StateResponse(**state)

    async def get_all_states(self) -> List[StateResponse]:
        """Get all states from the collection without pagination"""
        db = await get_database()
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
            label_object_ids = []
            for label_id in query.labels:
                if ObjectId.is_valid(label_id):
                    label_object_ids.append(ObjectId(label_id))
            
            if label_object_ids:
                if query.label_filter_type == "all":
                    filter_query["labels.id"] = {"$all": label_object_ids}
                else:  # "any" (OR logic)
                    filter_query["labels.id"] = {"$in": label_object_ids}
        
        # Get total count
        total = await collection.count_documents(filter_query)
        
        # Handle fetch_all for minimal data
        if query.fetch_all and query.template == "minimal":
            cursor = collection.find(filter_query)
            states = await cursor.to_list(length=None)
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
        
        # Enrich labels with names
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
            
            # Enrich labels with names
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
