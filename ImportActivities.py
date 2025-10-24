import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import sys
import argparse

# Load .env if present
load_dotenv()

# CLI args to override defaults
parser = argparse.ArgumentParser(description="Import activities from Excel into MongoDB")
parser.add_argument("--file", "-f", help="Path to Excel file", default=os.getenv("ACTIVITIES_EXCEL", "importExperiences.xlsx"))
parser.add_argument("--db", "-d", help="Mongo database name", default=os.getenv("MONGO_DB", "travhoo"))
parser.add_argument("--collection", "-c", help="Mongo collection name", default=os.getenv("MONGO_COLLECTION", "activities"))
args = parser.parse_args()

EXCEL_PATH = args.file
DB_NAME = args.db
COLLECTION_NAME = args.collection

# Read MONGO_URL from environment
mongo_url = os.getenv("MONGO_URL")
if not mongo_url:
    print("Error: MONGO_URL environment variable not set. Please set it in your environment or .env file.")
    sys.exit(1)

# Connect to MongoDB with basic error handling
try:
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    # trigger server selection
    client.admin.command('ping')
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)

# Use specified database/collection
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Label mapping (keep provided ObjectIds)
label_map = {
    "Adventure": ObjectId("68d90c36fc0c58520c6cf20d"),
    "Historical": ObjectId("68e5e54021c4af9b4a754983"),
    "Cultural": ObjectId("68e5e54021c4af9b4a754986"),
    "Nature": ObjectId("68e5e54021c4af9b4a754987"),
    "Food": ObjectId("68f1c03170888f8a3ddf2ef8"),
    "Spiritual": ObjectId("68f1c03170888f8a3ddf2efc"),
    "Activities": ObjectId("68f389c75b1a905ca48c898e"),
    "Others": ObjectId("68f389ff5b1a905ca48c898f")
}

# Load Excel
if not os.path.exists(EXCEL_PATH):
    print(f"Error: Excel file not found at {EXCEL_PATH}")
    sys.exit(1)

try:
    df = pd.read_excel(EXCEL_PATH)
except Exception as e:
    print(f"Error reading Excel file: {e}")
    sys.exit(1)

# Expected columns - try to be flexible
required_columns = ["activity_name", "description", "Experience Type", "best_season", "state", "city"]
missing = [c for c in required_columns if c not in df.columns]
if missing:
    print(f"Warning: Missing expected columns in Excel: {missing}. The script will attempt to continue when possible.")

# Transform and insert
records = []
for idx, row in df.iterrows():
    label_name = None
    # try multiple column names for label
    for col in ("Experience Type", "experience_type", "label", "category"):
        if col in df.columns and pd.notna(row.get(col)):
            label_name = str(row.get(col)).strip()
            break

    label_id = label_map.get(label_name, label_map["Others"]) if label_name else label_map["Others"]

    name = row.get("activity_name") or row.get("name") or row.get("Activity") or None
    description = row.get("description") or row.get("Description") or ""
    best_season = row.get("best_season") or row.get("bestSeason") or ""
    state = row.get("state") or row.get("State") or ""
    city = row.get("city") or row.get("City") or ""

    if not name:
        print(f"Skipping row {idx} because it lacks a name/title")
        continue

    record = {
        "name": str(name).strip(),
        "description": description if pd.notna(description) else "",
        "tips": [],
        "images": [],
        "difficultyLevel": "",
        "duration": "",
        "bestTimeToDo": best_season if pd.notna(best_season) else "",
        "labels": [{"id": label_id}],
        "notes": f"State: {state}, City: {city}",
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc)
    }
    records.append(record)

if records:
    try:
        result = collection.insert_many(records)
        print(f"Inserted {len(result.inserted_ids)} records into {DB_NAME}.{COLLECTION_NAME}.")
    except Exception as e:
        print(f"Error inserting records: {e}")
        sys.exit(1)
else:
    print("No records to insert.")