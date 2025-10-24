"""Check referenced country/region IDs from `states` and report missing lookup documents.

Usage (cmd.exe):
    python scripts\check_location_lookups.py

It uses config.settings and MONGO_URL/DB_NAME env vars if present.
"""
import os
import sys
from bson import ObjectId
try:
    from pymongo import MongoClient
except Exception as e:
    print("pymongo is required to run this script. Install with: pip install pymongo bson")
    sys.exit(1)

from config import settings

mongodb_url = os.getenv("MONGO_URL") or settings.mongodb_url
database_name = os.getenv("DB_NAME") or settings.database_name

print(f"Using MongoDB host: {mongodb_url.split('@')[-1] if '@' in mongodb_url else mongodb_url}")
print(f"Database: {database_name}")

client = MongoClient(mongodb_url)
db = client[database_name]

states_col = db["states"]
countries_col = db["countries"]
regions_col = db["regions"]

# Collect referenced ids
country_ids = set()
region_ids = set()

for s in states_col.find({}, {"name": 1, "location": 1}):
    locs = s.get("location") or []
    for loc in locs:
        if not loc:
            continue
        country = loc.get("country")
        region = loc.get("region")
        if country:
            if isinstance(country, dict):
                cid = country.get("id")
            else:
                cid = country
            if cid:
                try:
                    country_ids.add(ObjectId(str(cid)))
                except Exception:
                    print(f"Invalid country id format in state '{s.get('name')}', value: {cid}")
        if region:
            if isinstance(region, dict):
                rid = region.get("id")
            else:
                rid = region
            if rid:
                try:
                    region_ids.add(ObjectId(str(rid)))
                except Exception:
                    print(f"Invalid region id format in state '{s.get('name')}', value: {rid}")

print(f"Found {len(country_ids)} unique referenced country IDs and {len(region_ids)} referenced region IDs from states")

present_countries = set()
if country_ids:
    for doc in countries_col.find({"_id": {"$in": list(country_ids)}}, {"_id": 1, "name": 1}):
        present_countries.add(doc.get("_id"))

present_regions = set()
if region_ids:
    for doc in regions_col.find({"_id": {"$in": list(region_ids)}}, {"_id": 1, "name": 1}):
        present_regions.add(doc.get("_id"))

missing_countries = country_ids - present_countries
missing_regions = region_ids - present_regions

print(f"Missing countries: {len(missing_countries)}")
if missing_countries:
    print("Sample missing country IDs:")
    for i, mc in enumerate(list(missing_countries)[:10], start=1):
        print(f"  {i}. {mc}")

print(f"Missing regions: {len(missing_regions)}")
if missing_regions:
    print("Sample missing region IDs:")
    for i, mr in enumerate(list(missing_regions)[:10], start=1):
        print(f"  {i}. {mr}")

# Show example states that reference missing IDs
if missing_countries or missing_regions:
    print("\nExample states referencing missing IDs:")
    for s in states_col.find({}, {"name": 1, "location": 1}):
        locs = s.get("location") or []
        for loc in locs:
            found = False
            country = loc.get("country")
            region = loc.get("region")
            if country:
                cid = country.get("id") if isinstance(country, dict) else country
                try:
                    if ObjectId(str(cid)) in missing_countries:
                        print(f"- State '{s.get('name')}' references missing country id: {cid}")
                        found = True
                except Exception:
                    pass
            if region:
                rid = region.get("id") if isinstance(region, dict) else region
                try:
                    if ObjectId(str(rid)) in missing_regions:
                        print(f"- State '{s.get('name')}' references missing region id: {rid}")
                        found = True
                except Exception:
                    pass
            if found:
                # print full location for debugging
                print(f"  location: {loc}")

print("\nDone.")

