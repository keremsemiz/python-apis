from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class TodoItem(BaseModel):
    id: int
    task: str
    completed: bool

todos: List[TodoItem] = []

@app.get("/")
def read_root():
    return {"message": "Welcome to the To-Do List API"}

@app.get("/todos")
def get_all_todos():
    return {"todos": todos}

@app.post("/todo", response_model=TodoItem)
def add_todo_item(item: TodoItem):
    todos.append(item)
    return item
