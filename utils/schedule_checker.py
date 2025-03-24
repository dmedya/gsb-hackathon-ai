from datetime import datetime, timedelta
from database import SessionLocal
from models import Agenda, Event

def find_free_time(user_id):
    db = SessionLocal()
    agenda = db.query(Agenda).filter(Agenda.user_id == user_id).all()
    now = datetime.now()
    upcoming_events = [e.event.date for e in agenda if e.event.date > now]
    if not upcoming_events:
        return "Ajandanızda yaklaşan etkinlik yok, istediğiniz zaman etkinlik ekleyebilirsiniz."
    upcoming_events.sort()
    free_time_slots = []
    for i in range(len(upcoming_events) - 1):
        gap = upcoming_events[i + 1] - upcoming_events[i]
        if gap > timedelta(hours=2):
            free_time_slots.append((upcoming_events[i], upcoming_events[i + 1]))
    if not free_time_slots:
        return "Boş zaman aralığınız bulunamadı."
    return free_time_slots
