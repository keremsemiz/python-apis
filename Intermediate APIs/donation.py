from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List
from datetime import date

DATABASE_URL = "sqlite:///./donation_management.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Donor(Base):
    __tablename__ = "donors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)
    donations = relationship("Donation", back_populates="donor")

class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id"))
    amount = Column(Float)
    date = Column(Date)
    donor = relationship("Donor", back_populates="donations")

Base.metadata.create_all(bind=engine)

class DonorCreate(BaseModel):
    name: str
    email: str

class DonationCreate(BaseModel):
    donor_id: int
    amount: float
    date: date

class DonorOut(BaseModel):
    id: int
    name: str
    email: str
    donations: List[DonationCreate] = []

class DonationOut(BaseModel):
    id: int
    donor_id: int
    amount: float
    date: date

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/donors/", response_model=DonorOut)
async def add_donor(donor: DonorCreate, db: Session = Depends(get_db)):
    db_donor = Donor(**donor.dict())
    db.add(db_donor)
    db.commit()
    db.refresh(db_donor)
    return db_donor

@app.get("/donors/", response_model=List[DonorOut])
async def list_donors(db: Session = Depends(get_db)):
    return db.query(Donor).all()

@app.post("/donations/", response_model=DonationOut)
async def add_donation(donation: DonationCreate, db: Session = Depends(get_db)):
    db_donor = db.query(Donor).filter(Donor.id == donation.donor_id).first()
    if not db_donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    db_donation = Donation(**donation.dict())
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)
    return db_donation

@app.get("/donations/", response_model=List[DonationOut])
async def list_donations(db: Session = Depends(get_db)):
    return db.query(Donation).all()

@app.get("/donations/report/", response_model=List[DonationOut])
async def donation_report(start_date: date, end_date: date, db: Session = Depends(get_db)):
    return db.query(Donation).filter(Donation.date.between(start_date, end_date)).all()