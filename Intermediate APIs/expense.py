from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client.expense_tracker

class Expense(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    amount: float
    category: str
    description: str
    date: datetime

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: str
    date: datetime

@app.post("/expenses/", response_model=Expense)
async def create_expense(expense: ExpenseCreate):
    expense_dict = expense.dict()
    result = db.expenses.insert_one(expense_dict)
    return {**expense_dict, "_id": str(result.inserted_id)}

@app.get("/expenses/", response_model=List[Expense])
async def read_expenses(skip: int = 0, limit: int = 10):
    expenses = list(db.expenses.find().skip(skip).limit(limit))
    return [Expense(**expense) for expense in expenses]

@app.put("/expenses/{expense_id}", response_model=Expense)
async def update_expense(expense_id: str, expense: ExpenseCreate):
    result = db.expenses.update_one({"_id": ObjectId(expense_id)}, {"$set": expense.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {**expense.dict(), "_id": expense_id}

@app.delete("/expenses/{expense_id}", response_model=dict)
async def delete_expense(expense_id: str):
    result = db.expenses.delete_one({"_id": ObjectId(expense_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted"}