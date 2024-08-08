from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

DATABASE_URL = "sqlite:///./quizzes.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    questions = relationship("Question", back_populates="quiz")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    answer = Column(String)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    quiz = relationship("Quiz", back_populates="questions")

Base.metadata.create_all(bind=engine)

class QuestionCreate(BaseModel):
    text: str
    answer: str

class QuizCreate(BaseModel):
    title: str
    description: str
    questions: List[QuestionCreate]

class QuestionOut(BaseModel):
    id: int
    text: str
    answer: str

class QuizOut(BaseModel):
    id: int
    title: str
    description: str
    questions: List[QuestionOut]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/quizzes/", response_model=QuizOut)
async def create_quiz(quiz: QuizCreate, db: Session = Depends(get_db)):
    db_quiz = Quiz(title=quiz.title, description=quiz.description)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    for question in quiz.questions:
        db_question = Question(text=question.text, answer=question.answer, quiz_id=db_quiz.id)
        db.add(db_question)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

@app.get("/quizzes/", response_model=List[QuizOut])
async def read_quizzes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Quiz).offset(skip).limit(limit).all()

@app.put("/quizzes/{quiz_id}", response_model=QuizOut)
async def update_quiz(quiz_id: int, quiz: QuizCreate, db: Session = Depends(get_db)):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    db_quiz.title = quiz.title
    db_quiz.description = quiz.description
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

@app.delete("/quizzes/{quiz_id}", response_model=dict)
async def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if db_quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    db.delete(db_quiz)
    db.commit()
    return {"message": "Quiz deleted"}