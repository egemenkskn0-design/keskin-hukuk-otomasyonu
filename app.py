import streamlit as st
import sqlite3
from datetime import datetime

# --- Veritabanı Hazırlık ---
def veri_tabani_hazirla():
    conn = sqlite3.connect("hukuk_otomasyon.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yeni_kontratlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, tarih TEXT, kiralayan TEXT, kiralayan_tc TEXT, 
            kiralayan_adres TEXT, kiralayan_iban TEXT, kiraci TEXT, kiraci_tc TEXT, kiraci_adres TEXT, 
            cins TEXT, bedel REAL, para_birimi TEXT, depozito INTEGER, artis INTEGER, baslangic TEXT, odeme_gunu INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eski_kontratlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, islem_tarihi TEXT, kiralayan TEXT, kiralayan_tc TEXT, 
            kiraci TEXT, kiraci_tc TEXT, dosya_adi TEXT, notlar TEXT
        )
    """)
    conn.commit()
    conn.close()

veri_tabani_hazirla()

# --- Arayüz ---
st.set_page_config(page_title="AV. EGEMEN KESKİN", layout="wide")
st.title("⚖️ AV. EGEMEN KESKİN")

islem = st.sidebar.radio("Lütfen Durumunuza Uygun Seçeneği İşaretleyin:", 
                         ["✨ Sıfırdan Kira Sözleşmesi Hazırlatmak İstiyorum", 
                          "📂 Elimde İmzalanmış Mevcut Bir Sözleşme Var"])

if islem == "✨ Sıfırdan Kira Sözleşmesi Hazırlatmak İstiyorum":
    st.subheader("📋 Sıfırdan Sözleşme Üretim Formu")
    col1, col2 = st.columns(2)
    with col1:
        kiralayan_ad = st.text_input("Kiraya Veren Adı / Unvanı")
        kiralayan_tc = st.text_input("T.C. Kimlik No / Vergi No")
        kiralayan_adres = st.text_area("Resmi Tebligat Adresi")
        kiralayan_iban = st.text_input("IBAN Numarası")
    with col2:
        kiraci_ad = st.text_input("Kiracı Adı / Şirket Unvanı")
        kiraci_tc = st.text_input("T.C. Kimlik / Pasaport / Vergi No")
        kiraci_adres = st.text_area("Kiracının İkametgah Adresi")

    col3, col4 = st.columns(2)
    with col3:
        gayrimenkul_turu = st.selectbox("Kiralanan Taşınmazın Cinsi", ["Konut", "Çatılı İşyeri", "Arsa/Arazi"])
        kira_bedeli_aylik = st.number_input("Aylık Kira Bedeli", min_value=0, value=20000, step=500)
        para_birimi = st.selectbox("Para Birimi", ["TL (₺)", "USD ($)", "EUR (€)"])
    with col4:
        sozlesme_artis_orani = st.slider("Yeni Dönem Yıllık Artış Oranı (%)", 0, 150, 50)
        kira_baslangic = st.date_input("Kira Sözleşmesi Başlangıç Tarihi", datetime.now())
        odeme_gunu = st.number_input("Her Ayın Hangi Günü Ödenecek? (1-30)", 1, 30, 5)

    if st.button("🚀 BİLGİLERİ AVUKATA GÖNDER", use_container_width=True):
        conn = sqlite3.connect("hukuk_otomasyon.db")
        c = conn.cursor()
        c.execute("INSERT INTO yeni_kontratlar (tarih, kiralayan, kiralayan_tc, kiralayan_adres, kiralayan_iban, kiraci, kiraci_tc, kiraci_adres, cins, bedel, para_birimi, artis, baslangic, odeme_gunu) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                  (datetime.now().strftime("%d.%m.%Y %H:%M"), kiralayan_ad, kiralayan_tc, kiralayan_adres, kiralayan_iban, kiraci_ad, kiraci_tc, kiraci_adres, gayrimenkul_turu, kira_bedeli_aylik, para_birimi, sozlesme_artis_orani, kira_baslangic.strftime('%d.%m.%Y'), odeme_gunu))
        conn.commit()
        conn.close()
        st.success("🎯 Bilgileriniz başarıyla avukatımıza iletildi.")

elif islem == "📂 Elimde İmzalanmış Mevcut Bir Sözleşme Var":
    st.subheader("📂 Mevcut Sözleşme Bildirim ve Yükleme Formu")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        e_kiralayan = st.text_input("Kiraya Veren Adı Soyadı")
        e_kiralayan_tc = st.text_input("Kiraya Veren T.C. No")
    with col_e2:
        e_kiraci = st.text_input("Kiracı Adı Soyadı")
        e_kiraci_tc = st.text_input("Kiracı T.C. No")
    
    yuklenen_dosya = st.file_uploader("Sözleşme PDF/Fotoğrafı Yükle", type=["pdf", "jpg", "png"])
    e_notlar = st.text_area("Hukuki Sorununuz / Notlarınız:")

    if st.button("🔒 EVRAKLARI VE ANALİZ TALEBİNİ GÖNDER", use_container_width=True):
        dosya_adi = yuklenen_dosya.name if yuklenen_dosya else "Dosya Yüklenmedi"
        conn = sqlite3.connect("hukuk_otomasyon.db")
        c = conn.cursor()
        c.execute("INSERT INTO eski_kontratlar (islem_tarihi, kiralayan, kiralayan_tc, kiraci, kiraci_tc, dosya_adi, notlar) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                  (datetime.now().strftime("%d.%m.%Y %H:%M"), e_kiralayan, e_kiralayan_tc, e_kiraci, e_kiraci_tc, dosya_adi, e_notlar))
        conn.commit()
        conn.close()
        st.success("✔️ Talebiniz ve evraklarınız başarıyla iletilmiştir.")
