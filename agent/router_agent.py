import os
import sys

# Proje kök dizinini Python yoluna ekle (ModuleNotFoundError hatasını önler)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tools.analytics_tools import get_financial_summary, detect_anomalies_in_credits
from tools.external_tools import search_financial_web

# .env dosyasındaki Kloudeks API anahtarını yüklüyoruz
load_dotenv()

KLOUDEKS_API_KEY = os.getenv("KLOUDEKS_API_KEY")
KLOUDEKS_BASE_URL = os.getenv("KLOUDEKS_BASE_URL", "https://api.kloudeks.kkb.com.tr/v1")

def get_kloudeks_llm():
    """
    Kloudeks platformu üzerinden açık kaynaklı LLM modeline bağlanır.
    """
    llm = ChatOpenAI(
        api_key=KLOUDEKS_API_KEY,
        base_url=KLOUDEKS_BASE_URL,
        model="qwen-1.5-32b",
        temperature=0.1
    )
    return llm

def run_agentic_workflow(user_query: str) -> str:
    """
    Kullanıcı sorgusunu analiz eden ve uygun aracı seçerek yanıt üreten akıllı ajan fonksiyonu.
    """
    print(f"🤖 Agent işleme başladı. Kullanıcı Sorusu: '{user_query}'")
    
    query_lower = user_query.lower()
    
    if "anomali" in query_lower or "şok" in query_lower or "sıçrama" in query_lower:
        print("🛠️ Ajan 'Anomali Tespiti' aracını seçti.")
        tool_result = detect_anomalies_in_credits()
    elif "özet" in query_lower or "genel" in query_lower or "istatistik" in query_lower:
        print("🛠️ Ajan 'Finansal Özet' aracını seçti.")
        tool_result = get_financial_summary()
    elif "faiz" in query_lower or "bddk" in query_lower or "haber" in query_lower:
        print("🛠️ Ajan 'Web/Dış Kaynak' aracını seçti.")
        tool_result = search_financial_web(user_query)
    else:
        print("🛠️ Ajan doğrudan veri özeti aracını varsayılan olarak seçti.")
        tool_result = get_financial_summary()
        
    try:
        llm = get_kloudeks_llm()
        prompt = f"""
        Sen profesyonel bir Finansal Veri Analitiği Asistanısın. KKB/BDDK/TCMB verilerini yorumluyorsun.
        Kullanıcının Sorusu: {user_query}
        
        Arka planda çalıştırılan araçtan gelen ham veri/sonuç:
        {tool_result}
        
        Lütfen bu veriyi kullanarak kullanıcıya profesyonel, anlaşılır ve analitik bir Türkçe yanıt ver.
        """
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"⚠️ Kloudeks LLM bağlantı uyarısı: {e}\n\nElde edilen Ham Araç Sonucu:\n{tool_result}"

if __name__ == "__main__":
    print("🧠 Router Agent Test Ediliyor...\n" + "-"*40)
    print(run_agentic_workflow("Kredi hacmindeki anomalileri ve piyasa şoklarını analiz eder misin?"))
