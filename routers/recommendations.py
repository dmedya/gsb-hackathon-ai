from fastapi import APIRouter, HTTPException
from database import SessionLocal
from models import User, Event

router = APIRouter()

@router.get("/")
def get_recommendations(user_id: int, location: str = None):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    query = db.query(Event).filter(Event.category == user.interest)
    if location:
        query = query.filter(Event.location == location)
    recommended_events = query.all()
    return {"recommendations": [{"event_name": e.name, "date": e.date, "location": e.location} for e in recommended_events]}

@router.get("/popular/")
def get_popular_events():
    db = SessionLocal()
    popular_events = db.query(Event).order_by(Event.popularity.desc()).limit(5).all()
    return {"popular_events": [{"name": e.name, "date": e.date, "location": e.location, "popularity": e.popularity} for e in popular_events]}
