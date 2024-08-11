from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import date

DATABASE_URL = "sqlite:///./subscriptions.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    product = Column(String, index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

class SubscriptionCreate(BaseModel):
    customer_name: str
    product: str
    start_date: date
    end_date: date

class SubscriptionOut(BaseModel):
    id: int
    customer_name: str
    product: str
    start_date: date
    end_date: date
    active: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/subscriptions/", response_model=SubscriptionOut)
async def add_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@app.get("/subscriptions/", response_model=List[SubscriptionOut])
async def list_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).all()

@app.put("/subscriptions/{subscription_id}/cancel/", response_model=SubscriptionOut)
async def cancel_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    subscription.active = False
    db.commit()
    db.refresh(subscription)
    return subscription
