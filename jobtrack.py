from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from enum import Enum
from datetime import date

DATABASE_URL = "sqlite:///./job_applications.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class ApplicationStatus(str, Enum):
    applied = "applied"
    interview = "interview"
    offer = "offer"
    rejected = "rejected"

class JobApplication(Base):
    __tablename__ = "job_applications"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    job_title = Column(String, index=True)
    application_date = Column(Date)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.applied)

Base.metadata.create_all(bind=engine)

class JobApplicationCreate(BaseModel):
    company_name: str
    job_title: str
    application_date: date
    status: ApplicationStatus = ApplicationStatus.applied

class JobApplicationOut(BaseModel):
    id: int
    company_name: str
    job_title: str
    application_date: date
    status: ApplicationStatus

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/applications/", response_model=JobApplicationOut)
async def create_application(application: JobApplicationCreate, db: Session = Depends(get_db)):
    db_application = JobApplication(**application.dict())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@app.get("/applications/", response_model=List[JobApplicationOut])
async def list_applications(db: Session = Depends(get_db)):
    return db.query(JobApplication).all()

@app.put("/applications/{application_id}/", response_model=JobApplicationOut)
async def update_application(application_id: int, application: JobApplicationCreate, db: Session = Depends(get_db)):
    db_application = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    for key, value in application.dict().items():
        setattr(db_application, key, value)
    db.commit()
    db.refresh(db_application)
    return db_application
