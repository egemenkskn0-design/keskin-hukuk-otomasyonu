import streamlit as st
import docx
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
from datetime import datetime
import sqlite3
import hashlib

# =====================================================================
# WORD ÜRETİM FONKSİYONU
# =====================================================================
def word_uret(v):
    doc = docx.Document()
    # Başlık
    title = doc.add_paragraph("KİRA SÖZLEŞMESİ TASLAĞI")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Pt(16)
    
    doc.add_paragraph(f"Tarih: {datetime.now().strftime('%d.%m.%Y')}")
    doc.add_paragraph("\n1. TARAFLAR\n")
    doc.add_paragraph(f"KİRAYA VEREN: {v['kiralayan']}\nT.C./Vergi No: {v['kiralayan_tc']}\nAdres: {v['kiralayan_adres']}\nIBAN: {v['kiralayan_iban']}")
    doc.add_paragraph(f"\nKİRACI: {v['kiraci']}\nT.C./Pasaport No: {v['kiraci_tc']}\nAdres: {v['kiraci_adres']}")
    
    doc.add_paragraph("\n2. KİRA ŞARTLARI\n")
    doc.add_paragraph(f"Taşınmaz Cinsi: {v['cins']}\nAylık Kira Bedeli: {v['bedel']:,} {v['para_birimi']}\nGüvence Bedeli: {v['depozito']} Aylık Kira\nYıllık Artış Oranı: %{v['artis']}\nBaşlangıç Tarihi: {v['baslangic']}\nÖdeme Günü: Her ayın {v['odeme_gunu']}.")
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# =====================================================================
# GERİ KALAN ALTYAPI
# =====================================================================
def hash_sifre(sifre): return hashlib.sha256(sifre.encode()).hexdigest()

def veri_tabani_hazirla():
    conn = sqlite3.connect("hukuk_otomasyon.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS admin_auth (id INTEGER PRIMARY KEY, password_hash TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS yeni_kontratlar (id INTEGER PRIMARY KEY AUTOINCREMENT, tarih TEXT, kiralayan TEXT, kiralayan_tc TEXT, kiralayan_adres TEXT, kiralayan_iban TEXT, kiraci TEXT, kiraci_tc TEXT, kiraci_adres TEXT, cins TEXT, bedel REAL, para_birimi TEXT, depozito INTEGER, artis INTEGER, baslangic TEXT, odeme_gunu INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS eski_kontratlar (id INTEGER PRIMARY KEY AUTOINCREMENT, islem_tarihi TEXT, kiralayan TEXT, kiraci TEXT, baslangic_tarihi TEXT, aylik_bedel REAL, para_birimi TEXT, dosya_adi TEXT, notlar TEXT)")
    conn.commit()
    conn.close()

veri_tabani_hazirla()
st.set_page_config(page_title="Keskin Hukuk", layout="wide")

# (SENARYO 1 VE 2 AYNI KALACAK - Buraya senin daha önce kullandığın formları ekle)
# ... (Form kodlarını buraya ekleyeceksin) ...

# =====================================================================
# YÖNETİM PANELİ (GÜNCELLENMİŞ)
# =====================================================================
# [Senaryo 3 kısmında 'Yeni Talepler' döngüsü içine şu butonu ekledim:]
# ...
#    for k in yeni_list:
#        with st.expander(f"📋 Form #{k['id']} | {k['kiraci']}"):
#            ... (bilgiler) ...
#            
#            w_data = word_uret(k)
#            st.download_button(
#                label="📜 Resmi Word Sözleşmesini İndir",
#                data=w_data,
#                file_name=f"Sozlesme_{k['kiraci']}.docx",
#                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#            )
