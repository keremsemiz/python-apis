from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class User(BaseModel):
    id: str
    name: str

class FollowAction(BaseModel):
    follower_id: str
    followee_id: str

users_db = {}
followers_db = {}

@app.post("/users/", response_model=User)
async def create_user(user: User):
    users_db[user.id] = user.dict()
    followers_db[user.id] = {"following": [], "followers": []}
    return user

@app.post("/follow/")
async def follow_user(action: FollowAction):
    if action.follower_id not in users_db or action.followee_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    followers_db[action.follower_id]["following"].append(action.followee_id)
    followers_db[action.followee_id]["followers"].append(action.follower_id)
    return {"status": "success"}

@app.post("/unfollow/")
async def unfollow_user(action: FollowAction):
    if action.follower_id not in users_db or action.followee_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    followers_db[action.follower_id]["following"].remove(action.followee_id)
    followers_db[action.followee_id]["followers"].remove(action.follower_id)
    return {"status": "success"}

@app.get("/users/{user_id}/followers/", response_model=List[str])
async def get_followers(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return followers_db[user_id]["followers"]

@app.get("/users/{user_id}/following/", response_model=List[str])
async def get_following(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return followers_db[user_id]["following"]