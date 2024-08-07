from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

DATABASE_URL = "sqlite:///./polls.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Poll(Base):
    __tablename__ = "polls"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    options = relationship("Option", back_populates="poll")

class Option(Base):
    __tablename__ = "options"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    votes = Column(Integer, default=0)
    poll_id = Column(Integer, ForeignKey("polls.id"))
    poll = relationship("Poll", back_populates="options")

Base.metadata.create_all(bind=engine)

class OptionCreate(BaseModel):
    text: str

class PollCreate(BaseModel):
    question: str
    options: List[OptionCreate]

class OptionOut(BaseModel):
    id: int
    text: str
    votes: int

class PollOut(BaseModel):
    id: int
    question: str
    options: List[OptionOut]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/polls/", response_model=PollOut)
async def create_poll(poll: PollCreate, db: Session = Depends(get_db)):
    db_poll = Poll(question=poll.question)
    db.add(db_poll)
    db.commit()
    db.refresh(db_poll)
    for option in poll.options:
        db_option = Option(text=option.text, poll_id=db_poll.id)
        db.add(db_option)
    db.commit()
    db.refresh(db_poll)
    return db_poll

@app.get("/polls/", response_model=List[PollOut])
async def read_polls(db: Session = Depends(get_db)):
    return db.query(Poll).all()

@app.post("/polls/{poll_id}/vote/{option_id}", response_model=OptionOut)
async def vote(poll_id: int, option_id: int, db: Session = Depends(get_db)):
    option = db.query(Option).filter(Option.id == option_id, Option.poll_id == poll_id).first()
    if option is None:
        raise HTTPException(status_code=404, detail="Option not found")
    option.votes += 1
    db.commit()
    db.refresh(option)
    return option

@app.get("/polls/{poll_id}", response_model=PollOut)
async def read_poll(poll_id: int, db: Session = Depends(get_db)):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if poll is None:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll