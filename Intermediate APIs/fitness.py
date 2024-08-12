from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List
from datetime import datetime

DATABASE_URL = "sqlite:///./fitness_progress.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    workouts = relationship("Workout", back_populates="user")
    measurements = relationship("Measurement", back_populates="user")

class Workout(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    exercise = Column(String)
    sets = Column(Integer)
    reps = Column(Integer)
    weight = Column(Float)
    user = relationship("User", back_populates="workouts")

class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    weight = Column(Float)
    body_fat = Column(Float)
    user = relationship("User", back_populates="measurements")

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    name: str

class WorkoutCreate(BaseModel):
    user_id: int
    date: datetime
    exercise: str
    sets: int
    reps: int
    weight: float

class MeasurementCreate(BaseModel):
    user_id: int
    date: datetime
    weight: float
    body_fat: float

class UserOut(BaseModel):
    id: int
    name: str
    workouts: List[WorkoutCreate] = []
    measurements: List[MeasurementCreate] = []

class WorkoutOut(BaseModel):
    id: int
    user_id: int
    date: datetime
    exercise: str
    sets: int
    reps: int
    weight: float

class MeasurementOut(BaseModel):
    id: int
    user_id: int
    date: datetime
    weight: float
    body_fat: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=UserOut)
async def add_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserOut])
async def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/workouts/", response_model=WorkoutOut)
async def add_workout(workout: WorkoutCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == workout.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_workout = Workout(**workout.dict())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

@app.get("/workouts/", response_model=List[WorkoutOut])
async def list_workouts(db: Session = Depends(get_db)):
    return db.query(Workout).all()

@app.post("/measurements/", response_model=MeasurementOut)
async def add_measurement(measurement: MeasurementCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == measurement.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_measurement = Measurement(**measurement.dict())
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

@app.get("/measurements/", response_model=List[MeasurementOut])
async def list_measurements(db: Session = Depends(get_db)):
    return db.query(Measurement).all()