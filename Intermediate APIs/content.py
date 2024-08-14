from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import datetime

DATABASE_URL = "sqlite:///./content_management.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    body = Column(Text)
    content_type = Column(String, index=True)
    published_on = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class ContentCreate(BaseModel):
    title: str
    body: str
    content_type: str

class ContentOut(BaseModel):
    id: int
    title: str
    body: str
    content_type: str
    published_on: datetime

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/content/", response_model=ContentOut)
async def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    db_content = Content(**content.dict())
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

@app.get("/content/", response_model=List[ContentOut])
async def list_content(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Content).offset(skip).limit(limit).all()

@app.get("/content/{content_id}", response_model=ContentOut)
async def get_content(content_id: int, db: Session = Depends(get_db)):
    db_content = db.query(Content).filter(Content.id == content_id).first()
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    return db_content

@app.put("/content/{content_id}", response_model=ContentOut)
async def update_content(content_id: int, content: ContentCreate, db: Session = Depends(get_db)):
    db_content = db.query(Content).filter(Content.id == content_id).first()
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    for key, value in content.dict().items():
        setattr(db_content, key, value)
    db.commit()
    db.refresh(db_content)
    return db_content

@app.delete("/content/{content_id}", response_model=dict)
async def delete_content(content_id: int, db: Session = Depends(get_db)):
    db_content = db.query(Content).filter(Content.id == content_id).first()
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    db.delete(db_content)
    db.commit()
    return {"message": "Content deleted"}