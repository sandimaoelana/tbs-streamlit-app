# ============================================
# Sistem Digital Pengangkutan TBS - Streamlit
# Dibuat oleh: ChatGPT untuk Sandi Maulana
# ============================================

import streamlit as st
import pandas as pd
import datetime
import sqlite3

# Setup Database
conn = sqlite3.connect('tbs_data.db', check_same_thread=False)
c = conn.cursor()

# Inisialisasi DB jika belum ada
def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS tbs_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT,
                jam TEXT,
                km_awal INTEGER,
                km_akhir INTEGER,
                dari TEXT,
                ke TEXT,
                jenis_muatan TEXT,
                volume REAL,
                satuan TEXT,
                bbm REAL,
                biaya INTEGER,
                supir TEXT,
                keterangan TEXT,
                approved INTEGER DEFAULT 0
                )''')
    conn.commit()

# Simpan Data
def simpan_data(data):
    c.execute('''INSERT INTO tbs_data 
                (tanggal, jam, km_awal, km_akhir, dari, ke, jenis_muatan, volume, satuan, bbm, biaya, supir, keterangan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()

# Ambil Data
def ambil_data():
    return pd.read_sql("SELECT * FROM tbs_data", conn)

# Approve Data
def approve_data(entry_id):
    c.execute("UPDATE tbs_data SET approved=1 WHERE id=?", (entry_id,))
    conn.commit()

# Login System
def login():
    st.sidebar.title("Login")
    role = st.sidebar.selectbox("Pilih role:", ["supir", "pengawas", "admin"])
    nama = st.sidebar.text_input("Nama Pengguna")
    masuk = st.sidebar.button("Masuk")
    return role if masuk else None, nama

# Halaman Input Supir
def halaman_supir(nama):
    st.title("Form Harian Supir")
    with st.form("form_supir"):
        tanggal = st.date_input("Tanggal", datetime.date.today())
        jam = st.text_input("Jam")
        km_awal = st.number_input("KM Awal", 0)
        km_akhir = st.number_input("KM Akhir", 0)
        dari = st.text_input("Dari")
        ke = st.text_input("Ke")
        jenis_muatan = st.text_input("Jenis Muatan", "TBS")
        volume = st.number_input("Volume", 0.0)
        satuan = st.selectbox("Satuan", ["Kg", "Ton"])
        bbm = st.number_input("BBM (liter)", 0.0)
        biaya = st.number_input("Biaya (Rp)", 0)
        keterangan = st.text_area("Keterangan", "-")
        submitted = st.form_submit_button("Simpan")
        if submitted:
            simpan_data((str(tanggal), jam, km_awal, km_akhir, dari, ke, jenis_muatan, volume, satuan, bbm, biaya, nama, keterangan))
            st.success("Data berhasil disimpan.")

# Halaman Pengawas
def halaman_pengawas():
    st.title("Dashboard Pengawas")
    df = ambil_data()
    df_filter = df[df['approved'] == 0]
    st.subheader("Data Belum Diverifikasi")
    for i, row in df_filter.iterrows():
        st.write(row)
        if st.button(f"Verifikasi ID {row['id']}"):
            approve_data(row['id'])
            st.success(f"Data ID {row['id']} berhasil diverifikasi.")
    st.subheader("Data Terverifikasi")
    df_approved = df[df['approved'] == 1]
    st.dataframe(df_approved)

# Halaman Admin
def halaman_admin():
    st.title("Export Laporan")
    df = ambil_data()
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Excel", csv, "laporan_tbs.csv", "text/csv")

# Main App
init_db()
role, nama = login()
if role == "supir":
    halaman_supir(nama)
elif role == "pengawas":
    halaman_pengawas()
elif role == "admin":
    halaman_admin()
else:
    st.title("Sistem Digital Pengangkutan TBS")
    st.write("Silakan login terlebih dahulu.")
