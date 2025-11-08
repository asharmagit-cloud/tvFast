import json
import os
import argparse
from pymongo import MongoClient, UpdateOne
from config import settings

# --- Command line argument parsing ---
parser = argparse.ArgumentParser(description="Synchronize states and labels with MongoDB")
parser.add_argument("--mongo-url", help="MongoDB connection URL")
parser.add_argument("--db-name", help="Database name")
parser.add_argument("--labels-collection", help="Labels collection name")
parser.add_argument("--states-collection", help="States collection name")
parser.add_argument("--json-file", help="Path to JSON file with states and labels")
parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
args = parser.parse_args()

# --- MongoDB connection using environment variables and command line args ---
# Priority: command line args > environment variables > config defaults
mongodb_url = args.mongo_url or os.getenv("MONGO_URL") or settings.mongodb_url
database_name = args.db_name or os.getenv("DB_NAME") or settings.database_name

# Collection and file configuration (CLI > env > defaults)
labels_collection = args.labels_collection or os.getenv("LABELS_COLLECTION") or "labels"
states_collection = args.states_collection or os.getenv("STATES_COLLECTION") or "states"
json_file_path = args.json_file or os.getenv("STATES_LABELS_JSON") or "states_with_labels.json"

# Friendly output (avoid printing credentials if present)
display_host = mongodb_url.split('@')[-1] if "@" in mongodb_url else mongodb_url
print(f"🔗 Connecting to MongoDB host: {display_host}")
print(f"📊 Using database: {database_name}")
if args.dry_run:
    print("🔍 DRY RUN MODE: No changes will be made to the database")

# --- Test MongoDB connection ---
try:
    client = MongoClient(mongodb_url)
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("Please check your MONGO_URL environment variable or config settings")
    exit(1)

# create DB and collection handles
db = client[database_name]
labels_col = db[labels_collection]
states_col = db[states_collection]

print(f"📋 Using collections: {labels_collection}, {states_collection}")

# --- Load data from JSON file ---
print(f"📁 Loading data from: {json_file_path}")

try:
    with open(json_file_path, "r", encoding="utf-8") as f:
        states_data = json.load(f)
    print(f"✅ Successfully loaded {len(states_data)} states from JSON file")
except FileNotFoundError:
    print(f"❌ Error: JSON file '{json_file_path}' not found!")
    print("Please ensure the file exists or set STATES_LABELS_JSON environment variable")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON format in '{json_file_path}': {e}")
    exit(1)
except Exception as e:
    print(f"❌ Error loading JSON file: {e}")
    exit(1)

# Example JSON format:
# [
#   {"name": "Maharashtra", "labels": ["Culture", "Heritage", "Beaches", "Modern City"]},
#   {"name": "Rajasthan", "labels": ["Desert", "Culture", "Royalty", "Heritage"]}
# ]

# --- STEP 1: Collect all unique labels ---
all_labels = {label for state in states_data for label in state["labels"]}

# --- STEP 2: Fetch existing labels and map by name ---
try:
    existing_labels = {lbl["name"]: lbl["_id"] for lbl in labels_col.find({}, {"name": 1})}
    print(f"📊 Found {len(existing_labels)} existing labels in database")
except Exception as e:
    print(f"❌ Error fetching existing labels: {e}")
    exit(1)

# --- STEP 3: Find missing labels ---
missing_labels = list(all_labels - set(existing_labels.keys()))
print(f"🔍 Missing labels to insert: {len(missing_labels)}")

# --- STEP 4: Insert missing labels and update map ---
if missing_labels:
    if args.dry_run:
        print(f"🔍 DRY RUN: Would insert {len(missing_labels)} new labels: {missing_labels}")
        # For dry run, simulate the labels being inserted
        for lbl in missing_labels:
            existing_labels[lbl] = f"simulated_id_for_{lbl}"
    else:
        try:
            new_label_docs = [{"name": lbl} for lbl in missing_labels]
            insert_result = labels_col.insert_many(new_label_docs)
            for lbl, _id in zip(missing_labels, insert_result.inserted_ids):
                existing_labels[lbl] = _id
            print(f"✅ Successfully inserted {len(missing_labels)} new labels")
        except Exception as e:
            print(f"❌ Error inserting new labels: {e}")
            exit(1)

print(f"✅ Total labels: {len(existing_labels)} (Inserted {len(missing_labels)} new)")

# --- STEP 5: Prepare bulk update operations for states ---
bulk_ops = []
for state in states_data:
    # Build label objects matching RefId schema: {id: ObjectId, name: <label-name>}
    label_objs = []
    missing_in_map = []
    for lbl in state.get("labels", []):
        if lbl not in existing_labels:
            missing_in_map.append(lbl)
            continue
        label_objs.append({"id": existing_labels[lbl], "name": lbl})

    if missing_in_map:
        print(f"⚠️ Warning: state '{state.get('name')}' references unknown labels: {missing_in_map}")

    bulk_ops.append(
        UpdateOne(
            {"name": state["name"]},
            {"$set": {"labels": label_objs}},
            upsert=True
        )
    )

# --- STEP 6: Execute bulk update ---
if bulk_ops:
    if args.dry_run:
        print(f"🔍 DRY RUN: Would perform {len(bulk_ops)} bulk operations on states")
        for i, op in enumerate(bulk_ops[:3]):  # Show first 3 operations as examples
            print(f"  Operation {i+1}: Update state '{op._filter['name']}' with {len(op._doc['$set']['labels'])} labels")
        if len(bulk_ops) > 3:
            print(f"  ... and {len(bulk_ops) - 3} more operations")
    else:
        try:
            result = states_col.bulk_write(bulk_ops)
            print(f"✅ States upserted: {result.upserted_count}, modified: {result.modified_count}")
        except Exception as e:
            print(f"❌ Error updating states: {e}")
            exit(1)
else:
    print("⚠️ No bulk operations to perform")

print("🎯 All states and labels are now synchronized successfully!")
