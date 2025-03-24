from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Event
import pandas as pd
import ollama
from datetime import datetime, timedelta
import joblib

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

# Model ve Vectorizer'ı global olarak yükleyelim
try:
    vectorizer = joblib.load("vectorizer.pkl")
    intent_model = joblib.load("intent_model.pkl")
    print("✅ Intent modeli yüklendi.")
except Exception as e:
    print(f"❌ Intent modeli yüklenemedi: {e}")
    vectorizer = None
    intent_model = None

def get_events_for_today(db_session: Session):
    """Bugünün etkinliklerini getirir (gün bazında aralık sorgusu ile)"""
    try:
        today_str = datetime.today().strftime("%Y-%m-%d")
        day_start = datetime.strptime(today_str, "%Y-%m-%d")  # Bugün 00:00:00
        day_end = day_start + timedelta(days=1)                # Ertesi gün 00:00:00
        events = db_session.query(Event).filter(
            Event.date >= day_start,
            Event.date < day_end
        ).all()
        return events
    except Exception as e:
        print(f"⚠️ Veritabanı hatası: {e}")
        return []

def get_response_from_csv(user_message: str) -> str:
    """intents.csv dosyasından doğrudan mesajla eşleşen yanıtı döndürür."""
    try:
        df = pd.read_csv("intents.csv", encoding="utf-8")
        row = df[df["text"].str.lower() == user_message.lower()]
        if not row.empty:
            return row.iloc[0]["response"]
    except Exception as e:
        print(f"⚠️ CSV Okuma Hatası: {e}")
    return None

def classify_with_model(user_message: str):
    """SVM modeliyle intent sınıflandırması yapar ve (tahmin, güven) döndürür."""
    if not intent_model or not vectorizer:
        return None, 0.0

    X = vectorizer.transform([user_message])
    predicted_intent = intent_model.predict(X)[0]
    probabilities = intent_model.predict_proba(X)[0]
    confidence = max(probabilities)
    return predicted_intent, confidence

@router.post("/respond", tags=["Chatbot"])
def chatbot_response(request: ChatRequest, db: Session = Depends(get_db)):
    user_message = request.message.lower().strip()
    print("\n=== YENİ MESAJ ===")
    print(f"📩 Gelen mesaj: {user_message}")

    try:
        # 1️⃣ Öncelikle takvim sorgusu kontrolü
        if any(kw in user_message for kw in ["takvim", "ajandam", "izin"]):
            events = get_events_for_today(db)
            if events:
                event_texts = "\n".join([f"- {evt.name} ({evt.start_time})" for evt in events])
                print("📅 Takvim verileri alındı.")
                return {"response": f"📅 Bugünkü etkinlikler:\n{event_texts}"}
            else:
                print("📅 Bugün için etkinlik bulunamadı.")
                # Takvim sorgusu var ama veri yoksa devam ediyoruz, model kontrol edilecek.
        
        # 2️⃣ Model ile intent sınıflandırması
        predicted_intent, confidence = classify_with_model(user_message)
        print(f"🔍 Model Tahmini: {predicted_intent}, Güven: {confidence:.2f}")
        threshold = 0.50  # Güven eşiği

        if confidence >= threshold:
            # Intent'e göre yanıtları belirleyin
            intent_responses = {
                "izin_sorgulama": "Takviminizde izin bilgisi bulunuyor: [Detaylı veriler].",
                "etkinlik_ekleme": "Etkinlik ekleme işlemi için lütfen gerekli bilgileri giriniz.",
                # Diğer intent'ler ve yanıtlar...
            }
            if predicted_intent in intent_responses:
                return {"response": intent_responses[predicted_intent]}
        
        # 3️⃣ Modelden yeterli yanıt alınamadıysa CSV'den yanıt arayalım
        csv_response = get_response_from_csv(user_message)
        if csv_response:
            print(f"✅ CSV yanıtı: {csv_response}")
            return {"response": csv_response}

        # 4️⃣ Son çare olarak LLM (Ollama) kullanımı
        print("🤖 LLM'e yönlendiriliyor...")
        try:
            ollama_response = ollama.chat("mistral", [{"role": "user", "content": user_message}])
            print(f"🔵 LLM Ham Yanıt: {ollama_response}")
            if ollama_response and isinstance(ollama_response, dict):
                llm_response = ollama_response.get("message", {}).get("content", "").strip()
                if llm_response:
                    return {"response": llm_response}
        except Exception as e:
            print(f"⚠️ LLM Hatası: {e}")

        return {"response": "Üzgünüm, bu konuda yardımcı olamıyorum."}

    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        return {"response": f"Bir hata oluştu: {str(e)}"}
