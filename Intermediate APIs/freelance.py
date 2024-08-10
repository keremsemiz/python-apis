from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

DATABASE_URL = "sqlite:///./freelancer_job_board.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    location = Column(String)
    applications = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    freelancer_name = Column(String)
    freelancer_email = Column(String)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    job = relationship("Job", back_populates="applications")

Base.metadata.create_all(bind=engine)

class JobCreate(BaseModel):
    title: str
    description: str
    location: str

class ApplicationCreate(BaseModel):
    freelancer_name: str
    freelancer_email: str

class JobOut(BaseModel):
    id: int
    title: str
    description: str
    location: str
    applications: List[ApplicationCreate] = []

class ApplicationOut(BaseModel):
    id: int
    freelancer_name: str
    freelancer_email: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/jobs/", response_model=JobOut)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/jobs/", response_model=List[JobOut])
async def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@app.post("/jobs/{job_id}/apply/", response_model=ApplicationOut)
async def apply_for_job(job_id: int, application: ApplicationCreate, db: Session = Depends(get_db)):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    db_application = Application(**application.dict(), job_id=job_id)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@app.get("/jobs/{job_id}", response_model=JobOut)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job
