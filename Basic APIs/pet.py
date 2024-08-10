from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

DATABASE_URL = "sqlite:///./pet_adoption.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    species = Column(String, index=True)
    age = Column(Integer)
    adopted = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

class PetCreate(BaseModel):
    name: str
    species: str
    age: int

class PetOut(BaseModel):
    id: int
    name: str
    species: str
    age: int
    adopted: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/pets/", response_model=PetOut)
async def create_pet(pet: PetCreate, db: Session = Depends(get_db)):
    db_pet = Pet(**pet.dict())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

@app.get("/pets/", response_model=List[PetOut])
async def list_pets(db: Session = Depends(get_db)):
    return db.query(Pet).all()

@app.put("/pets/{pet_id}/adopt", response_model=PetOut)
async def adopt_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    if pet.adopted:
        raise HTTPException(status_code=400, detail="Pet already adopted")
    pet.adopted = True
    db.commit()
    db.refresh(pet)
    return pet
