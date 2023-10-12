# This is a sample Python script.
import uuid
# from bson import ObjectId
from typing import List

import motor.motor_asyncio
from fastapi import FastAPI, Body, HTTPException, status, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter(
    prefix='/scores',
    tags=['scores']
)

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


MONGODB_URL = "mongodb+srv://micahehrlich:75BCD1532@cluster0.zwcgc8w.mongodb.net/?retryWrites=true&w=majority"
app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.college


class UserScoreModel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    score: int = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "name": "Mike",
                "score": "120"
            }
        }


@router.post("/", response_description="Add new score", response_model=UserScoreModel)
async def create_user_score(user_score: UserScoreModel = Body(...)):
    user_score_row = jsonable_encoder(user_score)
    new_user_score = await db["scores"].insert_one(user_score_row)
    created_user_score = await db["scores"].find_one({"_id": new_user_score.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user_score)


@router.get(
    "/", response_description="List all scores", response_model=List[UserScoreModel]
)
async def list_scores():
    scores = await db["scores"].find().to_list(1000)
    score_list = []
    for row in scores:
        score_list.append({'id': str(row['_id']), 'name': row['name'], 'score': row['score']})
    return score_list


@router.get(
    "/{id}", response_description="Get a single score", response_model=UserScoreModel
)
async def show_score(id: str):
    if (user_score := await db["scores"].find_one({"_id": id})) is not None:
        return user_score

    raise HTTPException(status_code=404, detail=f"User score {id} not found")

app.include_router(router)


