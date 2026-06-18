import streamlit as st
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
from datetime import datetime
import sqlite3
import hashlib

# --- Fonksiyonlar ---
def hash_sifre(sifre): return hashlib.sha256(sifre.encode()).hexdigest()

def word_uret(v):
    doc = docx.Document()
    p = doc.add_paragraph("KİRA SÖZLEŞMESİ")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True
    doc.add_paragraph(f"Tarih: {datetime.now().strftime('%d.%m.%Y')}")
    doc.add_paragraph(f"KİRAYA VEREN: {v['kiralayan']} (TC: {v['kiralayan_tc']})\nAdres: {v['kiralayan_adres']}\nIBAN: {v['kiralayan_iban']}")
    doc.add_paragraph(f"KİRACI: {v['kiraci']} (TC: {v['kiraci_tc']})\nAdres: {v['kiraci_adres']}")
    doc.add_paragraph(f"ŞARTLAR: {v['bedel']} {v['para_birimi']} - Başlangıç: {v['baslangic']} - Ödeme Günü: {v['odeme_gunu']}")
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- Veritabanı ---
conn = sqlite3.connect("hukuk_otomasyon.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS admin_auth (id INTEGER PRIMARY KEY, password_hash TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS yeni_kontratlar (id INTEGER PRIMARY KEY AUTOINCREMENT, tarih TEXT, kiralayan TEXT, kiralayan_tc TEXT, kiralayan_adres TEXT, kiralayan_iban TEXT, kiraci TEXT, kiraci_tc TEXT, kiraci_adres TEXT, cins TEXT, bedel REAL, para_birimi TEXT, depozito INTEGER, artis INTEGER, baslangic TEXT, odeme_gunu INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS eski_kontratlar (id INTEGER PRIMARY KEY AUTOINCREMENT, islem_tarihi TEXT, kiralayan TEXT, kiralayan_tc TEXT, kiraci TEXT, kiraci_tc TEXT, dosya_adi TEXT, notlar TEXT)")
conn.commit()
conn.close()

# --- Arayüz ---
st.set_page_config(page_title="AV. EGEMEN KESKİN", layout="wide")
st.title("⚖️ AV. EGEMEN KESKİN")

# Gizli Anahtar Kontrolü
if "admin_girdi" not in st.session_state: st.session_state.admin_girdi = False

if st.sidebar.text_input("Gizli Erişim", type="password") == "egemen123": # Buradaki şifreyi istediğin gibi değiştir
    st.session_state.admin_girdi = True

is_admin_mode = st.session_state.admin_girdi

options = ["Sıfırdan Sözleşme", "Mevcut Sözleşme"]
if is_admin_mode:
    options.append("Admin Paneli")

islem = st.sidebar.radio("İşlem Seçiniz:", options)

if islem == "Sıfırdan Sözleşme":
    st.subheader("📋 Sıfırdan Sözleşme Hazırlama Formu")
    col1, col2 = st.columns(2)
    with col1:
        kiralayan = st.text_input("Kiraya Veren Adı/Unvanı")
        kiralayan_tc = st.text_input("Kiraya Veren T.C./Vergi No")
        kiralayan_adres = st.text_area("Tebligat Adresi")
        kiralayan_iban = st.text_input("IBAN")
    with col2:
        kiraci = st.text_input("Kiracı Adı/Unvanı")
        kiraci_tc = st.text_input("Kiracı T.C./Vergi No")
        kiraci_adres = st.text_area("Kiracı İkametgah Adresi")
    
    bedel = st.number_input("Aylık Kira Bedeli", value=20000)
    para = st.selectbox("Para Birimi", ["TL", "USD", "EUR"])
    artis = st.slider("Artış Oranı (%)", 0, 100, 50)
    baslangic = st.date_input("Başlangıç Tarihi")
    odeme = st.number_input("Ödeme Günü", 1, 30, 5)
    
    if st.button("Sisteme Kaydet"):
        conn = sqlite3.connect("hukuk_otomasyon.db")
        c = conn.cursor()
        c.execute("INSERT INTO yeni_kontratlar (tarih, kiralayan, kiralayan_tc, kiralayan_adres, kiralayan_iban, kiraci, kiraci_tc, kiraci_adres, bedel, para_birimi, artis, baslangic, odeme_gunu) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                  (datetime.now().strftime("%d.%m.%Y"), kiralayan, kiralayan_tc, kiralayan_adres, kiralayan_iban, kiraci, kiraci_tc, kiraci_adres, bedel, para, artis, baslangic.strftime("%d.%m.%Y"), odeme))
        conn.commit()
        conn.close()
        st.success("Talebiniz alınmıştır.")

elif islem == "Mevcut Sözleşme":
    st.subheader("📁 Mevcut Sözleşme İnceleme Talebi")
    col1, col2 = st.columns(2)
    with col1:
        e_kiralayan = st.text_input("Kiraya Veren")
        e_kiralayan_tc = st.text_input("Kiraya Veren T.C.")
    with col2:
        e_kiraci = st.text_input("Kiracı")
        e_kiraci_tc = st.text_input("Kiracı T.C.")
    
    yuklenen_dosya = st.file_uploader("Sözleşme PDF/Fotoğrafı Yükle", type=["pdf", "jpg", "png"])
    e_not = st.text_area("Talep ve Notlarınız")
    
    if st.button("Avukata Gönder"):
        dosya_adi = yuklenen_dosya.name if yuklenen_dosya else "Dosya Yüklenmedi"
        conn = sqlite3.connect("hukuk_otomasyon.db")
        c = conn.cursor()
        c.execute("INSERT INTO eski_kontratlar (islem_tarihi, kiralayan, kiralayan_tc, kiraci, kiraci_tc, dosya_adi, notlar) VALUES (?,?,?,?,?,?,?)", 
                  (datetime.now().strftime("%d.%m.%Y"), e_kiralayan, e_kiralayan_tc, e_kiraci, e_kiraci_tc, dosya_adi, e_not))
        conn.commit()
        conn.close()
        st.success("Belgeleriniz iletildi.")

elif islem == "Admin Paneli":
    st.header("🔒 Yönetici Paneli")
    conn = sqlite3.connect("hukuk_otomasyon.db")
    c = conn.cursor()
    c.execute("SELECT password_hash FROM admin_auth")
    auth = c.fetchone()
    conn.close()
    
    if not auth:
        s = st.text_input("Şifre Oluştur:", type="password")
        if st.button("Kur"):
            conn = sqlite3.connect("hukuk_otomasyon.db")
            c = conn.cursor()
            c.execute("INSERT INTO admin_auth (password_hash) VALUES (?)", (hash_sifre(s),))
            conn.commit()
            conn.close()
            st.rerun()
    else:
        giris = st.text_input("Yönetici Şifresi:", type="password")
        if hash_sifre(giris) == auth[0]:
            st.success("Erişim Onaylandı")
            st.subheader("📬 Yeni Sözleşme Talepleri")
            conn = sqlite3.connect("hukuk_otomasyon.db")
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM yeni_kontratlar")
            kayitlar = c.fetchall()
            for k in kayitlar:
                with st.expander(f"Müvekkil: {k['kiraci']}"):
                    st.write(f"Kiraya Veren: {k['kiralayan']}")
                    data = word_uret(k)
                    st.download_button("📜 Sözleşmeyi İndir", data, f"Sozlesme_{k['kiraci']}.docx")
            
            st.subheader("📂 Mevcut Sözleşme İncelemeleri")
            c.execute("SELECT * FROM eski_kontratlar")
            eski = c.fetchall()
            for e in eski:
                st.write(f"Müvekkil: {e['kiraci']} | Not: {e['notlar']} | Dosya: {e['dosya_adi']}")
            conn.close()
