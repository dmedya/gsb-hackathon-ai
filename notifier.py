from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from models import Event
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

scheduler = BackgroundScheduler()

def send_reminders():
    """Yaklaşan etkinlikler için hatırlatma gönderir."""
    db = SessionLocal()
    now = datetime.now()
    events = db.query(Event).filter(Event.date == now.date()).all()

    for event in events:
        event_time = datetime.strptime(event.start_time, "%H:%M")
        if (event_time - now).total_seconds() / 60 < 60:  # 1 saatten az kaldıysa
            print(f"Hatırlatma: {event.name} etkinliğin 1 saat içinde başlayacak!")

    db.close()

scheduler.add_job(send_reminders, "interval", minutes=30)  # Her 30 dakikada bir kontrol et
scheduler.start()
