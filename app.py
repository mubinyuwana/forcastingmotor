import streamlit as st
import numpy as np

# --- Konfigurasi Aplikasi Streamlit ---
st.set_page_config(
    page_title="Forecasting Kondisi Motor",
    page_icon="🔮",
    layout="wide"
)

# --- Konfigurasi Awal & Ambang Batas (Thresholds) ---
# Nilai-nilai ini adalah contoh dan harus disesuaikan dengan spesifikasi motor Anda.
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


# --- BAGIAN 1: ANALISIS KONDISI SAAT INI ---
st.header("1. Analisis Kondisi Saat Ini")

# Logika Analisis Status
status = "Normal"
max_temp_bearing = max(temp_bearing_depan, temp_bearing_belakang)

if temp_motor >= TEMP_MOTOR_BAHAYA or max_temp_bearing >= TEMP_BEARING_BAHAYA or arus >= ARUS_BAHAYA or vibrasi_max_input >= VIBRASI_BAHAYA:
    status = "Bahaya"
elif temp_motor >= TEMP_MOTOR_PERINGATAN or max_temp_bearing >= TEMP_BEARING_PERINGATAN or arus >= ARUS_PERINGATAN or vibrasi_max_input >= VIBRASI_PERINGATAN:
    status = "Peringatan"

# Tampilkan Status Utama
if status == "Normal":
    st.success("✅ **KONDISI SAAT INI: NORMAL**")
    st.write("Semua parameter operasional motor berada dalam batas aman.")
elif status == "Peringatan":
    st.warning("⚠️ **KONDISI SAAT INI: PERINGATAN**")
    st.write("Terdeteksi satu atau lebih parameter yang melebihi ambang batas wajar.")
else:
    st.error("🛑 **KONDISI SAAT INI: BAHAYA**")
    st.write("Parameter kritis terdeteksi! Berisiko menyebabkan kerusakan motor.")

st.markdown("---")

# --- BAGIAN 2: PREDIKSI & PROGNOSTIK (FORECASTING) ---
st.header("2. Prediksi & Prognostik (Forecasting)")

# Fungsi untuk menghitung sisa waktu
def hitung_sisa_waktu(nilai_sekarang, laju_kenaikan, ambang_batas):
    """Menghitung waktu (dalam jam) hingga nilai sekarang mencapai ambang batas."""
    if laju_kenaikan <= 0:
        return np.inf  # Tidak akan pernah tercapai jika tidak ada kenaikan
    if nilai_sekarang >= ambang_batas:
        return 0  # Sudah melewati ambang batas
    
    sisa_waktu = (ambang_batas - nilai_sekarang) / laju_kenaikan
    return sisa_waktu

# Lakukan kalkulasi untuk setiap parameter
waktu_prediksi = []

# Prediksi Suhu Motor
waktu_prediksi.append({
    'parameter': 'Suhu Motor',
    'waktu_ke_peringatan': hitung_sisa_waktu(temp_motor, kenaikan_temp_motor_per_jam, TEMP_MOTOR_PERINGATAN),
    'waktu_ke_bahaya': hitung_sisa_waktu(temp_motor, kenaikan_temp_motor_per_jam, TEMP_MOTOR_BAHAYA),
})

# Prediksi Suhu Bearing (menggunakan suhu bearing tertinggi saat ini)
waktu_prediksi.append({
    'parameter': 'Suhu Bearing',
    'waktu_ke_peringatan': hitung_sisa_waktu(max_temp_bearing, kenaikan_temp_bearing_per_jam, TEMP_BEARING_PERINGATAN),
    'waktu_ke_bahaya': hitung_sisa_waktu(max_temp_bearing, kenaikan_temp_bearing_per_jam, TEMP_BEARING_BAHAYA),
})

# Prediksi Vibrasi
waktu_prediksi.append({
    'parameter': 'Vibrasi',
    'waktu_ke_peringatan': hitung_sisa_waktu(vibrasi_max_input, kenaikan_vibrasi_per_jam, VIBRASI_PERINGATAN),
    'waktu_ke_bahaya': hitung_sisa_waktu(vibrasi_max_input, kenaikan_vibrasi_per_jam, VIBRASI_BAHAYA),
})

# Cari prediksi waktu terdekat menuju status BAHAYA
prediksi_terdekat = min(p['waktu_ke_bahaya'] for p in waktu_prediksi)
parameter_kritis = [p['parameter'] for p in waktu_prediksi if p['waktu_ke_bahaya'] == prediksi_terdekat][0]


if prediksi_terdekat == np.inf:
    st.info("Tidak ada tren kenaikan yang diinputkan. Prediksi tidak dapat dibuat.")
elif prediksi_terdekat == 0:
    st.error(f"**Motor sudah dalam kondisi BAHAYA karena {parameter_kritis}.**")
else:
    # Tampilkan metrik utama prediksi
    st.metric(
        label=f"Prediksi Status BAHAYA Pertama dalam",
        value=f"~{prediksi_terdekat:.1f} Jam",
        delta=f"Disebabkan oleh tren kenaikan {parameter_kritis}",
        delta_color="inverse"
    )

    st.write("#### Rincian Waktu Prediksi menuju Ambang Batas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"##### Suhu Motor")
        p = waktu_prediksi[0]
        st.write(f"Menuju Peringatan: `{p['waktu_ke_peringatan']:.1f} jam`")
        st.write(f"Menuju Bahaya: `{p['waktu_ke_bahaya']:.1f} jam`")
    
    with col2:
        st.write(f"##### Suhu Bearing")
        p = waktu_prediksi[1]
        st.write(f"Menuju Peringatan: `{p['waktu_ke_peringatan']:.1f} jam`")
        st.write(f"Menuju Bahaya: `{p['waktu_ke_bahaya']:.1f} jam`")

    with col3:
        st.write(f"##### Vibrasi")
        p = waktu_prediksi[2]
        st.write(f"Menuju Peringatan: `{p['waktu_ke_peringatan']:.1f} jam`")
        st.write(f"Menuju Bahaya: `{p['waktu_ke_bahaya']:.1f} jam`")

st.caption("Catatan: `inf jam` berarti parameter tidak akan mencapai ambang batas dengan tren kenaikan saat ini.")
