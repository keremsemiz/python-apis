from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import random

app = FastAPI()

devices_db: Dict[str, Dict] = {}

class Device(BaseModel):
    id: str
    name: str
    status: str

class DeviceUpdate(BaseModel):
    status: str

@app.post("/devices/", response_model=Device)
async def add_device(device: Device):
    if device.id in devices_db:
        raise HTTPException(status_code=400, detail="Device already exists")
    devices_db[device.id] = device.dict()
    return device

@app.get("/devices/", response_model=List[Device])
async def list_devices():
    return list(devices_db.values())

@app.get("/devices/{device_id}", response_model=Device)
async def get_device(device_id: str):
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices_db[device_id]

@app.put("/devices/{device_id}", response_model=Device)
async def update_device(device_id: str, update: DeviceUpdate):
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    devices_db[device_id]['status'] = update.status
    return devices_db[device_id]

@app.delete("/devices/{device_id}", response_model=dict)
async def delete_device(device_id: str):
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    del devices_db[device_id]
    return {"message": "Device deleted"}