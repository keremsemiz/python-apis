from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import httpx
import asyncio

app = FastAPI()

API_KEY = "x147!hekcnw82656741x"
BASE_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={apikey}"

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

async def get_stock_price(symbol: str):
    url = BASE_URL.format(symbol=symbol, apikey=API_KEY)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        try:
            price = list(data["Time Series (1min)"].values())[0]["1. open"]
            return price
        except KeyError:
            return None

@app.websocket("/ws/stock/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await manager.connect(websocket)
    try:
        while True:
            price = await get_stock_price(symbol)
            if price:
                await manager.broadcast(f"{symbol} price: {price}")
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        manager.disconnect(websocket)