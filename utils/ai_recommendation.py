from database import SessionLocal
from models import Agenda, Event
from collections import Counter
from typing import List, Dict, Optional
from datetime import datetime, timedelta

def get_user_preferences(user_id: int) -> Optional[str]:
    db = SessionLocal()
    try:
        # Son 3 aya ait etkinlikleri al
        three_months_ago = datetime.now() - timedelta(days=90)
        events = (
            db.query(Agenda)
            .join(Event)
            .filter(Agenda.user_id == user_id)
            .filter(Event.date >= three_months_ago)
            .all()
        )
        
        categories = [e.event.category for e in events]
        category_counts = Counter(categories)
        
        if not category_counts:
            return None
        
        most_frequent_category = category_counts.most_common(1)[0][0]
        return most_frequent_category
    finally:
        db.close()

def get_recommended_events(user_id: int) -> List[Dict]:
    db = SessionLocal()
    try:
        preferred_category = get_user_preferences(user_id)
        
        if not preferred_category:
            return []

        # Gelecek etkinlikleri al
        now = datetime.now()
        recommended_events = (
            db.query(Event)
            .filter(Event.category == preferred_category)
            .filter(Event.date >= now)
            .order_by(Event.date)
            .limit(5)
            .all()
        )
        
        return [
            {
                "id": e.id,
                "name": e.name,
                "date": e.date.strftime("%Y-%m-%d %H:%M"),
                "location": e.location,
                "category": e.category,
                "description": e.description
            } 
            for e in recommended_events
        ]
    finally:
        db.close()
