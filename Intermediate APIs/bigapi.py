from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional
import httpx
import asyncio

DATABASE_URL = "sqlite:///./project_management.db"
SECRET_KEY = "/.env"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
API_KEY = "/.env"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    tasks = relationship("Task", back_populates="project")
    owner = relationship("User", back_populates="projects")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="tasks")

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    project_id: int

class Weather(BaseModel):
    city: str
    temperature: float
    description: str

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


async def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }
        return weather

@app.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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

@app.post("/projects/", response_model=ProjectOut)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_project = Project(**project.dict(), owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    await manager.broadcast(f"New project created: {db_project.name}")
    return db_project

@app.get("/projects/", response_model=List[ProjectOut])
async def read_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects

@app.post("/tasks/", response_model=TaskOut)
async def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    await manager.broadcast(f"New task created: {db_task.title}")
    return db_task

@app.get("/tasks/", response_model=List[TaskOut])
async def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Notification: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/weather/{city}", response_model=Weather)
async def get_weather_info(city: str):
    weather = await get_weather(city)
    if not weather:
        raise HTTPException(status_code=404, detail="City not found")
    return weather