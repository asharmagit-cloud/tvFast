import os
from dotenv import load_dotenv
import pandas as pd
from pymongo import MongoClient
import re

# Load environment from .env in project root
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGO_URL")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI or MONGO_URL not set. Create a .env file with MONGO_URI=<your-uri> or MONGO_URL=<your-uri> at the project root.")

client = MongoClient(MONGO_URI)
# Use DB_NAME from env if present, otherwise default to 'travhoo'
DB_NAME = os.getenv("DB_NAME") or os.getenv("DATABASE") or 'travhoo'

# Use the configured database name explicitly
db = client.get_database(DB_NAME)
labels_col = db['labels']
cities_col = db['cities']

# Load Excel
excel_file = "cities.xlsx"
try:
    df = pd.read_excel(excel_file)
except FileNotFoundError:
    raise FileNotFoundError(f"Excel file not found: {excel_file}. Put the file in the project root or update the path.")

# Clean and process each city row
for idx, row in df.iterrows():
    city_name = str(row.get('City', '') or row.get('cities', '')).strip()
    print(city_name)
    if not city_name:
        # log each city with empty name in json file
        print(f"Skipping row {idx} because City is empty")
        continue
    # If city not present in the cities collection, record it to a JSON file
    json = __import__('json')
    try:
        city_doc = cities_col.find_one({"name": city_name})
    except Exception:
        city_doc = None
    if not city_doc:
        missing_file = "missing_cities.json"
        try:
            with open(missing_file, "r", encoding="utf-8") as f:
                try:
                    missing = json.load(f)
                except Exception:
                    missing = []
        except FileNotFoundError:
            missing = []
        if city_name not in missing:
            missing.append(city_name)
            with open(missing_file, "w", encoding="utf-8") as f:
                json.dump(missing, f, ensure_ascii=False, indent=2)
        print(f'City not found in DB, logged to {missing_file}: {city_name}')

    # Support labels column named 'Labels' or 'labels'
    raw_labels = str(row.get('Labels', '') or row.get('labels', '') or '')
    # Split on '|' or ',' with optional surrounding whitespace
    label_names = [lbl.strip() for lbl in re.split(r"\s*\|\s*|\s*,\s*", raw_labels) if lbl.strip()]

    label_ids_objs = []

    for label_name in label_names:
        label_doc = labels_col.find_one({"name": label_name})
        if label_doc:
            # store ObjectId directly so DB documents keep $oid representation
            label_ids_objs.append({'id': label_doc['_id']})
        else:
            print(f"Label not found in DB: {label_name}")

    if label_ids_objs:
        # Update cities collection, appending or setting labels array
        res = cities_col.update_one(
            {"name": city_name},
            {"$set": {"labels": label_ids_objs}}
        )
        if res.matched_count:
            print(f'Updated {city_name} with labels: {label_names}')
        else:
            print(f'No city matched with name "{city_name}"; skipping update')
    else:
        print(f'No matching labels found for city: {city_name}')

print("Done updating cities collection.")
