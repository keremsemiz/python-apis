from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import date

DATABASE_URL = "sqlite:///./vehicle_maintenance.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer, index=True)
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle")

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    service_type = Column(String, index=True)
    service_date = Column(Date)
    cost = Column(Float)
    vehicle = relationship("Vehicle", back_populates="maintenance_records")

Base.metadata.create_all(bind=engine)

class VehicleCreate(BaseModel):
    make: str
    model: str
    year: int

class MaintenanceRecordCreate(BaseModel):
    vehicle_id: int
    service_type: str
    service_date: date
    cost: float

class VehicleOut(BaseModel):
    id: int
    make: str
    model: str
    year: int
    maintenance_records: List[MaintenanceRecordCreate] = []

class MaintenanceRecordOut(BaseModel):
    id: int
    vehicle_id: int
    service_type: str
    service_date: date
    cost: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/vehicles/", response_model=VehicleOut)
async def add_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@app.get("/vehicles/", response_model=List[VehicleOut])
async def list_vehicles(db: Session = Depends(get_db)):
    return db.query(Vehicle).all()

@app.post("/maintenance/", response_model=MaintenanceRecordOut)
async def add_maintenance_record(record: MaintenanceRecordCreate, db: Session = Depends(get_db)):
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db_record = MaintenanceRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/maintenance/", response_model=List[MaintenanceRecordOut])
async def list_maintenance_records(db: Session = Depends(get_db)):
    return db.query(MaintenanceRecord).all()
