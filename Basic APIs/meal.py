from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import date

DATABASE_URL = "sqlite:///./meal_planning.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    day = Column(Date)

Base.metadata.create_all(bind=engine)

class MealCreate(BaseModel):
    name: str
    day: date

class MealOut(BaseModel):
    id: int
    name: str
    day: date

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/meals/", response_model=MealOut)
async def add_meal(meal: MealCreate, db: Session = Depends(get_db)):
    db_meal = Meal(**meal.dict())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

@app.get("/meals/", response_model=List[MealOut])
async def list_meals(db: Session = Depends(get_db)):
    return db.query(Meal).order_by(Meal.day.asc()).all()

@app.put("/meals/{meal_id}/", response_model=MealOut)
async def update_meal(meal_id: int, meal: MealCreate, db: Session = Depends(get_db)):
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    for key, value in meal.dict().items():
        setattr(db_meal, key, value)
    db.commit()
    db.refresh(db_meal)
    return db_meal

@app.delete("/meals/{meal_id}/", response_model=dict)
async def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    db_meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.delete(db_meal)
    db.commit()
    return {"message": "Meal deleted"}
