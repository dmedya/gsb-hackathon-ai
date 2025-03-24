from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Event, EventCategory
from datetime import datetime

router = APIRouter()

class EventCreate(BaseModel):
    title: str
    date: str
    start_time: str

@router.post("/add_event")
def add_event(event: EventCreate, db: Session = Depends(get_db)):
    try:
        parsed_date = datetime.strptime(event.date, "%Y-%m-%d")
        new_event = Event(
            name=event.title,
            date=parsed_date,
            start_time=event.start_time,
            category=EventCategory.DIGER
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return {"message": f"{event.date} tarihine '{event.title}' etkinliği eklendi!", "id": new_event.id}
    except ValueError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Tarih formatı hatalı. 'YYYY-MM-DD' şeklinde giriniz.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{date}")
def get_events(date: str, db: Session = Depends(get_db)):
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        events = db.query(Event).filter(Event.date == parsed_date).all()
        return events
    except ValueError:
        raise HTTPException(status_code=400, detail="Tarih formatı hatalı.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    evt = db.query(Event).filter(Event.id == event_id).first()
    if not evt:
        raise HTTPException(status_code=404, detail="Etkinlik bulunamadı")
    db.delete(evt)
    db.commit()
    return {"message": "Etkinlik silindi"}
