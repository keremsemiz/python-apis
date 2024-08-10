from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

DATABASE_URL = "sqlite:///./reading.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    progress = Column(Integer, default=0)  # Percentage
    rating = Column(Float, nullable=True)

Base.metadata.create_all(bind=engine)

class BookCreate(BaseModel):
    title: str
    author: str

class BookUpdate(BaseModel):
    progress: int
    rating: float

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    progress: int
    rating: float = None

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

@app.put("/books/{book_id}", response_model=BookOut)
async def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.progress is not None:
        db_book.progress = book.progress
    if book.rating is not None:
        db_book.rating = book.rating
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}", response_model=dict)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted"}
