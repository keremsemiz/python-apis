from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from celery import Celery
import time

app = FastAPI()

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

class Task(BaseModel):
    id: str
    description: str
    status: str

tasks_db = {}

@celery_app.task
def long_running_task(task_id: str):
    time.sleep(10)  # to simulate long tesk
    tasks_db[task_id]["status"] = "completed"

@app.post("/tasks/", response_model=Task)
async def create_task(description: str, background_tasks: BackgroundTasks):
    task_id = str(len(tasks_db) + 1)
    task = {"id": task_id, "description": description, "status": "pending"}
    tasks_db[task_id] = task
    background_tasks.add_task(long_running_task, task_id)
    return task

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task