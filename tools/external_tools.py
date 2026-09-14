import requests
from bs4 import BeautifulSoup
import os

def search_financial_web(query: str) -> str:
    """
    Finansal terimler veya güncel ekonomik gelişmeler hakkında web arama aracı.
    """
    print(f"🌐 Web araması simülasyonu yapılıyor: {query}")
    if "faiz" in query.lower():
        return "TCMB son kararlarına göre politika faizi makroekonomik dengeyi gözetmektedir."
    elif "bddk" in query.lower():
        return "BDDK bültenlerine göre bankacılık sektörünün kredi hacmi düzenli olarak raporlanmaktadır."
    else:
        return f"'{query}' ile ilgili finansal veri kaynaklarında güncel bilgi tarandı."

def read_pdf_report(pdf_path: str) -> str:
    """
    İndirilen PDF raporlarını okuyarak ajan için metne dönüştürür.
    """
    if not os.path.exists(pdf_path):
        return f"⚠️ Belirtilen yolda ({pdf_path}) PDF dosyası bulunamadı."
    
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text[:3000]
    except Exception as e:
        return f"❌ PDF okuma hatası: {e}"

if __name__ == "__main__":
    print("🌍 External Tools Test Ediliyor...")
    print(search_financial_web("TCMB faiz oranları"))
