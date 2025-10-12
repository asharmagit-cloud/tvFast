from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import re
import os
load_dotenv()  # Loads variables from .env

# import the value from MONGO_URL environment variable
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
#check for connection error
try:
    client.admin.command('ping')
    #print("Connected to MongoDB")
    #exit(0)
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)


db = client["travhoo"]

df = pd.read_excel("Activities.xlsx")

for _, row in df.iterrows():

    state = db.states.find_one({"name": re.compile(f"^{row['State']}$", re.IGNORECASE)})

    city = db.cities.find_one({"name": re.compile(f"^{row['City']}$", re.IGNORECASE)})
    print(city)
    exit(0)
    label = db.labels.find_one({"name": re.compile(f"^{row['Type']}$", re.IGNORECASE)})

    activity = {
        "name": row["Activity Name"],
        "description": row["Description"],
        "tips": [],
        "images": [],
        "difficultyLevel": "",
        "duration": "",
        "bestTimeToDo": row["Best Season"],
        "labels": [{"id": label["_id"]}] if label else [],
        "stateId": state["_id"] if state else None,
        "cityId": city["_id"] if city else None,
        "averageCost": row["Average Cost"],
        "createdAt": pd.Timestamp.now().to_pydatetime(),
        "updatedAt": pd.Timestamp.now().to_pydatetime()
    }

    db.activities.insert_one(activity)
