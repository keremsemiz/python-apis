from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List
from datetime import date

DATABASE_URL = "sqlite:///./expense_reimbursement.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    expenses = relationship("Expense", back_populates="employee")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    amount = Column(Float)
    description = Column(String)
    date_submitted = Column(Date)
    approved = Column(Boolean, default=False)
    employee = relationship("Employee", back_populates="expenses")

Base.metadata.create_all(bind=engine)

class EmployeeCreate(BaseModel):
    name: str

class ExpenseCreate(BaseModel):
    employee_id: int
    amount: float
    description: str
    date_submitted: date

class ExpenseOut(BaseModel):
    id: int
    employee_id: int
    amount: float
    description: str
    date_submitted: date
    approved: bool

class EmployeeOut(BaseModel):
    id: int
    name: str
    expenses: List[ExpenseOut] = []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/employees/", response_model=EmployeeOut)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/employees/", response_model=List[EmployeeOut])
async def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@app.post("/expenses/", response_model=ExpenseOut)
async def submit_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.put("/expenses/{expense_id}/approve/", response_model=ExpenseOut)
async def approve_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense.approved = True
    db.commit()
    db.refresh(expense)
    return expense
