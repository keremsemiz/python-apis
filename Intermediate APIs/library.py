from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    available = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

class BookCreate(BaseModel):
    title: str
    author: str

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    available: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/books/", response_model=BookOut)
async def add_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/", response_model=List[BookOut])
async def list_books(db: Session = Depends(get_db)):
    return db.query(Book).all()

@app.put("/books/{book_id}/borrow", response_model=BookOut)
async def borrow_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.available:
        raise HTTPException(status_code=400, detail="Book already borrowed")
    book.available = False
    db.commit()
    db.refresh(book)
    return book

@app.put("/books/{book_id}/return", response_model=BookOut)
async def return_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available:
        raise HTTPException(status_code=400, detail="Book is not borrowed")
    book.available = True
    db.commit()
    db.refresh(book)
    return book