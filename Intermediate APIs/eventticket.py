from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

DATABASE_URL = "sqlite:///./event_ticketing.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(String)
    tickets_available = Column(Integer)
    tickets_sold = Column(Integer, default=0)
    bookings = relationship("Booking", back_populates="event")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    customer_name = Column(String)
    number_of_tickets = Column(Integer)
    event = relationship("Event", back_populates="bookings")

Base.metadata.create_all(bind=engine)

class EventCreate(BaseModel):
    name: str
    date: str
    tickets_available: int

class BookingCreate(BaseModel):
    customer_name: str
    number_of_tickets: int

class EventOut(BaseModel):
    id: int
    name: str
    date: str
    tickets_available: int
    tickets_sold: int

class BookingOut(BaseModel):
    id: int
    event_id: int
    customer_name: str
    number_of_tickets: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/events/", response_model=EventOut)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events/", response_model=List[EventOut])
async def list_events(db: Session = Depends(get_db)):
    return db.query(Event).all()

@app.post("/events/{event_id}/book/", response_model=BookingOut)
async def book_tickets(event_id: int, booking: BookingCreate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.tickets_available < booking.number_of_tickets:
        raise HTTPException(status_code=400, detail="Not enough tickets available")
    event.tickets_available -= booking.number_of_tickets
    event.tickets_sold += booking.number_of_tickets
    db_booking = Booking(event_id=event_id, **booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    db.refresh(event)
    return db_booking

@app.get("/events/{event_id}/", response_model=EventOut)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
