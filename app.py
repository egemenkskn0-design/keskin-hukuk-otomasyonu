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

# Gizli parametre kontrolü: Sadece URL'de ?admin=1 varsa Admin Paneli'ni gösterir
query_params = st.query_params
is_admin_mode = query_params.get("admin") == "1"

options = ["Sıfırdan Sözleşme", "Mevcut Sözleşme"]
if is_admin_mode:
    options.append("Admin Paneli")

islem = st.sidebar.radio("Seçim:", options)

if islem == "Sıfırdan Sözleşme":
    st.subheader("Sıfırdan Sözleşme Hazırlama")
    # ... (Sıfırdan sözleşme formun aynı kalacak) ...
    kiralayan = st.text_input("Kiraya Veren Adı")
    # (Buraya diğer alanlarını ekle)
    if st.button("Sisteme Kaydet"):
        st.success("Talebiniz iletildi.")

elif islem == "Mevcut Sözleşme":
    st.subheader("📁 Mevcut Sözleşme Dosyası Yükleme")
    # ... (Mevcut sözleşme formun aynı kalacak) ...
    if st.button("Avukata Gönder"):
        st.success("Talebiniz iletildi.")

elif islem == "Admin Paneli":
    st.header("🔒 Yönetici Paneli")
    conn = sqlite3.connect("hukuk_otomasyon.db")
    c = conn.cursor()
    c.execute("SELECT password_hash FROM admin_auth")
    auth = c.fetchone()
    conn.close()
    
    # Giriş kontrolü...
    giris = st.text_input("Şifre:", type="password")
    if auth and hash_sifre(giris) == auth[0]:
        st.success("Erişim Onaylandı")
        # Listelemeler buraya...
