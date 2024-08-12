from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List
from enum import Enum

DATABASE_URL = "sqlite:///./issue_tracking.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class IssueStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(SQLEnum(IssueStatus), default=IssueStatus.open)
    assignee_id = Column(Integer, ForeignKey("developers.id"))
    assignee = relationship("Developer", back_populates="issues")

class Developer(Base):
    __tablename__ = "developers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    issues = relationship("Issue", back_populates="assignee")

Base.metadata.create_all(bind=engine)

class IssueCreate(BaseModel):
    title: str
    description: str
    assignee_id: int

class DeveloperCreate(BaseModel):
    name: str

class IssueOut(BaseModel):
    id: int
    title: str
    description: str
    status: IssueStatus
    assignee_id: int

class DeveloperOut(BaseModel):
    id: int
    name: str
    issues: List[IssueCreate] = []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/developers/", response_model=DeveloperOut)
async def add_developer(developer: DeveloperCreate, db: Session = Depends(get_db)):
    db_developer = Developer(**developer.dict())
    db.add(db_developer)
    db.commit()
    db.refresh(db_developer)
    return db_developer

@app.get("/developers/", response_model=List[DeveloperOut])
async def list_developers(db: Session = Depends(get_db)):
    return db.query(Developer).all()

@app.post("/issues/", response_model=IssueOut)
async def add_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    db_developer = db.query(Developer).filter(Developer.id == issue.assignee_id).first()
    if not db_developer:
        raise HTTPException(status_code=404, detail="Assignee not found")
    db_issue = Issue(**issue.dict())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

@app.get("/issues/", response_model=List[IssueOut])
async def list_issues(db: Session = Depends(get_db)):
    return db.query(Issue).all()

@app.put("/issues/{issue_id}/status/", response_model=IssueOut)
async def update_issue_status(issue_id: int, status: IssueStatus, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.status = status
    db.commit()
    db.refresh(issue)
    return issue