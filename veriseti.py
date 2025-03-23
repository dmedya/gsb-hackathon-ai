import pandas as pd
from faker import Faker
fake = Faker("tr_TR")
import random

fake = Faker()

takvim_data = []
for i in range(100):
    takvim_data.append([
        i+1, random.randint(100, 200), fake.date_this_year(), 
        f"{random.randint(8, 20)}:00", 
        random.choice(["Toplantı", "Seyahat", "Spor Etkinliği", "Eğitim"]),
        fake.sentence(), random.choice(["Aktif", "İptal"])
    ])

df_takvim = pd.DataFrame(takvim_data, columns=["Etkinlik_ID", "Kullanıcı_ID", "Tarih", "Saat", "Etkinlik_Türü", "Açıklama", "Durum"])
df_takvim.to_csv("takvim_verileri.csv", index=False)
print("Takvim veri seti oluşturuldu!")
