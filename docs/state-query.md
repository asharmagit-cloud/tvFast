State query implementation notes

Purpose

This document describes the query contract and implementation details used by `controllers/state_controller.py`. Use it as a reference to implement the same flexible query logic for other collections (for example, `cities` and `places`). It explains input shapes, DB filters, projection rules, pagination and fetch-all behavior, enrichment of referenced documents (labels, countries, regions), error handling, and recommended tests and optimizations.

Contract (inputs / outputs)

- Input: a query object (two supported formats in the codebase):
  - Legacy: page/limit/template/search/labels/label_filter_type/fetch_all (used by `query_states`)
  - New: filter object with fields { id: [..], view: "minimal"|"full", ... }, plus offset/size or fetch_all (used by `query_states_new`)
- Output: StateQueryResponse (or list / StateListResponse) with:
  - states: list of response models (StateResponse or StateMinimalResponse)
  - pagination metadata: total, page, limit (or size), total_pages, has_next, has_prev, next_count
- Error modes:
  - 400 Bad Request for invalid IDs or invalid input
  - 500 Internal Server Error for DB connection failure or unexpected exceptions

Key concepts and mapping to DB

- Collection name: `states` (for cities/places use `cities` / `places` respectively)
- Document id field: MongoDB `_id` (ObjectId)
- Label references are stored as arrays of objects: `{ "id": ObjectId("...") }` (controller expects `labels` to be an array of dicts)
- Locations: `location` items may contain `country` and `region`. They can be stored as nested dict `{ "id": ObjectId(...) }` or as a raw id value. The enrichment helpers normalize these.

Filter semantics (what you should implement for cities/places)

1. ID filtering
   - Accept an array of string IDs in the request (for new query format) or a single `id` (legacy). Validate with ObjectId.is_valid.
   - For special token like `"t_all"` treat as no ID filtering and return all records.
   - Convert valid ids to ObjectId and filter with `_id: { $in: [ ... ] }`.

2. Search text
   - Use case-insensitive regex over one or more string fields (example: `name`, or `tagLine`).
   - Example filter: `{ $or: [ { name: { $regex: "...", $options: "i" } }, ... ] }`.

3. Label filtering
   - Input: `labels` array of label ids and `label_filter_type` = `all` | `any`.
   - `all` => `{ "labels.id": { "$all": [ObjectId(...), ...] } }` (documents must contain all label ids)
   - `any` => `{ "labels.id": { "$in": [ObjectId(...), ...] } }` (documents with at least one label id)
   - For performance, ensure `labels.id` is indexed.

4. View/template
   - `minimal` or `full` (or other templates). When `minimal` is requested, use a projection to return only selected fields (for states: `_id`, `name`, `tagLine`, `labels`, `images`). This reduces network payload and processing.

Pagination + fetch_all

- Two common pagination approaches in the repo:
  - Legacy page/limit: page is 1-based. skip = (page - 1) * limit
  - New offset/size: offset is skip (0-based), size is limit
- `fetch_all` flag
  - When `fetch_all` is true: ignore pagination and return all matching documents (or for minimal view return them in one page). Be careful — this may return a large result set.
  - Implementation sets skip=0 and limit=total (or uses cursor.to_list(length=None) when appropriate).

Projection

- Use projection only when template/view == `minimal` to limit fields. Example projection:
  { "_id": 1, "name": 1, "tagLine": 1, "labels": 1, "images": 1 }

Enrichment helpers (recommended, shareable)

- Purpose: replace cross-collection ObjectId references with friendly names for API responses (e.g., labels -> label names, countries/regions -> names).
- Suggested helper signatures (async):
  - async def _enrich_labels_with_names(db, docs: List[dict]) -> List[dict]
  - async def _enrich_locations_with_names(db, docs: List[dict]) -> List[dict]
- Implementation outline:
  - Collect unique referenced ObjectIds for the target reference collection (labels/countries/regions).
  - Query the referenced collection once with `$in` on `_id` to fetch id->name map.
  - Walk the input documents and inject `name` where applicable.
  - Keep these helpers generic and reuse them for cities and places (they will likely call different referenced collections).

Error handling and DB guard

- After obtaining a DB client via `db = await get_database()` always check `if db is None:` and raise a 500 HTTPException with a clear message (example: "Failed to obtain database connection").
- Validate ObjectId strings using `ObjectId.is_valid(id)` before converting/using them. For invalid ID inputs return 400.

Metadata calculation (pagination)

Given total, skip and limit:
- page = (skip // limit) + 1 if limit > 0 else 1
- total_pages = (total + limit - 1) // limit if limit > 0 else 0
- has_next = (skip + limit) < total
- has_prev = skip > 0
- next_count = max(0, min(limit, total - (skip + limit))) if has_next else 0

Note: when using legacy page/limit calculation, skip = (page - 1) * limit.

Type handling: ObjectId -> str

- After fetching docs from Mongo, convert ObjectId instances to strings for JSON serialization. Provide a small recursive function like `_convert_object_ids(obj)` which:
  - returns str(obj) for ObjectId
  - recurses into lists and dicts

Testing guidance

- Add tests that cover:
  - ID filtering (valid and invalid ids)
  - Label filtering (both `all` and `any` semantics)
  - Minimal view projection and full view
  - Pagination: first page, middle page, last page, page beyond range
  - fetch_all behavior
  - DB guard: mock `get_database()` to return `None` and assert HTTP 500
- For integration tests consider spinning a test MongoDB instance (or mocking Motor / DB) and running queries against sample documents.

Performance and operational notes

- count_documents(filter) is used to compute `total`. For very large collections or complex filters this may be slow. Consider:
  - Using estimated_document_count() when exact total is not required.
  - Caching counts for common queries.
  - Using cursor-based pagination if deep pagination becomes an issue.
- Ensure indexes exist on frequently filtered fields: `name`, `code`, `labels.id`, `state_id`, `city_id`.

Adapting for `cities` and `places`

1. collection name
   - Swap `self.collection_name = "states"` to `"cities"` or `"places"`.

2. Filter mapping
   - Cities often need to support filtering by `state_id` (e.g., return all cities for a given state). Accept state id(s) similar to label id handling. Use `ObjectId` validation.
   - Places may need to filter by `city_id`, `state_id`, `labels`, `experiences` etc. Map input filter keys to the collection fields.

3. Enrichment differences
   - Cities will enrich `state_id` into state name (use `states` collection) and may enrich labels similar to states.
   - Places may enrich `city`, `state`, `labels`, and referenced `experiences`.

4. Projections
   - Define what `minimal` means per resource. Example for cities: `_id`, `name`, `state_id`, `images`.

5. Pagination & fetch_all
   - Use the same offset/size or page/limit logic.

Example request payloads

Legacy (used by query_states):
{
  "page": 1,
  "limit": 10,
  "template": "minimal",   // or "full"
  "search": "north",
  "labels": ["64f...", "65a..."],
  "label_filter_type": "any",
  "fetch_all": false
}

New (used by query_states_new):
{
  "offset": 0,
  "size": 50,
  "fetch_all": false,
  "filter": {
    "id": ["t_all"],            // or specific ids
    "view": "minimal",
    "labels": ["64f...", "65a..."]
  }
}

Controller function signature suggestions

- async def query_items(self, query: StateQueryRequest) -> StateQueryResponse
- async def query_items_new(self, query: StateQueryRequest) -> StateQueryResponse

Implementation checklist (copyable)

- [ ] Validate db: call `db = await get_database()` and raise 500 if None.
- [ ] Validate and convert ids using `ObjectId.is_valid`.
- [ ] Build `filter_query` for Mongo using $in/$all/$or as required.
- [ ] Get `total = await collection.count_documents(filter_query)`.
- [ ] Compute skip/limit from page/limit or offset/size (or use fetch_all).
- [ ] Apply projection for `minimal` view.
- [ ] Retrieve docs with find(filter, projection).skip(skip).limit(limit).
- [ ] Enrich docs using shared helpers (labels / locations / states / cities).
- [ ] Convert ObjectId instances to strings before returning.
- [ ] Build and return pagination metadata.

If you want, I can now:
- Create a shared utility helper (e.g., `utils/query_helpers.py`) with common functions (db guard, enrich helpers, id conversion) and update the `cities` and `places` controllers to reuse them.
- Or, implement a `cities` controller stub using these rules so you can see the pattern.

Let me know which follow-up action you prefer and I'll implement it next.
