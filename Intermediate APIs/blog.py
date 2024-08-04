from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional

DATABASE_URL = "sqlite:///./blog.db"
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="posts")

User.posts = relationship("BlogPost", back_populates="owner")

class UserCreate(BaseModel):
    username: str
    password: str

class UserInDB(UserCreate):
    hashed_password: str

class BlogPostCreate(BaseModel):
    title: str
    content: str

class BlogPostOut(BlogPostCreate):
    id: int
    user_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

Base.metadata.create_all(bind=engine)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register", response_model=UserCreate)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: UserCreate, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/blog/", response_model=BlogPostOut)
async def create_blog_post(post: BlogPostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = BlogPost(**post.dict(), user_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/blog/", response_model=List[BlogPostOut])
async def read_blog_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = db.query(BlogPost).offset(skip).limit(limit).all()
    return posts

@app.put("/blog/{post_id}", response_model=BlogPostOut)
async def update_blog_post(post_id: int, post: BlogPostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id, BlogPost.user_id == current_user.id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/blog/{post_id}", response_model=dict)
async def delete_blog_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id, BlogPost.user_id == current_user.id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted"}