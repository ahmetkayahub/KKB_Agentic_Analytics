import duckdb
import pandas as pd
import numpy as np

DB_PATH = "data/processed/lakehouse.db"

def query_lakehouse(sql_query: str) -> pd.DataFrame:
    """DuckDB Lakehouse üzerinden güvenli SQL sorgusu çalıştırır."""
    conn = duckdb.connect(DB_PATH, read_only=True)
    df = conn.execute(sql_query.strip()).fetchdf()
    conn.close()
    return df

def get_financial_summary() -> str:
    """Genel finansal veri setinin özet istatistiklerini döner."""
    query = "SELECT * FROM financial_lakehouse"
    df = query_lakehouse(query)
    
    summary = f"Veri Aralığı: {df['tarih'].min()} ile {df['tarih'].max()} arası.\n"
    summary += f"Toplam Ay Sayısı: {len(df)}\n"
    summary += f"Ortalama Dolar Kuru: {df['dolar_kuru'].mean():.2f} TL\n"
    summary += f"Ortalama Politika Faizi: %{df['politika_faizi'].mean():.2f}\n"
    return summary

def detect_anomalies_in_credits() -> str:
    """
    Konut kredisi net akışındaki anormal sıçramaları (anomalileri) tespit eder.
    Jürinin 'Beklenmeyen piyasa şoklarını bul' senaryosu için kritik araçtır.
    """
    df = query_lakehouse("SELECT tarih, aylik_net_konut_kredisi_akisi FROM financial_lakehouse")
    
    # Basit ve etkili bir Z-Score tabanlı anomali tespiti (Ortalamadan 2 standart sapma sapanlar)
    mean = df['aylik_net_konut_kredisi_akisi'].mean()
    std = df['aylik_net_konut_kredisi_akisi'].std()
    
    df['z_score'] = (df['aylik_net_konut_kredisi_akisi'] - mean) / std
    anomalies = df[abs(df['z_score']) > 2.0]
    
    if anomalies.empty:
        return "Belirtilen dönemde kredi hacminde istatistiki bir anomali (aşırı sapma) bulunamadı."
    
    result = "🔍 Tespit Edilen Kredi Hacmi Anomalileri (Piyasa Şokları):\n"
    for _, row in anomalies.iterrows():
        tarih_str = str(row['tarih'])[:10]
        result += f"- Tarih: {tarih_str} | Net Kredi Akışı: {row['aylik_net_konut_kredisi_akisi']:,.0f} milyon TL (Z-Skor: {row['z_score']:.2f})\n"
        
    return result

if __name__ == "__main__":
    print("🛠️ Analytics Tools Test Ediliyor...\n")
    print(get_financial_summary())
    print("-" * 40)
    print(detect_anomalies_in_credits())
