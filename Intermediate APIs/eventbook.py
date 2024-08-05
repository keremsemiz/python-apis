from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

DATABASE_URL = "sqlite:///./events.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    date = Column(String)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_name = Column(String)
    tickets = Column(Integer)

class EventCreate(BaseModel):
    name: str
    location: str
    date: str

class BookingCreate(BaseModel):
    event_id: int
    user_name: str
    tickets: int

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/events/", response_model=EventCreate)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events/", response_model=List[EventCreate])
async def read_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@app.post("/bookings/", response_model=BookingCreate)
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.id == booking.event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    db_booking = Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.get("/bookings/", response_model=List[BookingCreate])
async def read_bookings(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    bookings = db.query(Booking).offset(skip).limit(limit).all()
    return bookings