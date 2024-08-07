from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import hashlib

app = FastAPI()

url_store: Dict[str, str] = {}

class URLRequest(BaseModel):
    url: str

class URLResponse(BaseModel):
    original_url: str
    shortened_url: str

def shorten_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:6]

@app.post("/shorten/", response_model=URLResponse)
async def shorten(request: URLRequest):
    short_url = shorten_url(request.url)
    url_store[short_url] = request.url
    return URLResponse(original_url=request.url, shortened_url=f"/{short_url}")

@app.get("/{short_url}", response_model=URLResponse)
async def resolve(short_url: str):
    if short_url not in url_store:
        raise HTTPException(status_code=404, detail="URL not found")
    return URLResponse(original_url=url_store[short_url], shortened_url=f"/{short_url}")