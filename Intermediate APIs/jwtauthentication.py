from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI()

# Secret key for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock database
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": "$2b$12$WzDwLpO4FjP5g.T2mWmK0O9uUm3J6.Hyl1fO0elVbT7M4e7YI2PAK"  # password: secret
    }
}

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class UserIn(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    user = db.get(username)
    if user:
        return UserInDB(**user)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user