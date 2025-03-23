import psycopg2
import os

db_params = {
    "dbname": "gsb_chatbot",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": "5432"
}

def load_sql_dump(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"❌ Hata: {file_path} dosyası bulunamadı!")
            return

        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        with open(file_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Eğer dosya tamamen boşsa, örnek bir sorgu ekleyebilirsiniz:
        if not sql_script.strip():
            sql_script = "CREATE TABLE IF NOT EXISTS dummy_table (id SERIAL PRIMARY KEY);"
        
        for statement in sql_script.split(";"):
            if statement.strip():
                cur.execute(statement)

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Veritabanı başarıyla yüklendi!")
    except Exception as e:
        print("❌ Hata oluştu:", e)
