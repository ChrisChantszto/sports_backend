from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

API = os.getenv('API')  # Fetch API from environment variables
client = MongoClient(API)

class SportDetails(BaseModel):
    format: Optional[str] = None
    skills_level: Optional[str] = None
    age_group: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    number_of_courts: Optional[int] = None

class SportData(BaseModel):
    zh: SportDetails
    en: SportDetails


app = FastAPI()

# initialize MongoDB client
client = MongoClient(API)
db = client['SportsApp']
collection = db['sports']


@app.get("/sports/{sport_type}")
async def get_sport_data_from_db(sport_type):
    sport_data = get_sport_data_from_db(sport_type)
    if sport_data:
        return sport_data
    else:
        raise HTTPException(status_code=404, detail="Sport type not found")
    
@app.get("/sports/{sport_type}/details", response_model=SportDetails)
async def get_sport_details(sport_type: str):
    sport_data = get_sport_data_from_db(sport_type)
    if sport_data is not None and 'en' in sport_data:
        return SportDetails(**sport_data['en'])
    else:
        raise HTTPException(status_code=404, detail="Sport not found")
    
@app.post("/sports/{sport_type}")
async def update_sports_details(sport_type: str, sport_data: SportData):
    return update_sport_data_in_db(sport_type, sport_data.model_dump())

def get_sport_data_from_db(sport_type: str) -> Optional[Dict]:
    sport_data = collection.find_one({"sport_type": sport_type})
    if sport_data:
        # convert ObjectId to str for serialization
        sport_data["_id"] = str(sport_data["_id"])
    return sport_data

def update_sport_data_in_db(sport_type: str, sport_data: Dict) -> Dict:
    result = collection.update_one({"sport_type": sport_type}, {"$set": sport_data}, upsert=True)
    return {"acknowledged": result.acknowledged, "matched_count": result.matched_count, "modified_count": result.modified_count}

