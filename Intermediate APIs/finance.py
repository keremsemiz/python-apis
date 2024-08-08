from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

DATABASE_URL = "sqlite:///./finance.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)  # income or expense
    amount = Column(Float)
    description = Column(String)

Base.metadata.create_all(bind=engine)

class TransactionCreate(BaseModel):
    type: str
    amount: float
    description: str

class TransactionOut(BaseModel):
    id: int
    type: str
    amount: float
    description: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/transactions/", response_model=TransactionOut)
async def add_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/", response_model=List[TransactionOut])
async def list_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()

@app.get("/transactions/summary/")
async def summary(db: Session = Depends(get_db)):
    income = db.query(Transaction).filter(Transaction.type == "income").all()
    expense = db.query(Transaction).filter(Transaction.type == "expense").all()
    total_income = sum(i.amount for i in income)
    total_expense = sum(e.amount for e in expense)
    return {"total_income": total_income, "total_expense": total_expense, "net_balance": total_income - total_expense}