from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List
from datetime import date, time

DATABASE_URL = "sqlite:///./workforce_management.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    position = Column(String, index=True)
    shifts = relationship("Shift", back_populates="employee")

class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    employee = relationship("Employee", back_populates="shifts")

Base.metadata.create_all(bind=engine)

class EmployeeCreate(BaseModel):
    name: str
    position: str

class ShiftCreate(BaseModel):
    employee_id: int
    date: date
    start_time: time
    end_time: time

class EmployeeOut(BaseModel):
    id: int
    name: str
    position: str
    shifts: List[ShiftCreate] = []

class ShiftOut(BaseModel):
    id: int
    employee_id: int
    date: date
    start_time: time
    end_time: time

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/employees/", response_model=EmployeeOut)
async def add_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/", response_model=List[EmployeeOut])
async def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@app.post("/shifts/", response_model=ShiftOut)
async def assign_shift(shift: ShiftCreate, db: Session = Depends(get_db)):
    db_employee = db.query(Employee).filter(Employee.id == shift.employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db_shift = Shift(**shift.dict())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift

@app.get("/shifts/", response_model=List[ShiftOut])
async def list_shifts(db: Session = Depends(get_db)):
    return db.query(Shift).all()
