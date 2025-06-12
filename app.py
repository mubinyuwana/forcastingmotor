import streamlit as st
import numpy as np

# --- Konfigurasi Aplikasi Streamlit ---
st.set_page_config(
    page_title="Simulasi Motor Listrik",
    page_icon="⚡",
    layout="wide"
)

# --- Konfigurasi Awal & Ambang Batas (Thresholds) ---
# Nilai-nilai ini adalah contoh dan harus disesuaikan dengan spesifikasi motor Anda.
VOLTAGE_NORMAL = 380  # VAC
ARUS_NORMAL = 5.0  # Ampere

# Ambang Batas Suhu (°C)
TEMP_MOTOR_PERINGATAN = 70.0
TEMP_MOTOR_BAHAYA = 90.0
TEMP_BEARING_PERINGATAN = 65.0
TEMP_BEARING_BAHAYA = 85.0

# Ambang Batas Arus (Ampere)
ARUS_PERINGATAN = ARUS_NORMAL * 1.15  # 15% di atas normal
ARUS_BAHAYA = ARUS_NORMAL * 1.30  # 30% di atas normal

# Ambang Batas Vibrasi (mm/s) - Sesuai standar ISO 10816
VIBRASI_PERINGATAN = 2.8
VIBRASI_BAHAYA = 4.5


# --- UI Sidebar untuk Input ---
st.sidebar.title("🔧 Parameter Input Motor")
st.sidebar.info("Gunakan slider di bawah ini untuk mengubah nilai pengukuran secara real-time.")

# --- Grup Slider Suhu ---
st.sidebar.subheader("🌡️ Suhu (°C)")
temp_motor = st.sidebar.slider('Suhu Badan Motor', min_value=20.0, max_value=120.0, value=45.0, step=0.5, format='%.1f°C')
temp_bearing_depan = st.sidebar.slider('Suhu Bearing Depan', min_value=20.0, max_value=120.0, value=40.0, step=0.5, format='%.1f°C')
temp_bearing_belakang = st.sidebar.slider('Suhu Bearing Belakang', min_value=20.0, max_value=120.0, value=40.0, step=0.5, format='%.1f°C')

# --- Grup Slider Arus ---
st.sidebar.subheader("⚡ Arus (Ampere)")
arus = st.sidebar.slider(f'Arus (Normal: {ARUS_NORMAL}A)', min_value=0.0, max_value=10.0, value=5.0, step=0.1, format='%.1f A')

# --- Grup Slider Vibrasi ---
st.sidebar.subheader(" shaky_face: Vibrasi (mm/s)")
vibrasi_depan_axial = st.sidebar.slider('Vibrasi Depan (Axial)', min_value=0.0, max_value=10.0, value=1.2, step=0.1, format='%.1f mm/s')
vibrasi_depan_radial = st.sidebar.slider('Vibrasi Depan (Radial)', min_value=0.0, max_value=10.0, value=1.5, step=0.1, format='%.1f mm/s')
vibrasi_belakang_axial = st.sidebar.slider('Vibrasi Belakang (Axial)', min_value=0.0, max_value=10.0, value=1.1, step=0.1, format='%.1f mm/s')
vibrasi_belakang_radial = st.sidebar.slider('Vibrasi Belakang (Radial)', min_value=0.0, max_value=10.0, value=1.4, step=0.1, format='%.1f mm/s')

# --- Main Panel untuk Output ---
st.title("Dashboard Forecasting Kondisi Motor Listrik")
st.write("Aplikasi ini mensimulasikan kondisi kesehatan motor listrik 3-phase 380VAC berdasarkan input dari sensor. Status diperbarui secara otomatis saat slider diubah.")
st.markdown("---")

# --- Logika Analisis dan Forecasting ---
pesan = []
status = "Normal"  # Status default

# 1. Analisis Suhu
if temp_motor >= TEMP_MOTOR_BAHAYA or temp_bearing_depan >= TEMP_BEARING_BAHAYA or temp_bearing_belakang >= TEMP_BEARING_BAHAYA:
    status = "Bahaya"
elif temp_motor >= TEMP_MOTOR_PERINGATAN or temp_bearing_depan >= TEMP_BEARING_PERINGATAN or temp_bearing_belakang >= TEMP_BEARING_PERINGATAN:
    status = "Peringatan"

# 2. Analisis Arus
if arus >= ARUS_BAHAYA:
    if status != "Bahaya": status = "Bahaya"
elif arus >= ARUS_PERINGATAN:
    if status == "Normal": status = "Peringatan"

# 3. Analisis Vibrasi
vibrasi_max = max(vibrasi_depan_axial, vibrasi_depan_radial, vibrasi_belakang_axial, vibrasi_belakang_radial)
if vibrasi_max >= VIBRASI_BAHAYA:
    if status != "Bahaya": status = "Bahaya"
elif vibrasi_max >= VIBRASI_PERINGATAN:
    if status == "Normal": status = "Peringatan"

# --- Menampilkan Status Utama ---
if status == "Normal":
    st.success("✅ **KONDISI: NORMAL**")
    st.write("Semua parameter operasional motor berada dalam batas aman.")
elif status == "Peringatan":
    st.warning("⚠️ **KONDISI: PERINGATAN**")
    st.write("Terdeteksi satu atau lebih parameter yang melebihi ambang batas wajar. Inspeksi lebih lanjut mungkin diperlukan.")
else: # Bahaya
    st.error("🛑 **KONDISI: BAHAYA**")
    st.write("Terdeteksi parameter kritis yang dapat menyebabkan kerusakan motor! **Segera lakukan pengecekan atau hentikan operasi.**")

# --- Menampilkan Detail Masalah ---
st.subheader("Detail Analisis:")

# Kolom untuk detail yang lebih rapi
col1, col2 = st.columns(2)

# Analisis Suhu Detail
with col1:
    st.write("##### **Analisis Suhu**")
    if temp_motor >= TEMP_MOTOR_BAHAYA:
        pesan.append(f"🔥 Suhu Motor Kritis: **{temp_motor}°C** (Batas: {TEMP_MOTOR_BAHAYA}°C)")
    elif temp_motor >= TEMP_MOTOR_PERINGATAN:
        pesan.append(f"⚠️ Suhu Motor Tinggi: **{temp_motor}°C** (Batas: {TEMP_MOTOR_PERINGATAN}°C)")

    if temp_bearing_depan >= TEMP_BEARING_BAHAYA:
         pesan.append(f"🔥 Suhu Bearing Depan Kritis: **{temp_bearing_depan}°C** (Batas: {TEMP_BEARING_BAHAYA}°C)")
    elif temp_bearing_depan >= TEMP_BEARING_PERINGATAN:
         pesan.append(f"⚠️ Suhu Bearing Depan Tinggi: **{temp_bearing_depan}°C** (Batas: {TEMP_BEARING_PERINGATAN}°C)")

    if temp_bearing_belakang >= TEMP_BEARING_BAHAYA:
         pesan.append(f"🔥 Suhu Bearing Belakang Kritis: **{temp_bearing_belakang}°C** (Batas: {TEMP_BEARING_BAHAYA}°C)")
    elif temp_bearing_belakang >= TEMP_BEARING_PERINGATAN:
         pesan.append(f"⚠️ Suhu Bearing Belakang Tinggi: **{temp_bearing_belakang}°C** (Batas: {TEMP_BEARING_PERINGATAN}°C)")

# Analisis Arus Detail
with col1:
    st.write("##### **Analisis Arus**")
    if arus >= ARUS_BAHAYA:
        pesan.append(f"⚡ Arus Sangat Tinggi (Overload): **{arus:.2f} A** (Batas: {ARUS_BAHAYA:.2f} A)")
    elif arus >= ARUS_PERINGATAN:
        pesan.append(f"⚡ Arus Melebihi Normal: **{arus:.2f} A** (Batas: {ARUS_PERINGATAN:.2f} A)")

# Analisis Vibrasi Detail
with col2:
    st.write("##### **Analisis Vibrasi**")
    if vibrasi_max >= VIBRASI_BAHAYA:
        pesan.append(f"🚨 Vibrasi Kritis: **{vibrasi_max:.2f} mm/s** (Batas: {VIBRASI_BAHAYA:.2f} mm/s)")
    elif vibrasi_max >= VIBRASI_PERINGATAN:
        pesan.append(f"🚨 Vibrasi Tinggi: **{vibrasi_max:.2f} mm/s** (Batas: {VIBRASI_PERINGATAN:.2f} mm/s)")

if not pesan:
    st.info("Tidak ada anomali yang terdeteksi pada parameter motor.")
else:
    for p in pesan:
        st.write(f"- {p}")