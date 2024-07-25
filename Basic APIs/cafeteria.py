from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

menu = {
    "1": {"name": "Pasta", "description": "Delicious homemade pasta", "price": 8.5},
    "2": {"name": "Salad", "description": "Fresh garden salad", "price": 5.0},
    "3": {"name": "Burger", "description": "Juicy beef burger with fries", "price": 10.0}
}

class Booking(BaseModel):
    meal_id: str
    customer_name: str
    quantity: int

bookings: List[Dict] = []

@app.get("/")
def read_root():
    return {"message": "Welcome to the Cafeteria Food Booking API"}

@app.get("/menu")
def view_menu():
    return {"menu": menu}

@app.post("/book", response_model=Booking)
def book_meal(booking: Booking):
    if booking.meal_id not in menu:
        raise HTTPException(status_code=404, detail="Meal not found")
    if booking.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    bookings.append(booking.dict())
    return booking

@app.get("/bookings")
def view_bookings():
    return {"bookings": bookings}
