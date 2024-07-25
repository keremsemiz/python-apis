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

@app.put("/todo/{item_id}/complete")
def complete_todo_item(item_id: int):
    for item in todos:
        if item.id == item_id:
            item.completed = True
            return {"message": "Task marked as completed", "item": item}
    raise HTTPException(status_code=404, detail="Todo item not found")

@app.delete("/todo/{item_id}")
def delete_todo_item(item_id: int):
    global todos
    todos = [item for item in todos if item.id != item_id]
    return {"message": "Task deleted"}