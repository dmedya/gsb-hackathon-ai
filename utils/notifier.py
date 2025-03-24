from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from models import Event, Agenda
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

scheduler = BackgroundScheduler(daemon=True)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "senin_emailin@gmail.com"
EMAIL_PASSWORD = "senin_sifren"

def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

def get_upcoming_events():
    db = SessionLocal()
    try:
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        return (db.query(Event)
                .join(Agenda)
                .filter(Event.start_time.between(now, tomorrow))
                .filter(Agenda.reminder_sent == False)
                .all())
    finally:
        db.close()

def send_reminders():
    db = SessionLocal()
    try:
        events = get_upcoming_events()
        for event in events:
            for agenda in event.agendas:
                user_email = agenda.user.email
                message = f"📢 Hatırlatma: Sayın {agenda.user.name}, '{event.name}' etkinliği yarın {event.start_time.strftime('%H:%M')}’da {event.location}’da!"
                print(message)
                send_email("Yaklaşan Etkinlik Hatırlatması", message, user_email)
                agenda.reminder_sent = True
        db.commit()
    except Exception as e:
        print(f"Hatırlatma gönderilirken hata: {str(e)}")
    finally:
        db.close()

scheduler.add_job(send_reminders, "interval", hours=1)

def start_notifier():
    if not scheduler.running:
        try:
            scheduler.start()
            print("🔔 Bildirim sistemi başlatıldı")
        except Exception as e:
            print(f"Bildirim sistemi başlatılırken hata: {str(e)}")
    else:
        print("⚠️ Bildirim sistemi zaten çalışıyor.")
