from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List
from datetime import date

DATABASE_URL = "sqlite:///./property_management.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    tenants = relationship("Tenant", back_populates="property")

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)
    property_id = Column(Integer, ForeignKey("properties.id"))
    lease_start = Column(Date)
    lease_end = Column(Date)
    is_active = Column(Boolean, default=True)
    property = relationship("Property", back_populates="tenants")

Base.metadata.create_all(bind=engine)

class PropertyCreate(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str

class TenantCreate(BaseModel):
    name: str
    email: str
    property_id: int
    lease_start: date
    lease_end: date

class PropertyOut(BaseModel):
    id: int
    address: str
    city: str
    state: str
    zip_code: str
    tenants: List[TenantCreate] = []

class TenantOut(BaseModel):
    id: int
    name: str
    email: str
    lease_start: date
    lease_end: date
    is_active: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/properties/", response_model=PropertyOut)
async def add_property(property: PropertyCreate, db: Session = Depends(get_db)):
    db_property = Property(**property.dict())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

@app.get("/properties/", response_model=List[PropertyOut])
async def list_properties(db: Session = Depends(get_db)):
    return db.query(Property).all()

@app.post("/tenants/", response_model=TenantOut)
async def add_tenant(tenant: TenantCreate, db: Session = Depends(get_db)):
    db_tenant = Tenant(**tenant.dict())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

@app.get("/tenants/", response_model=List[TenantOut])
async def list_tenants(db: Session = Depends(get_db)):
    return db.query(Tenant).all()

@app.put("/tenants/{tenant_id}/deactivate/", response_model=TenantOut)
async def deactivate_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.is_active = False
    db.commit()
    db.refresh(tenant)
    return tenant
