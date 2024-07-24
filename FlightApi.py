from fastapi import FastAPI, HTTPException
from typing import List, Dict

app = FastAPI()

# some mock data for flights
flights_data = {
    "NYC123": {"from": "New York", "to": "Los Angeles", "duration": "6h", "status": "on time"},
    "LA456": {"from": "Los Angeles", "to": "Chicago", "duration": "4h", "status": "delayed"},
    "CHI789": {"from": "Chicago", "to": "New York", "duration": "2h", "status": "on time"}
}

@app.get("/")
def read_root():
    return {"message": "welcome to the flight api!"}

# get info about a flight by its id
@app.get("/flight/{flight_id}")
def get_flight_info(flight_id: str):
    if flight_id in flights_data:
        return {"flight_id": flight_id, "details": flights_data[flight_id]}
    else:
        raise HTTPException(status_code=404, detail="flight not found")

# get all flights
@app.get("/flights")
def get_all_flights():
    return {"flights": flights_data}

# get flights by departure city
@app.get("/flights/from/{city}")
def get_flights_from_city(city: str):
    results = {fid: details for fid, details in flights_data.items() if details["from"].lower() == city.lower()}
    if results:
        return {"flights_from": city, "details": results}
    else:
        raise HTTPException(status_code=404, detail="no flights from this city")

# get flights by arrival city
@app.get("/flights/to/{city}")
def get_flights_to_city(city: str):
    results = {fid: details for fid, details in flights_data.items() if details["to"].lower() == city.lower()}
    if results:
        return {"flights_to": city, "details": results}
    else:
        raise HTTPException(status_code=404, detail="no flights to this city")
