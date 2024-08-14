from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List
from datetime import datetime

DATABASE_URL = "sqlite:///./booking_management.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    booking_date = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    service = Column(String)
    status = Column(String, default="confirmed")
    is_cancelled = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

class BookingCreate(BaseModel):
    customer_name: str
    booking_date: datetime
    start_time: datetime
    end_time: datetime
    service: str

class BookingOut(BaseModel):
    id: int
    customer_name: str
    booking_date: datetime
    start_time: datetime
    end_time: datetime
    service: str
    status: str
    is_cancelled: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/bookings/", response_model=BookingOut)
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    db_booking = Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.get("/bookings/", response_model=List[BookingOut])
async def list_bookings(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Booking).offset(skip).limit(limit).all()

@app.get("/bookings/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking

@app.put("/bookings/{booking_id}/cancel/", response_model=BookingOut)
async def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    db_booking.is_cancelled = True
    db_booking.status = "cancelled"
    db.commit()
    db.refresh(db_booking)
    return db_booking