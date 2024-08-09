from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

DATABASE_URL = "sqlite:///./forum.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Thread(Base):
    __tablename__ = "threads"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    comments = relationship("Comment", back_populates="thread")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    thread_id = Column(Integer, ForeignKey("threads.id"))
    thread = relationship("Thread", back_populates="comments")

Base.metadata.create_all(bind=engine)

class CommentCreate(BaseModel):
    content: str

class ThreadCreate(BaseModel):
    title: str
    content: str
    comments: List[CommentCreate] = []

class CommentOut(BaseModel):
    id: int
    content: str

class ThreadOut(BaseModel):
    id: int
    title: str
    content: str
    comments: List[CommentOut]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/threads/", response_model=ThreadOut)
async def create_thread(thread: ThreadCreate, db: Session = Depends(get_db)):
    db_thread = Thread(title=thread.title, content=thread.content)
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    for comment in thread.comments:
        db_comment = Comment(content=comment.content, thread_id=db_thread.id)
        db.add(db_comment)
    db.commit()
    db.refresh(db_thread)
    return db_thread

@app.get("/threads/", response_model=List[ThreadOut])
async def read_threads(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Thread).offset(skip).limit(limit).all()

@app.post("/threads/{thread_id}/comments/", response_model=CommentOut)
async def add_comment(thread_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    db_thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if db_thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    db_comment = Comment(content=comment.content, thread_id=db_thread.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/threads/{thread_id}", response_model=ThreadOut)
async def read_thread(thread_id: int, db: Session = Depends(get_db)):
    db_thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if db_thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return db_thread