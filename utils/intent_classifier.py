import joblib

vectorizer = joblib.load("vectorizer.pkl")
model = joblib.load("intent_model.pkl")

def classify_intent(user_message: str) -> str:
    X_input = vectorizer.transform([user_message])
    predicted_intent = model.predict(X_input)[0]
    confidence_score = model.predict_proba(X_input)[0][predicted_intent]
    
    try:
        if confidence_score < 0.5:
            return None
        
        return predicted_intent
    except:
        return None

if __name__ == "__main__":
    test_message = "takvimimde etkinlik ekle 12-03-2025 maç"
    intent = classify_intent(test_message)
    print("Tahmin edilen intent:", intent)
