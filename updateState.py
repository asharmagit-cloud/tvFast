"""
updateState.py

Scans the `activities` collection, extracts State from activity.notes (pattern `State: <stateName>`), resolves labels via the `labels` collection, builds an `experiences` mapping like

  experiences: { "Food": [ObjectId(...), ...], "Nature": [...], ... }

and updates the matching state document in `states` by adding each activity id into the appropriate array under `experiences.<labelName>`.

Usage:
  python updateState.py              # dry-run: prints intended updates
  python updateState.py --apply      # actually applies updates to DB
  python updateState.py --limit 100  # process first 100 activities

Environment:
  MONGO_URL  (required)
  MONGO_DB   (optional, defaults to travhoo)

The script is defensive about label formats (ObjectId, {$oid: '...'}, string) and activity.labels being JSON string or list.
"""

import os
import re
import json
import argparse
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from typing import Any
from urllib.parse import urlparse

# Load .env if present
load_dotenv()

# CLI
parser = argparse.ArgumentParser(description="Update states.experiences from activities collection")
parser.add_argument("--apply", action="store_true", help="Apply updates to DB. Default is dry-run (no changes).")
parser.add_argument("--limit", type=int, default=0, help="Limit number of activities processed; 0 = all")
parser.add_argument("--skip", type=int, default=0, help="Skip this many activities before processing")
parser.add_argument("--db", default=os.getenv("MONGO_DB", "travhoo"), help="MongoDB database name (default: travhoo)")
parser.add_argument("--url", default=os.getenv("MONGO_URL"), help="MongoDB connection URL (or set MONGO_URL env)")
parser.add_argument("--report", default=None, help="Path to JSON report file to write operation details")
args = parser.parse_args()

MONGO_URL = args.url
DB_NAME = args.db
APPLY = args.apply
LIMIT = args.limit
SKIP = args.skip
REPORT_PATH = args.report

if not MONGO_URL:
    print("Error: MONGO_URL not set. Provide via environment or --url")
    raise SystemExit(1)

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise SystemExit(1)

# Ensure `db` is defined before proceeding
db = client[DB_NAME]

# Helper to mask the URL for printing
def mask_url(url: str) -> str:
    try:
        p = urlparse(url)
        host = p.hostname or ''
        port = f":{p.port}" if p.port else ''
        return f"{p.scheme}://{host}{port}{p.path or ''}"
    except Exception:
        return (url[:60] + '...') if url and len(url) > 60 else url

# Print connection info so user can verify which DB was used
print(f"Connecting to: {mask_url(MONGO_URL)}")
print(f"Database: {DB_NAME}, apply={APPLY}, limit={LIMIT}, skip={SKIP}")

activities_coll = db.get_collection("activities")
labels_coll = db.get_collection("labels")
states_coll = db.get_collection("states")

state_pattern = re.compile(r"State:\s*([^,\n]+)", re.IGNORECASE)

def sanitize_label_key(name: str) -> str:
    """Return a Mongo-safe field name for a label.
    Replaces dots and whitespace, removes leading $ and other non-alphanumeric/underscore characters.
    """
    if name is None:
        return "unknown_label"
    s = str(name).strip()
    # remove leading $ which is invalid for field names
    while s.startswith('$'):
        s = s[1:]
    # replace dots and whitespace with underscores
    s = s.replace('.', '_')
    s = re.sub(r"\s+", "_", s)
    # keep only alnum and underscore
    s = re.sub(r"[^A-Za-z0-9_]", "", s)
    if not s:
        return "unknown_label"
    return s


def extract_state_from_notes(notes: Any) -> str | None:
    if not notes:
        return None
    if not isinstance(notes, str):
        try:
            notes = str(notes)
        except Exception:
            return None
    m = state_pattern.search(notes)
    if not m:
        return None
    return m.group(1).strip()


def normalize_label_entries(labels_field: Any) -> list:
    """Return list of label dicts in normalized form. Accepts:
       - list of dicts: [{'id': ObjectId(...)}, ...]
       - JSON string representing the list
       - other shapes
    """
    if labels_field is None:
        return []
    # If already a list
    if isinstance(labels_field, list):
        return labels_field
    # If it's a dict (single label), wrap
    if isinstance(labels_field, dict):
        return [labels_field]
    # If string: try to parse JSON
    if isinstance(labels_field, str):
        # Try raw json
        try:
            parsed = json.loads(labels_field)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return [parsed]
        except Exception:
            # Not JSON - nothing to do
            return []
    # Unknown type
    return []


def extract_label_id(label_entry: Any) -> str | None:
    """Extract a string ObjectId from various label entry shapes.
       Examples:
        - {'id': ObjectId('...')}
        - {'id': {'$oid': '...'}}
        - {'id': '...'}
        - ObjectId('...')
    """
    if label_entry is None:
        return None
    # If label_entry is an ObjectId itself
    if isinstance(label_entry, ObjectId):
        return str(label_entry)
    # If it's a dict and has 'id'
    if isinstance(label_entry, dict) and 'id' in label_entry:
        lid = label_entry['id']
        if isinstance(lid, ObjectId):
            return str(lid)
        if isinstance(lid, dict) and '$oid' in lid:
            return str(lid['$oid'])
        if isinstance(lid, str):
            return lid
    # If entry has '$oid' at top level
    if isinstance(label_entry, dict) and '$oid' in label_entry:
        return str(label_entry['$oid'])
    # If it's a string, treat as id
    if isinstance(label_entry, str):
        return label_entry
    return None


def resolve_label_name(label_id_str: str) -> str | None:
    try:
        lbl = labels_coll.find_one({"_id": ObjectId(label_id_str)})
        if lbl:
            # common name fields
            return lbl.get('name') or lbl.get('label') or lbl.get('title')
    except Exception:
        # label_id_str might not be a valid ObjectId -- fallback try by string name
        lbl = labels_coll.find_one({"name": label_id_str})
        if lbl:
            return lbl.get('name')
    return None


def process_activity(activity_doc):
    notes = activity_doc.get('notes') or ''
    state_name = extract_state_from_notes(notes)
    if not state_name:
        return (False, f"No state found in notes for activity {activity_doc.get('_id')}")

    # parse labels
    labels_field = activity_doc.get('labels')
    labels_list = normalize_label_entries(labels_field)

    experiences = {}
    for lab in labels_list:
        label_id = extract_label_id(lab)
        if not label_id:
            # try if lab has 'name' directly
            lab_name = None
            if isinstance(lab, dict):
                lab_name = lab.get('name') or lab.get('label')
            if lab_name:
                key = sanitize_label_key(lab_name)
                experiences.setdefault(key, []).append(activity_doc.get('_id'))
            continue
        lab_name = resolve_label_name(label_id)
        if not lab_name:
            # if label doc not found, try use id as fallback name
            lab_name = label_id
        key = sanitize_label_key(lab_name)
        experiences.setdefault(key, []).append(activity_doc.get('_id'))

    if not experiences:
        return (False, f"No labels resolved for activity {activity_doc.get('_id')}")

    # Build update operations: for each label name, addToSet the activity id into experiences.<labelName>
    update_ops = {}
    for label_name, ids in experiences.items():
        # Use $each with $addToSet to add unique elements
        update_ops.setdefault('$addToSet', {})[f"experiences.{label_name}"] = {"$each": ids}

    # Ensure state document exists; if not, create it with experiences
    state_doc = states_coll.find_one({"name": state_name})
    # try case-insensitive match if exact match failed
    if not state_doc:
        try:
            ci = states_coll.find_one({"name": {"$regex": f"^{re.escape(state_name)}$", "$options": "i"}})
            if ci:
                state_doc = ci
        except Exception:
            pass
    if not state_doc:
        # create state document
        if APPLY:
            # Insert using sanitized keys already present in `experiences`
            # res = states_coll.insert_one({"name": state_name, "experiences": experiences})
            return (True, f"Created state {state_name} with experiences (inserted_id={res.inserted_id})")
        else:
            return (True, f"Would create state {state_name} with experiences: {experiences}")

    # Apply update
    if APPLY:
        try:
            res = states_coll.update_one({"_id": state_doc['_id']}, update_ops)
            # If matched_count is 0, warn the user (unexpected)
            if res.matched_count == 0:
                return (False, f"Update affected 0 documents for state {state_name} (ops: {update_ops})")
            return (True, f"Updated state {state_name} (matched={res.matched_count}, modified={res.modified_count})")
        except Exception as e:
            return (False, f"Failed to update state {state_name}: {e}")
    else:
        return (True, f"Would update state {state_name} with ops: {update_ops}")


def main():
    query = {}
    cursor = activities_coll.find(query).skip(SKIP)
    if LIMIT > 0:
        cursor = cursor.limit(LIMIT)

    total = cursor.count() if hasattr(cursor, 'count') else None
    processed = 0
    success = 0
    failures = 0
    report_entries = []

    for activity in cursor:
        processed += 1
        ok, msg = process_activity(activity)
        if ok:
            success += 1
            print("✅", msg)
            report_entries.append({"activity_id": str(activity.get('_id')), "ok": True, "msg": msg})
        else:
            failures += 1
            print("⚠️", msg)
            report_entries.append({"activity_id": str(activity.get('_id')), "ok": False, "msg": msg})

    print(f"\nDone. Processed: {processed}, Successes: {success}, Failures: {failures}")

    if REPORT_PATH:
        try:
            with open(REPORT_PATH, 'w', encoding='utf-8') as f:
                json.dump({"processed": processed, "successes": success, "failures": failures, "entries": report_entries}, f, default=str, indent=2)
            print(f"Report written to {REPORT_PATH}")
        except Exception as e:
            print(f"Failed to write report to {REPORT_PATH}: {e}")


if __name__ == '__main__':
    print(f"Connected to DB: {DB_NAME} (apply={APPLY})")
    main()
