from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

DATABASE_URL = "sqlite:///./jobboard.db"
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
    applicant_name = Column(String)
    applicant_email = Column(String)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    job = relationship("Job", back_populates="applications")

Base.metadata.create_all(bind=engine)

class JobCreate(BaseModel):
    title: str
    description: str
    location: str

class ApplicationCreate(BaseModel):
    applicant_name: str
    applicant_email: str

class JobOut(BaseModel):
    id: int
    title: str
    description: str
    location: str
    applications: List[ApplicationCreate] = []

class ApplicationOut(BaseModel):
    id: int
    applicant_name: str
    applicant_email: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/jobs/", response_model=JobOut)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(title=job.title, description=job.description, location=job.location)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/jobs/", response_model=List[JobOut])
async def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return jobs

@app.post("/jobs/{job_id}/apply/", response_model=ApplicationOut)
async def apply_for_job(job_id: int, application: ApplicationCreate, db: Session = Depends(get_db)):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    db_application = Application(applicant_name=application.applicant_name, applicant_email=application.applicant_email, job_id=job_id)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@app.get("/jobs/{job_id}", response_model=JobOut)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db