from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import datetime

DATABASE_URL = "sqlite:///./task_automation.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    schedule = Column(DateTime)
    status = Column(String, default="pending")
    is_completed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

class TaskCreate(BaseModel):
    name: str
    description: str
    schedule: datetime

class TaskOut(BaseModel):
    id: int
    name: str
    description: str
    schedule: datetime
    status: str
    is_completed: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tasks/", response_model=TaskOut)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=List[TaskOut])
async def list_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Task).offset(skip).limit(limit).all()

@app.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{task_id}/complete/", response_model=TaskOut)
async def complete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.is_completed = True
    db_task.status = "completed"
    db.commit()
    db.refresh(db_task)
    return db_task