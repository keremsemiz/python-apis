from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/"

class ConversionRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: float

class ConversionResponse(BaseModel):
    from_currency: str
    to_currency: str
    original_amount: float
    converted_amount: float
    rate: float

@app.post("/convert/", response_model=ConversionResponse)
async def convert_currency(request: ConversionRequest):
    url = f"{EXCHANGE_RATE_API_URL}{request.from_currency}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Currency not found")
        data = response.json()
        if request.to_currency not in data["rates"]:
            raise HTTPException(status_code=404, detail="Target currency not found")
        rate = data["rates"][request.to_currency]
        converted_amount = request.amount * rate
        return ConversionResponse(
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            original_amount=request.amount,
            converted_amount=converted_amount,
            rate=rate
        )