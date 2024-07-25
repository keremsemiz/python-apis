from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

class Venue(BaseModel):
    id: int
    name: str
    address: str
    capacity: int

class Participant(BaseModel):
    id: int
    name: str
    email: str
    event_id: int

class Event(BaseModel):
    id: int
    title: str
    description: str
    venue_id: int
    date: str
    time: str
    participants: Optional[List[Participant]] = []

venues: Dict[int, Venue] = {}
events: Dict[int, Event] = {}
participants: Dict[int, Participant] = {}

venues[1] = Venue(id=1, name="Conference Hall A", address="123 Main St", capacity=100)
venues[2] = Venue(id=2, name="Open Air Theater", address="456 Park Ave", capacity=500)

events[1] = Event(id=1, title="Tech Conference 2024", description="A conference on emerging technologies.",
                  venue_id=1, date="2024-10-20", time="10:00", participants=[])
events[2] = Event(id=2, title="Music Festival", description="A day-long festival featuring live music.",
                  venue_id=2, date="2024-11-15", time="12:00", participants=[])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Event Management API"}

# Venue Endpoints
@app.post("/venues/", response_model=Venue)
def create_venue(venue: Venue):
    if venue.id in venues:
        raise HTTPException(status_code=400, detail="Venue with this ID already exists")
    venues[venue.id] = venue
    return venue

@app.get("/venues/{venue_id}", response_model=Venue)
def get_venue(venue_id: int):
    if venue_id in venues:
        return venues[venue_id]
    else:
        raise HTTPException(status_code=404, detail="Venue not found")

@app.get("/venues/", response_model=List[Venue])
def list_venues():
    return list(venues.values())

# Event Endpoints
@app.post("/events/", response_model=Event)
def create_event(event: Event):
    if event.id in events:
        raise HTTPException(status_code=400, detail="Event with this ID already exists")
    if event.venue_id not in venues:
        raise HTTPException(status_code=404, detail="Venue not found")
    events[event.id] = event
    return event

@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: int):
    if event_id in events:
        return events[event_id]
    else:
        raise HTTPException(status_code=404, detail="Event not found")

@app.get("/events/", response_model=List[Event])
def list_events():
    return list(events.values())

@app.get("/events/venue/{venue_id}", response_model=List[Event])
def list_events_by_venue(venue_id: int):
    result = [event for event in events.values() if event.venue_id == venue_id]
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="No events found for this venue")

@app.post("/participants/", response_model=Participant)
def register_participant(participant: Participant):
    if participant.id in participants:
        raise HTTPException(status_code=400, detail="Participant with this ID already exists")
    if participant.event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    participants[participant.id] = participant
    events[participant.event_id].participants.append(participant)
    return participant

@app.get("/participants/{participant_id}", response_model=Participant)
def get_participant(participant_id: int):
    if participant_id in participants:
        return participants[participant_id]
    else:
        raise HTTPException(status_code=404, detail="Participant not found")

@app.get("/participants/", response_model=List[Participant])
def list_participants():
    return list(participants.values())

@app.get("/participants/event/{event_id}", response_model=List[Participant])
def list_participants_by_event(event_id: int):
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    return events[event_id].participants
