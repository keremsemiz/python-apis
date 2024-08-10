from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List

DATABASE_URL = "sqlite:///./conference_room_booking.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    bookings = relationship("Booking", back_populates="room")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    room = relationship("Room", back_populates="bookings")

Base.metadata.create_all(bind=engine)

class BookingCreate(BaseModel):
    room_id: int
    user: str
    start_time: datetime
    end_time: datetime

class BookingOut(BaseModel):
    id: int
    room_id: int
    user: str
    start_time: datetime
    end_time: datetime

class RoomCreate(BaseModel):
    name: str

class RoomOut(BaseModel):
    id: int
    name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/rooms/", response_model=RoomOut)
async def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    db_room = Room(name=room.name)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@app.get("/rooms/", response_model=List[RoomOut])
async def read_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).all()
    return rooms

@app.post("/bookings/", response_model=BookingOut)
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    overlapping_bookings = db.query(Booking).filter(
        Booking.room_id == booking.room_id,
        Booking.start_time < booking.end_time,
        Booking.end_time > booking.start_time
    ).all()
    
    if overlapping_bookings:
        raise HTTPException(status_code=400, detail="Time slot already booked")
    
    db_booking = Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.get("/bookings/", response_model=List[BookingOut])
async def read_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()
