from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

DATABASE_URL = "sqlite:///./course_enrollment.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    students = relationship("Enrollment", back_populates="course")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    enrollments = relationship("Enrollment", back_populates="student")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    completed = Column(Boolean, default=False)
    course = relationship("Course", back_populates="students")
    student = relationship("Student", back_populates="enrollments")

Base.metadata.create_all(bind=engine)

class CourseCreate(BaseModel):
    title: str
    description: str

class StudentCreate(BaseModel):
    name: str

class EnrollmentCreate(BaseModel):
    course_id: int
    student_id: int

class CourseOut(BaseModel):
    id: int
    title: str
    description: str
    students: List[EnrollmentCreate] = []

class StudentOut(BaseModel):
    id: int
    name: str
    enrollments: List[EnrollmentCreate] = []

class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    student_id: int
    completed: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/courses/", response_model=CourseOut)
async def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.get("/courses/", response_model=List[CourseOut])
async def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@app.post("/students/", response_model=StudentOut)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=List[StudentOut])
async def list_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

@app.post("/enrollments/", response_model=EnrollmentOut)
async def enroll_student(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    db_enrollment = Enrollment(**enrollment.dict())
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@app.put("/enrollments/{enrollment_id}/complete/", response_model=EnrollmentOut)
async def complete_course(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    enrollment.completed = True
    db.commit()
    db.refresh(enrollment)
    return enrollment
