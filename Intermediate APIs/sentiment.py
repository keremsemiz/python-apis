from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

sentiment_analysis = pipeline("sentiment-analysis")

class TextIn(BaseModel):
    text: str

class SentimentOut(BaseModel):
    label: str
    score: float

@app.post("/sentiment/", response_model=SentimentOut)
async def analyze_sentiment(text_in: TextIn):
    result = sentiment_analysis(text_in.text)[0]
    return SentimentOut(label=result['label'], score=result['score'])