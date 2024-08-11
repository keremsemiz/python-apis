from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from typing import List

DATABASE_URL = "sqlite:///./task_time_tracking.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    time_entries = relationship("TimeEntry", back_populates="task")

class TimeEntry(Base):
    __tablename__ = "time_entries"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    task = relationship("Task", back_populates="time_entries")

Base.metadata.create_all(bind=engine)

class TaskCreate(BaseModel):
    name: str

class TaskOut(BaseModel):
    id: int
    name: str

class TimeEntryCreate(BaseModel):
    task_id: int
    start_time: datetime

class TimeEntryOut(BaseModel):
    id: int
    task_id: int
    start_time: datetime
    end_time: datetime = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tasks/", response_model=TaskOut)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(name=task.name)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=List[TaskOut])
async def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.post("/tasks/{task_id}/start/", response_model=TimeEntryOut)
async def start_task(task_id: int, time_entry: TimeEntryCreate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_time_entry = TimeEntry(task_id=task_id, start_time=time_entry.start_time)
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry

@app.put("/tasks/{task_id}/stop/{entry_id}/", response_model=TimeEntryOut)
async def stop_task(task_id: int, entry_id: int, db: Session = Depends(get_db)):
    db_time_entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id, TimeEntry.task_id == task_id).first()
    if not db_time_entry or db_time_entry.end_time is not None:
        raise HTTPException(status_code=404, detail="Time entry not found or already stopped")
    db_time_entry.end_time = datetime.utcnow()
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry

@app.get("/tasks/{task_id}/time_entries/", response_model=List[TimeEntryOut])
async def list_time_entries(task_id: int, db: Session = Depends(get_db)):
    return db.query(TimeEntry).filter(TimeEntry.task_id == task_id).all()
