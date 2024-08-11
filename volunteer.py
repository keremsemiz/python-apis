from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

DATABASE_URL = "sqlite:///./volunteer_management.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Volunteer(Base):
    __tablename__ = "volunteers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    tasks = relationship("Task", back_populates="volunteer")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"))
    volunteer = relationship("Volunteer", back_populates="tasks")

Base.metadata.create_all(bind=engine)

class VolunteerCreate(BaseModel):
    name: str
    email: str

class TaskCreate(BaseModel):
    description: str
    volunteer_id: int

class VolunteerOut(BaseModel):
    id: int
    name: str
    email: str
    tasks: List[TaskCreate] = []

class TaskOut(BaseModel):
    id: int
    description: str
    volunteer_id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/volunteers/", response_model=VolunteerOut)
async def add_volunteer(volunteer: VolunteerCreate, db: Session = Depends(get_db)):
    db_volunteer = Volunteer(**volunteer.dict())
    db.add(db_volunteer)
    db.commit()
    db.refresh(db_volunteer)
    return db_volunteer

@app.get("/volunteers/", response_model=List[VolunteerOut])
async def list_volunteers(db: Session = Depends(get_db)):
    return db.query(Volunteer).all()

@app.post("/tasks/", response_model=TaskOut)
async def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_volunteer = db.query(Volunteer).filter(Volunteer.id == task.volunteer_id).first()
    if not db_volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=List[TaskOut])
async def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()
