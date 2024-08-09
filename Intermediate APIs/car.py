from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

DATABASE_URL = "sqlite:///./car_rental.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, index=True)
    model = Column(String)
    year = Column(Integer)
    available = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

class CarCreate(BaseModel):
    make: str
    model: str
    year: int

class CarOut(BaseModel):
    id: int
    make: str
    model: str
    year: int
    available: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/cars/", response_model=CarOut)
async def add_car(car: CarCreate, db: Session = Depends(get_db)):
    db_car = Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

@app.get("/cars/", response_model=List[CarOut])
async def list_cars(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Car).offset(skip).limit(limit).all()

@app.put("/cars/{car_id}/rent", response_model=CarOut)
async def rent_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    if not car.available:
        raise HTTPException(status_code=400, detail="Car already rented")
    car.available = False
    db.commit()
    db.refresh(car)
    return car

@app.put("/cars/{car_id}/return", response_model=CarOut)
async def return_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    if car.available:
        raise HTTPException(status_code=400, detail="Car is not rented")
    car.available = True
    db.commit()
    db.refresh(car)
    return car