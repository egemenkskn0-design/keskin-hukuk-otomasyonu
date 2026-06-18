import streamlit as st
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
from datetime import datetime
import sqlite3
import hashlib

# =====================================================================
# GÜVENLİ VERİ TABANI ALTYAPISI
# =====================================================================
def hash_sifre(sifre):
    return hashlib.sha256(sifre.encode()).hexdigest()

def veri_tabani_hazirla():
    conn = sqlite3.connect("hukuk_otomasyon.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS admin_auth (id INTEGER PRIMARY KEY, password_hash TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yeni_kontratlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, tarih TEXT, kiralayan TEXT, kiralayan_tc TEXT, 
            kiralayan_adres TEXT, kiralayan_iban TEXT, kiraci TEXT, kiraci_tc TEXT, kiraci_adres TEXT, 
            cins TEXT, bedel REAL, para_birimi TEXT, depozito INTEGER, artis INTEGER, baslangic TEXT, odeme_gunu INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eski_kontratlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, islem_tarihi TEXT, kiralayan TEXT, kiraci TEXT, 
            baslangic_tarihi TEXT, aylik_bedel REAL, para_birimi TEXT, dosya_adi TEXT, notlar TEXT
        )
    """)
    conn.commit()
    conn.close()

veri_tabani_hazirla()

st.set_page_config(page_title="Keskin Hukuk Bürosu", page_icon="⚖️", layout="wide")

st.sidebar.markdown("### 🏛️ Keskin Hukuk Portalı")
islem_tipi = st.sidebar.radio(
    "Lütfen Durumunuza Uygun Seçeneği İşaretleyin:",
    ["✨ Sıfırdan Kira Sözleşmesi Hazırlatmak İstiyorum", 
     "📂 Elimde İmzalanmış Mevcut Bir Sözleşme Var",
     "🔒 Avukat Yönetim Paneli (Sadece Ofis İçi Giriş)"]
)

# =====================================================================
# SENARYO 1: SIFIRDAN KİRA SÖZLEŞMESİ
# =====================================================================
if islem_tipi == "✨ Sıfırdan Kira Sözleşmesi Hazırlatmak İstiyorum":
    st.title("⚖️ Keskin Hukuk Bürosu - Dijital Bilgi Portalı")
    st.subheader("📋 Sıfırdan Sözleşme Üretim Formu")
    
    col1, col2 = st.columns(2)
    with col1:
        kiralayan_ad = st.text_input("Adı Soyadı / Unvanı", key="y_k_ad")
        kiralayan_tc = st.text_input("T.C. Kimlik No / Vergi No", key="y_k_tc")
        kiralayan_adres = st.text_area("Resmi Tebligat Adresi", key="y_k_adr")
        kiralayan_iban = st.text_input("IBAN Numarası", key="y_k_iban")
    with col2:
        kiraci_ad = st.text_input("Adı Soyadı / Şirket Unvanı", key="y_kr_ad")
        kiraci_tc = st.text_input("T.C. Kimlik / Pasaport / Vergi No", key="y_kr_tc")
        kiraci_adres = st.text_area("Kiracının İkametgah Adresi", key="y_kr_adr")

    col3, col4 = st.columns(2)
    with col3:
        gayrimenkul_turu = st.selectbox("Kiralanan Taşınmazın Cinsi", ["Konut", "Çatılı İşyeri", "Arsa/Arazi"])
        kira_bedeli_aylik = st.number_input("Aylık Kira Bedeli", min_value=0, value=20000, step=500)
        para_birimi = st.selectbox("Para Birimi", ["TL (₺)", "USD ($)", "EUR (€)"])
        depozito_ay_sayisi = st.slider("Güvence Bedeli (Kaç Aylık Kira?)", min_value=0, max_value=12, value=2)
        
        if gayrimenkul_turu in ["Konut", "Çatılı İşyeri"] and depozito_ay_sayisi > 3:
            st.error("⚠️ Türk Borçlar Kanunu md. 342 uyarınca, güvence bedeli 3 aylık kira bedelini aşamaz.")

    with col4:
        sozlesme_artis_orani = st.slider("Yeni Dönem Yıllık Artış Oranı (%)", min_value=0, max_value=150, value=50)
        kira_baslangic = st.date_input("Kira Sözleşmesi Başlangıç Tarihi", datetime.now())
        odeme_gunu = st.number_input("Her Ayın Hangi Günü Ödenecek? (1-30)", min_value=1, max_value=30, value=5)

    if st.button("🚀 BİLGİLERİ AVUKATA GÖNDER", use_container_width=True):
        if not kiralayan_ad or not kiraci_ad:
            st.error("❌ Hata: İsim alanları boş bırakılamaz.")
        elif gayrimenkul_turu in ["Konut", "Çatılı İşyeri"] and depozito_ay_sayisi > 3:
            st.error("❌ Hata: Güvence bedeli yasal sınırın üzerinde.")
        else:
            conn = sqlite3.connect("hukuk_otomasyon.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO yeni_kontratlar (tarih, kiralayan, kiralayan_tc, kiralayan_adres, kiralayan_iban, kiraci, kiraci_tc, kiraci_adres, cins, bedel, para_birimi, depozito, artis, baslangic, odeme_gunu) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                           (datetime.now().strftime("%d.%m.%Y %H:%M"), kiralayan_ad, kiralayan_tc, kiralayan_adres, kiralayan_iban, kiraci_ad, kiraci_tc, kiraci_adres, gayrimenkul_turu, kira_bedeli_aylik, para_birimi, depozito_ay_sayisi, sozlesme_artis_orani, kira_baslangic.strftime('%d.%m.%Y'), odeme_gunu))
            conn.commit()
            conn.close()
            st.success("🎯 Bilgileriniz başarıyla aktarıldı.")

# =====================================================================
# SENARYO 2: MEVCUT SÖZLEŞME YÜKLEME
# =====================================================================
elif islem_tipi == "📂 Elimde İmzalanmış Mevcut Bir Sözleşme Var":
    st.title("⚖️ Keskin Hukuk Bürosu - Dijital Bilgi Portalı")
    st.subheader("📂 Mevcut Sözleşme Bildirim ve Yükleme Formu")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        e_kiralayan = st.text_input("Sözleşmedeki Kiraya Veren:", key="e_k")
        e_kiraci = st.text_input("Sözleşmedeki Kiracı:", key="e_kr")
        e_baslangic = st.date_input("Başlangıç Tarihi:", datetime.now(), key="e_tar")
        e_bedel = st.number_input("Aylık Kira Bedeli:", min_value=0, value=15000, key="e_bedel")
        e_pb = st.selectbox("Para Birimi", ["TL (₺)", "USD ($)", "EUR (€)"], key="e_pb")
    with col_e2:
        yuklenen_dosya = st.file_uploader("Sözleşme Görseli / PDF:", type=["pdf", "png", "jpg", "jpeg"])
        e_notlar = st.text_area("Hukuki Sorununuz / Notlarınız:")

    if st.button("🔒 EVRAKLARI VE ANALİZ TALEBİNİ AVUKATA GÖNDER", use_container_width=True):
        if not e_kiralayan or not e_kiraci:
            st.error("❌ Hata: İsim alanları boş bırakılamaz.")
        else:
            dosya_adi = yuklenen_dosya.name if yuklenen_dosya else "Dosya Yüklenmedi"
            conn = sqlite3.connect("hukuk_otomasyon.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO eski_kontratlar (islem_tarihi, kiralayan, kiraci, baslangic_tarihi, aylik_bedel, para_birimi, dosya_adi, notlar) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                           (datetime.now().strftime("%d.%m.%Y %H:%M"), e_kiralayan, e_kiraci, e_baslangic.strftime('%d.%m.%Y'), e_bedel, e_pb, dosya_adi, e_notlar))
            conn.commit()
            conn.close()
            st.success("✔️ Talebiniz başarıyla iletilmiştir.")

# =====================================================================
# SENARYO 3: YÖNETİM PANELİ (DOKUNMA)
# =====================================================================
else:
    # (Yönetim paneli kodların buradaki gibi kalmaya devam eder, onları değiştirmedim)
    # ...
