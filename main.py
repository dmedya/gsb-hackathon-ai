import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse  
from database import Base, engine
from routers import users, events, recommendations, chatbot
from utils.notifier import start_notifier
from fastapi.middleware.cors import CORSMiddleware
from db_setup import load_sql_dump

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanını oluştur
Base.metadata.create_all(bind=engine)

# Dump dosyasının yolu (gerekirse)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dump_file_path = os.path.join(BASE_DIR, "gsb_chatbot.sql")
load_sql_dump(dump_file_path)

# Notifier başlat
start_notifier()

# Statik dosya servisi
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/")
def root():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))

# API Rotalarını Dahil Et
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(chatbot.router, prefix="/chat", tags=["Chatbot"])  # 🔥 Burada "/chat" kaldırıldı!
