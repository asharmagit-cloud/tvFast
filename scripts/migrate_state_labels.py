"""Migrate state documents whose `labels` field is an array of ObjectId
into the project's RefId format: [{"id": ObjectId, "name": <label-name>}].

Usage (cmd.exe):
    python scripts\migrate_state_labels.py --dry-run
    python scripts\migrate_state_labels.py        # perform changes

The script uses (in order): --mongo-url, MONGO_URL env var, or config.settings.mongodb_url
and --db-name, DB_NAME env var, or config.settings.database_name.

It will print a summary and perform bulk updates in batches.
"""

import argparse
import os
from pymongo import MongoClient, UpdateOne
from bson import ObjectId
from config import settings

parser = argparse.ArgumentParser(description="Migrate state label arrays to RefId objects")
parser.add_argument("--mongo-url", help="MongoDB connection URL")
parser.add_argument("--db-name", help="Database name")
parser.add_argument("--labels-collection", default="labels", help="Labels collection name")
parser.add_argument("--states-collection", default="states", help="States collection name")
parser.add_argument("--batch-size", type=int, default=100, help="Number of docs to update per bulk operation")
parser.add_argument("--dry-run", action="store_true", help="Show planned updates without applying them")
args = parser.parse_args()

mongodb_url = args.mongo_url or os.getenv("MONGO_URL") or settings.mongodb_url
database_name = args.db_name or os.getenv("DB_NAME") or settings.database_name
labels_collection = args.labels_collection
states_collection = args.states_collection

print(f"Using MongoDB host: {mongodb_url.split('@')[-1] if '@' in mongodb_url else mongodb_url}")
print(f"Database: {database_name}, states collection: {states_collection}, labels collection: {labels_collection}")
if args.dry_run:
    print("DRY RUN: no changes will be made")

client = MongoClient(mongodb_url)
db = client[database_name]
labels_col = db[labels_collection]
states_col = db[states_collection]

# Find states where labels.0 is an ObjectId (i.e., labels is an array of ObjectId)
query = {"labels.0": {"$type": "objectId"}}

cursor = states_col.find(query, {"labels": 1, "name": 1})
ops = []
count = 0
preview_limit = 10

for doc in cursor:
    state_id = doc.get("_id")
    state_name = doc.get("name")
    label_ids = doc.get("labels", [])
    # Build label objects by looking up label names
    label_objs = []
    missing = []
    for lid in label_ids:
        if not isinstance(lid, ObjectId):
            # unexpected type, skip
            continue
        lbl_doc = labels_col.find_one({"_id": lid}, {"name": 1})
        if lbl_doc:
            label_objs.append({"id": lid, "name": lbl_doc.get("name")})
        else:
            label_objs.append({"id": lid, "name": None})
            missing.append(str(lid))

    if not label_objs:
        continue

    update_op = UpdateOne({"_id": state_id}, {"$set": {"labels": label_objs}})
    ops.append((state_id, state_name, label_ids, label_objs, missing, update_op))
    count += 1

# Summary
print(f"Found {count} state documents with labels stored as raw ObjectId arrays.")
if count == 0:
    print("Nothing to do.")
    exit(0)

# Show a preview
print("Samples:")
for i, (sid, sname, old_ids, new_objs, missing, _) in enumerate(ops[:preview_limit], start=1):
    print(f"{i}. {sname} ({sid}) -> {len(old_ids)} labels, missing_label_names: {missing}")

if args.dry_run:
    print("DRY RUN complete. No changes applied.")
    exit(0)

# Perform bulk updates in batches
bulk = []
applied = 0
for i, (_, _, _, _, _, op) in enumerate(ops, start=1):
    bulk.append(op)
    if len(bulk) >= args.batch_size:
        result = states_col.bulk_write(bulk)
        applied += result.modified_count + result.upserted_count
        print(f"Applied batch: modified={result.modified_count}, upserted={result.upserted_count}")
        bulk = []

# final batch
if bulk:
    result = states_col.bulk_write(bulk)
    applied += result.modified_count + result.upserted_count
    print(f"Applied final batch: modified={result.modified_count}, upserted={result.upserted_count}")

print(f"Migration complete. Documents updated: {applied}")

