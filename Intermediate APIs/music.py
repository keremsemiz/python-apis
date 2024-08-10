from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

DATABASE_URL = "sqlite:///./playlist.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    songs = relationship("Song", back_populates="playlist")

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String)
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    playlist = relationship("Playlist", back_populates="songs")

Base.metadata.create_all(bind=engine)

class PlaylistCreate(BaseModel):
    name: str
    description: str

class SongCreate(BaseModel):
    title: str
    artist: str

class PlaylistOut(BaseModel):
    id: int
    name: str
    description: str
    songs: List[SongCreate] = []

class SongOut(BaseModel):
    id: int
    title: str
    artist: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/playlists/", response_model=PlaylistOut)
async def create_playlist(playlist: PlaylistCreate, db: Session = Depends(get_db)):
    db_playlist = Playlist(name=playlist.name, description=playlist.description)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@app.get("/playlists/", response_model=List[PlaylistOut])
async def list_playlists(db: Session = Depends(get_db)):
    return db.query(Playlist).all()

@app.post("/playlists/{playlist_id}/songs/", response_model=SongOut)
async def add_song(playlist_id: int, song: SongCreate, db: Session = Depends(get_db)):
    db_playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    db_song = Song(title=song.title, artist=song.artist, playlist_id=playlist_id)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

@app.get("/playlists/{playlist_id}", response_model=PlaylistOut)
async def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    db_playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return db_playlist
