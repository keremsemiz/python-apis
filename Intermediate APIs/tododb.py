from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

app = FastAPI()

DATABASE = "todo.db"

class TodoItem(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    completed: bool = False

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS todo (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        description TEXT,
                        completed BOOLEAN)''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()

@app.post("/todos/", response_model=TodoItem)
async def create_todo_item(item: TodoItem):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todo (title, description, completed) VALUES (?, ?, ?)",
                   (item.title, item.description, item.completed))
    conn.commit()
    item.id = cursor.lastrowid
    conn.close()
    return item

@app.get("/todos/", response_model=List[TodoItem])
async def read_todo_items():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM todo")
    items = cursor.fetchall()
    conn.close()
    return [TodoItem(id=row[0], title=row[1], description=row[2], completed=row[3]) for row in items]

@app.put("/todos/{todo_id}", response_model=TodoItem)
async def update_todo_item(todo_id: int, item: TodoItem):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE todo SET title = ?, description = ?, completed = ? WHERE id = ?",
                   (item.title, item.description, item.completed, todo_id))
    conn.commit()
    conn.close()
    return item

@app.delete("/todos/{todo_id}", response_model=dict)
async def delete_todo_item(todo_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todo WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return {"message": "Todo item deleted"}