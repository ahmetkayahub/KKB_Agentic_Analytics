import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Proje yollarını sisteme tanıt
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from agent.router_agent import run_agentic_workflow
from tools.analytics_tools import query_lakehouse

# Sayfa Konfigürasyonu
st.set_page_config(
    page_title="Agentic Data Analytics | KKB Hackathon",
    page_icon="📈",
    layout="wide"
)

st.title("🤖 Agentic Data Analytics & Finansal Zeka Platformu")
st.markdown("---")

# Yan Menü (Sidebar)
st.sidebar.header("⚙️ Kontrol Paneli")
page = st.sidebar.selectbox("Görünüm Seçin", ["Genel Bakış & Grafikler", "Akıllı Ajan (AI Asistan)"])

# Veriyi Lakehouse'dan Çek
@st.cache_data
def load_data():
    return query_lakehouse("SELECT * FROM financial_lakehouse ORDER BY tarih")

try:
    df = load_data()
except Exception as e:
    st.error(f"Veritabanı yüklenirken hata oluştu: {e}")
    df = pd.DataFrame()

if page == "Genel Bakış & Grafikler":
    st.subheader("📊 TCMB & BDDK Entegre Finansal Lakehouse Görselleştirmesi")
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Veri Periyodu", f"{len(df)} Ay")
        col2.metric("Ortalama Dolar Kuru", f"{df['dolar_kuru'].mean():.2f} TL")
        col3.metric("Ortalama Politika Faizi", f"%{df['politika_faizi'].mean():.2f}")
        
        st.markdown("---")
        
        # Grafik 1: Kredi Hacmi Net Akışı ve Anomaliler
        fig_credit = px.line(df, x='tarih', y='aylik_net_konut_kredisi_akisi', 
                             title="Aylık Net Konut Kredisi Akışı (Kümülatiften Arındırılmış)",
                             labels={'aylik_net_konut_kredisi_akisi': 'Net Akış (Milyon TL)', 'tarih': 'Tarih'})
        st.plotly_chart(fig_credit, use_container_width=True)
        
        # Grafik 2: Dolar Kuru ve Faiz Trendi
        fig_macro = px.line(df, x='tarih', y=['dolar_kuru', 'politika_faizi'],
                            title="TCMB Makroekonomik Göstergeler (Dolar Kuru & Politika Faizi)",
                            labels={'value': 'Oran / Kur', 'tarih': 'Tarih', 'variable': 'Gösterge'})
        st.plotly_chart(fig_macro, use_container_width=True)
    else:
        st.warning("Lakehouse verisi henüz bulunamadı. Lütfen veri işleme adımını çalıştırın.")

elif page == "Akıllı Ajan (AI Asistan)":
    st.subheader("💬 Finansal Analitik AI Asistanı ile Sohbet Et")
    st.markdown("Jüri senaryolarına uygun sorular sorabilir, ajanımızın arka plandaki araçları nasıl seçtiğini şeffafça görebilirsiniz.")
    
    user_input = st.text_input("Örn: 'Kredi hacmindeki anomalileri ve piyasa şoklarını analiz eder misin?'")
    
    if st.button("Analiz Et & Yanıtla"):
        if user_input:
            with st.spinner("Yapay zeka ajanı verileri inceliyor ve araçları çalıştırıyor..."):
                response = run_agentic_workflow(user_input)
            
            st.markdown("### 🤖 Ajanın Analiz Raporu:")
            st.success(response)
        else:
            st.warning("Lütfen bir soru yazın.")
