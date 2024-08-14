from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import datetime
import shutil
import os

DATABASE_URL = "sqlite:///./file_management.db"
UPLOAD_DIR = "./uploaded_files/"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class FileMeta(Base):
    __tablename__ = "file_meta"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    category = Column(String, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String)

Base.metadata.create_all(bind=engine)

class FileMetaCreate(BaseModel):
    category: str

class FileMetaOut(BaseModel):
    id: int
    filename: str
    category: str
    upload_date: datetime
    file_path: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/", response_model=FileMetaOut)
async def upload_file(file: UploadFile, metadata: FileMetaCreate, db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_file = FileMeta(filename=file.filename, category=metadata.category, file_path=file_path)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

@app.get("/files/", response_model=List[FileMetaOut])
async def list_files(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(FileMeta).offset(skip).limit(limit).all()

@app.get("/files/{file_id}", response_model=FileMetaOut)
async def get_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(FileMeta).filter(FileMeta.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@app.delete("/files/{file_id}", response_model=dict)
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(FileMeta).filter(FileMeta.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(db_file.file_path)
    db.delete(db_file)
    db.commit()
    return {"message": "File deleted"}