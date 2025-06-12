import streamlit as st
import numpy as np

# --- Konfigurasi Aplikasi Streamlit ---
st.set_page_config(
    page_title="Forecasting Kondisi Motor",
    page_icon="🔮",
    layout="wide"
)

# --- Konfigurasi Awal & Ambang Batas (Thresholds) ---
VOLTAGE_NORMAL = 380
ARUS_NORMAL = 5.0

# Ambang Batas Suhu (°C)
TEMP_MOTOR_PERINGATAN = 70.0
TEMP_MOTOR_BAHAYA = 90.0
TEMP_BEARING_PERINGATAN = 65.0
TEMP_BEARING_BAHAYA = 85.0

# Ambang Batas Arus (Ampere)
ARUS_PERINGATAN = ARUS_NORMAL * 1.15
ARUS_BAHAYA = ARUS_NORMAL * 1.30

# Ambang Batas Vibrasi (mm/s) - Sesuai standar ISO 10816
VIBRASI_PERINGATAN = 2.8
VIBRASI_BAHAYA = 4.5

# ==============================================================================
# --- UI Sidebar untuk Input ---
# ==============================================================================
st.sidebar.title("🔧 Panel Kontrol")
st.sidebar.info("Geser slider untuk mengubah nilai pengukuran dan tren kenaikan.")

# --- Grup Slider Nilai Saat Ini ---
st.sidebar.subheader("📊 Nilai Pengukuran Saat Ini")
temp_motor = st.sidebar.slider('Suhu Badan Motor', 20.0, 120.0, 45.0, 0.5, '%.1f°C')
temp_bearing_depan = st.sidebar.slider('Suhu Bearing Depan', 20.0, 120.0, 40.0, 0.5, '%.1f°C')
temp_bearing_belakang = st.sidebar.slider('Suhu Bearing Belakang', 20.0, 120.0, 40.0, 0.5, '%.1f°C')
arus = st.sidebar.slider(f'Arus (Normal: {ARUS_NORMAL}A)', 0.0, 10.0, 5.0, 0.1, '%.1f A')
vibrasi_max_input = st.sidebar.slider('Vibrasi Maksimum Terukur', 0.0, 10.0, 1.5, 0.1, '%.1f mm/s')

# --- Grup Slider Input Untuk Forecasting ---
st.sidebar.subheader("📈 Tren Kenaikan (Input Forecasting)")
st.sidebar.caption("Inputkan laju kenaikan nilai per jam untuk memprediksi sisa waktu operasi.")
kenaikan_temp_motor_per_jam = st.sidebar.slider('Kenaikan Suhu Motor/Jam', 0.0, 5.0, 0.0, 0.1, '%.1f °C/jam')
kenaikan_temp_bearing_per_jam = st.sidebar.slider('Kenaikan Suhu Bearing/Jam', 0.0, 5.0, 0.0, 0.1, '%.1f °C/jam')
kenaikan_vibrasi_per_jam = st.sidebar.slider('Kenaikan Vibrasi/Jam', 0.0, 2.0, 0.0, 0.05, '%.2f mm/s/jam')


# ==============================================================================
# --- Main Panel untuk Output ---
# ==============================================================================
st.title("🔮 Dashboard Forecasting & Kesehatan Motor Listrik")
st.markdown("---")


# --- BAGIAN 1: ANALISIS KONDISI SAAT INI (***UPDATED***) ---
st.header("1. Analisis Kondisi Saat Ini")

# Daftar untuk menampung pesan penyebab perubahan status
pesan_penyebab = []
status = "Normal"  # Status default

# Analisis setiap variabel
max_temp_bearing = max(temp_bearing_depan, temp_bearing_belakang)

# Cek Suhu Motor
if temp_motor >= TEMP_MOTOR_BAHAYA:
    status = "Bahaya"
    pesan_penyebab.append(f"🔥 **Suhu Motor Kritis**: `{temp_motor}°C` (Batas: {TEMP_MOTOR_BAHAYA}°C)")
elif temp_motor >= TEMP_MOTOR_PERINGATAN:
    status = "Peringatan"
    pesan_penyebab.append(f"⚠️ **Suhu Motor Tinggi**: `{temp_motor}°C` (Batas: {TEMP_MOTOR_PERINGATAN}°C)")

# Cek Suhu Bearing
if max_temp_bearing >= TEMP_BEARING_BAHAYA:
    if status != "Bahaya": status = "Bahaya"
    pesan_penyebab.append(f"🔥 **Suhu Bearing Kritis**: `{max_temp_bearing}°C` (Batas: {TEMP_BEARING_BAHAYA}°C)")
elif max_temp_bearing >= TEMP_BEARING_PERINGATAN:
    if status == "Normal": status = "Peringatan"
    pesan_penyebab.append(f"⚠️ **Suhu Bearing Tinggi**: `{max_temp_bearing}°C` (Batas: {TEMP_BEARING_PERINGATAN}°C)")

# Cek Arus
if arus >= ARUS_BAHAYA:
    if status != "Bahaya": status = "Bahaya"
    pesan_penyebab.append(f"⚡ **Arus Sangat Tinggi (Overload)**: `{arus:.1f} A` (Batas: {ARUS_BAHAYA:.1f} A)")
elif arus >= ARUS_PERINGATAN:
    if status == "Normal": status = "Peringatan"
    pesan_penyebab.append(f"⚡ **Arus Melebihi Normal**: `{arus:.1f} A` (Batas: {ARUS_PERINGATAN:.1f} A)")

# Cek Vibrasi
if vibrasi_max_input >= VIBRASI_BAHAYA:
    if status != "Bahaya": status = "Bahaya"
    pesan_penyebab.append(f"🚨 **Vibrasi Kritis**: `{vibrasi_max_input:.1f} mm/s` (Batas: {VIBRASI_BAHAYA} mm/s)")
elif vibrasi_max_input >= VIBRASI_PERINGATAN:
    if status == "Normal": status = "Peringatan"
    pesan_penyebab.append(f"🚨 **Vibrasi Tinggi**: `{vibrasi_max_input:.1f} mm/s` (Batas: {VIBRASI_PERINGATAN} mm/s)")

# Tampilkan Status Utama
if status == "Normal":
    st.success("✅ **KONDISI SAAT INI: NORMAL**")
else:
    # Tampilkan penyebabnya terlebih dahulu
    st.write("#### Detail Penyebab Perubahan Status:")
    for pesan in pesan_penyebab:
        st.write(f"&bull; {pesan}")
    
    # Baru tampilkan status keseluruhan
    if status == "Peringatan":
        st.warning("⚠️ **KONDISI KESELURUHAN: PERINGATAN**")
    else: # Bahaya
        st.error("🛑 **KONDISI KESELURUHAN: BAHAYA**")

st.markdown("---")

# --- BAGIAN 2: PREDIKSI & PROGNOSTIK (FORECASTING) ---
st.header("2. Prediksi & Prognostik (Forecasting)")

def hitung_sisa_waktu(nilai_sekarang, laju_kenaikan, ambang_batas):
    if laju_kenaikan <= 0:
        return np.inf
    if nilai_sekarang >= ambang_batas:
        return 0
    return (ambang_batas - nilai_sekarang) / laju_kenaikan

waktu_prediksi = [
    {'parameter': 'Suhu Motor', 'waktu_ke_bahaya': hitung_sisa_waktu(temp_motor, kenaikan_temp_motor_per_jam, TEMP_MOTOR_BAHAYA)},
    {'parameter': 'Suhu Bearing', 'waktu_ke_bahaya': hitung_sisa_waktu(max_temp_bearing, kenaikan_temp_bearing_per_jam, TEMP_BEARING_BAHAYA)},
    {'parameter': 'Vibrasi', 'waktu_ke_bahaya': hitung_sisa_waktu(vibrasi_max_input, kenaikan_vibrasi_per_jam, VIBRASI_BAHAYA)}
]

prediksi_terdekat = min(p['waktu_ke_bahaya'] for p in waktu_prediksi)
if prediksi_terdekat == np.inf:
    st.info("Tidak ada tren kenaikan yang diinputkan. Prediksi tidak dapat dibuat.")
elif prediksi_terdekat == 0:
    st.error("**Motor sudah berada dalam atau di atas ambang batas Bahaya.**")
else:
    parameter_kritis = [p['parameter'] for p in waktu_prediksi if p['waktu_ke_bahaya'] == prediksi_terdekat][0]
    st.metric(
        label=f"Prediksi Status BAHAYA Pertama dalam",
        value=f"~{prediksi_terdekat:.1f} Jam",
        delta=f"Disebabkan oleh tren kenaikan {parameter_kritis}",
        delta_color="inverse"
    )
