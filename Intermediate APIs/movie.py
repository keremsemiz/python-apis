from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import random

app = FastAPI()

movies_db: Dict[str, List[str]] = {
    "action": ["Mad Max: Fury Road", "John Wick", "Die Hard"],
    "comedy": ["Superbad", "The Hangover", "Step Brothers"],
    "drama": ["The Shawshank Redemption", "Forrest Gump", "Fight Club"],
    "sci-fi": ["Inception", "The Matrix", "Interstellar"],
}

class MovieRequest(BaseModel):
    genres: List[str]

class MovieResponse(BaseModel):
    recommendations: List[str]

@app.post("/recommendations/", response_model=MovieResponse)
async def get_recommendations(request: MovieRequest):
    recommendations = []
    for genre in request.genres:
        if genre not in movies_db:
            raise HTTPException(status_code=404, detail=f"Genre '{genre}' not found")
        recommendations.extend(random.sample(movies_db[genre], k=min(2, len(movies_db[genre]))))
    random.shuffle(recommendations)
    return MovieResponse(recommendations=recommendations)