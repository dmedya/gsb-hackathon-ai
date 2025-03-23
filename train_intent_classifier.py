import pandas as pd
import numpy as np
import nltk
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from nltk.corpus import stopwords
import string

# Stopwords indir
nltk.download("stopwords")
stop_words = set(stopwords.words("turkish"))

def clean_text(text):
    """
    Metni temizler: Küçük harfe çevirme, noktalama temizleme, fazla stopwords kaldırma
    """
    if pd.isna(text): return ""  # Boş verileri koru
    text = text.lower()
    text = ''.join([char for char in text if char not in string.punctuation])  # Noktalama temizle
    text = ' '.join([word for word in text.split() if word not in stop_words])  # Stopwords azalt
    return text

def main():
    # 1️⃣ Veri Setini Yükle
    df = pd.read_csv("intents.csv")

    # 2️⃣ Temizleme ve Boşluk Kontrolü
    df.dropna(subset=["text", "intent"], inplace=True)  # Boş satırları temizle
    df["text"] = df["text"].apply(clean_text)  # Metinleri temizle
    df = df[df["text"].str.strip() != ""]  # Boş kalanları çıkar

    # 3️⃣ Veri Dengesi
    label_counts = df["intent"].value_counts()
    min_samples = max(3, label_counts.min())  # En az 3 örnek olmalı
    balanced_df = df.groupby("intent", group_keys=False).apply(lambda x: x.sample(n=min_samples, replace=True))

    # 4️⃣ Eğitim ve Test Bölme
    X_train, X_test, y_train, y_test = train_test_split(
        balanced_df["text"], balanced_df["intent"], test_size=0.2, random_state=42
    )

    # 5️⃣ Vectorizer (TF-IDF yerine CountVectorizer)
    vectorizer = CountVectorizer(ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # 6️⃣ Model Eğitimi (SVM)
    model = SVC(kernel="linear", probability=True)
    model.fit(X_train_vec, y_train)

    # 7️⃣ Test ve Sonuç
    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Model doğruluğu: {acc * 100:.2f}%")

    # 8️⃣ Modeli Kaydetme
    joblib.dump(vectorizer, "vectorizer.pkl")
    joblib.dump(model, "intent_model.pkl")
    print("📌 Model başarıyla eğitildi ve kaydedildi!")

if __name__ == "__main__":
    main()
