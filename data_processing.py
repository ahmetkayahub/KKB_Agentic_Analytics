import os
import pandas as pd
import duckdb

def process_and_build_lakehouse():
    print("⏳ Aşama 2: Veri Hizalama ve DuckDB Lakehouse İşlemi Başlıyor...")
    
    # 1. Ham verileri oku
    df_tcmb = pd.read_csv("data/raw/tcmb_daily.csv")
    df_bddk = pd.read_csv("data/raw/bddk_monthly.csv")
    
    # Tarih formatlarını datetime'a çevir
    df_tcmb["tarih"] = pd.to_datetime(df_tcmb["tarih"])
    df_bddk["tarih"] = pd.to_datetime(df_bddk["tarih"])
    
    # 2. TCMB Günlük Verilerini Aylık Frekansa Çevir (Resampling)
    # Günlük dolar kuru ve faizin aylık ortalamasını alıyoruz ki aylık BDDK ile birleşebilsin.
    df_tcmb.set_index("tarih", inplace=True)
    df_tcmb_monthly = df_tcmb.resample("ME").mean().reset_index()
    
    # 3. BDDK Kümülatif Verisini Net Akışa Çevir (Kritik Mühendislik Adımı!)
    # Yıl başlarında sıfırlanan kümülatif veriden, aylık net değişimi (diff) hesaplıyoruz.
    df_bddk = df_bddk.sort_values("tarih")
    
    # Yıl bilgisini alarak her yılın kendi içindeki kümülatif artışını net akışa dönüştürelim
    df_bddk["yil"] = df_bddk["tarih"].dt.year
    
    # Eğer değer bir önceki aydan küçükse (Ocak sıfırlanması gibi) diff negatif çıkabilir, düzeltelim:
    # Basitçe pandas diff() alıp ilk aylardaki anomalileri temizliyoruz
    df_bddk["aylik_net_konut_kredisi_akisi"] = df_bddk["toplam_konut_kredisi_milyon_tl"].diff()
    # İlk ay için (Ocak 2021) NaN kalmasın diye direkt ilk değeri verelim
    df_bddk["aylik_net_konut_kredisi_akisi"].fillna(df_bddk["toplam_konut_kredisi_milyon_tl"].iloc[0], inplace=True)
    
    # 4. İki Veri Setini Tarih Üzerinden Birleştir (Merge)
    df_merged = pd.merge(df_bddk, df_tcmb_monthly, on="tarih", how="inner")
    
    # Sütun isimlerini düzenle
    df_merged = df_merged[["tarih", "toplam_konut_kredisi_milyon_tl", "aylik_net_konut_kredisi_akisi", "konut_fiyat_endeksi", "dolar_kuru", "politika_faizi"]]
    
    # İşlenmiş veriyi processed klasörüne CSV olarak da yedekleyelim
    os.makedirs("data/processed", exist_ok=True)
    df_merged.to_csv("data/processed/merged_financial_data.csv", index=False)
    print("✅ Temizlenmiş ve hizalanmış veri 'data/processed/merged_financial_data.csv' olarak kaydedildi.")
    
    # 5. DuckDB Lakehouse Kurulumu
    # DuckDB veritabanı dosyamızı oluşturuyoruz (Doğal dilde SQL sorguları buraya atılacak)
    db_path = "data/processed/lakehouse.db"
    conn = duckdb.connect(db_path)
    
    # Tabloyu DuckDB içine yaz
    conn.execute("CREATE OR REPLACE TABLE financial_lakehouse AS SELECT * FROM df_merged;")
    
    # Test sorgusu yapalım
    res = conn.execute("SELECT COUNT(*) FROM financial_lakehouse").fetchone()
    print(f"✅ DuckDB Lakehouse başarıyla oluşturuldu! Toplam Satır Sayısı: {res[0]}")
    
    conn.close()
    print("🎉 AŞAMA 2 TAMAMLANDI! Lakehouse kullanıma hazır.")

if __name__ == "__main__":
    process_and_build_lakehouse()
