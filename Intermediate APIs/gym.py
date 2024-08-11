from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List
from datetime import datetime

DATABASE_URL = "sqlite:///./gym_membership.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)
    membership_start = Column(DateTime)
    membership_end = Column(DateTime)
    attendances = relationship("Attendance", back_populates="member")
    classes = relationship("ClassBooking", back_populates="member")

class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    date = Column(DateTime)
    member = relationship("Member", back_populates="attendances")

class GymClass(Base):
    __tablename__ = "gym_classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    schedule = Column(DateTime)
    bookings = relationship("ClassBooking", back_populates="gym_class")

class ClassBooking(Base):
    __tablename__ = "class_bookings"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    class_id = Column(Integer, ForeignKey("gym_classes.id"))
    gym_class = relationship("GymClass", back_populates="bookings")
    member = relationship("Member", back_populates="classes")

Base.metadata.create_all(bind=engine)

class MemberCreate(BaseModel):
    name: str
    email: str
    membership_start: datetime
    membership_end: datetime

class AttendanceCreate(BaseModel):
    member_id: int
    date: datetime

class GymClassCreate(BaseModel):
    name: str
    schedule: datetime

class ClassBookingCreate(BaseModel):
    member_id: int
    class_id: int

class MemberOut(BaseModel):
    id: int
    name: str
    email: str
    membership_start: datetime
    membership_end: datetime
    attendances: List[AttendanceCreate] = []
    classes: List[ClassBookingCreate] = []

class AttendanceOut(BaseModel):
    id: int
    member_id: int
    date: datetime

class GymClassOut(BaseModel):
    id: int
    name: str
    schedule: datetime
    bookings: List[ClassBookingCreate] = []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/members/", response_model=MemberOut)
async def add_member(member: MemberCreate, db: Session = Depends(get_db)):
    db_member = Member(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@app.get("/members/", response_model=List[MemberOut])
async def list_members(db: Session = Depends(get_db)):
    return db.query(Member).all()

@app.post("/attendances/", response_model=AttendanceOut)
async def add_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    db_attendance = Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@app.post("/classes/", response_model=GymClassOut)
async def add_class(gym_class: GymClassCreate, db: Session = Depends(get_db)):
    db_class = GymClass(**gym_class.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@app.post("/class_bookings/", response_model=ClassBookingCreate)
async def book_class(booking: ClassBookingCreate, db: Session = Depends(get_db)):
    db_class = db.query(GymClass).filter(GymClass.id == booking.class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    db_booking = ClassBooking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking
