from fastapi import FastAPI, HTTPException
from typing import List, Dict

app = FastAPI()

# mock data for some books
books_data = {
    "1": {"title": "1984", "author": "George Orwell", "year": 1949},
    "2": {"title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960},
    "3": {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925}
}

@app.get("/")
def home():
    return {"message": "hello! this is the book collection api"}

# fetch details about a book using its id
@app.get("/book/{book_id}")
def get_book(book_id: str):
    if book_id in books_data:
        return {"book_id": book_id, "details": books_data[book_id]}
    else:
        raise HTTPException(status_code=404, detail="book not found")

# list all available books
@app.get("/books")
def list_books():
    return {"books": books_data}

# find books by a specific author
@app.get("/books/author/{author}")
def get_books_by_author(author: str):
    result = {bid: info for bid, info in books_data.items() if info["author"].lower() == author.lower()}
    if result:
        return {"books_by_author": author, "details": result}
    else:
        raise HTTPException(status_code=404, detail="no books found by this author")
