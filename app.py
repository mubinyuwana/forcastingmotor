import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- Konfigurasi Aplikasi Streamlit ---
# Mengatur judul tab, ikon, dan tata letak halaman menjadi lebar
st.set_page_config(
    page_title="Forecasting Kondisi Motor",
    page_icon="📈",
    layout="wide"
)

# --- Konfigurasi Awal & Ambang Batas (Thresholds) ---
# Nilai-nilai ini adalah contoh dan harus disesuaikan dengan spesifikasi motor Anda.
TEMP_MOTOR_PERINGATAN = 70.0
TEMP_MOTOR_BAHAYA = 90.0
TEMP_BEARING_PERINGATAN = 65.0
TEMP_BEARING_BAHAYA = 85.0
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
vibrasi_max_input = st.sidebar.slider('Vibrasi Maksimum Terukur', 0.0, 10.0, 1.5, 0.1, '%.1f mm/s')

# --- Grup Slider Input Untuk Forecasting ---
st.sidebar.subheader("📈 Tren Kenaikan (Input Forecasting)")
st.sidebar.caption("Inputkan laju kenaikan nilai per jam untuk memprediksi sisa waktu operasi.")
kenaikan_temp_motor_per_jam = st.sidebar.slider('Kenaikan Suhu Motor/Jam', 0.0, 5.0, 0.1, 0.1, '%.1f °C/jam')
kenaikan_temp_bearing_per_jam = st.sidebar.slider('Kenaikan Suhu Bearing/Jam', 0.0, 5.0, 0.0, 0.1, '%.1f °C/jam')
kenaikan_vibrasi_per_jam = st.sidebar.slider('Kenaikan Vibrasi/Jam', 0.0, 2.0, 0.0, 0.05, '%.2f mm/s/jam')


# ==============================================================================
# --- Main Panel untuk Output ---
# ==============================================================================
st.title("📈 Dashboard Forecasting & Kesehatan Motor Listrik")
st.markdown("---")

# --- BAGIAN 1: ANALISIS KONDISI SAAT INI DENGAN LAYOUT BARU ---
st.header("1. Kondisi Saat Ini")

# Fungsi untuk membuat grafik gauge yang lebih modern (bullet chart)
def create_modern_gauge(value, title, min_val, max_val, warn_val, danger_val):
    """Membuat grafik gauge modern berbentuk bullet chart."""
    fig = go.Figure(go.Indicator(
        mode="number+gauge",
        gauge={
            'shape': "bullet",
            'axis': {'range': [None, max_val]},
            'threshold': {
                'line': {'color': "black", 'width': 3},
                'thickness': 0.8,
                'value': value},
            'steps': [
                {'range': [min_val, warn_val], 'color': "lightgreen"},
                {'range': [warn_val, danger_val], 'color': "yellow"},
                {'range': [danger_val, max_val], 'color': "red"}],
        },
        value=value,
        number={'font': {'size': 48}},
        domain={'x': [0.1, 1], 'y': [0.2, 0.8]}
    ))
    fig.update_layout(height=120, margin={'t':10, 'b':10, 'l':10, 'r':10})
    return fig

# Menentukan status keseluruhan di awal
max_temp_bearing = max(temp_bearing_depan, temp_bearing_belakang)
status = "Normal"
if (temp_motor >= TEMP_MOTOR_BAHAYA or max_temp_bearing >= TEMP_BEARING_BAHAYA or vibrasi_max_input >= VIBRASI_BAHAYA):
    status = "Bahaya"
elif (temp_motor >= TEMP_MOTOR_PERINGATAN or max_temp_bearing >= TEMP_BEARING_PERINGATAN or vibrasi_max_input >= VIBRASI_PERINGATAN):
    status = "Peringatan"

# Menampilkan status keseluruhan
if status == "Normal":
    st.success("✅ **KONDISI KESELURUHAN: NORMAL**")
elif status == "Peringatan":
    st.warning("⚠️ **KONDISI KESELURUHAN: PERINGATAN**")
else: # Bahaya
    st.error("🛑 **KONDISI KESELURUHAN: BAHAYA**")

st.markdown("---") # Garis pemisah

# --- Layout untuk setiap parameter ---
def display_parameter_status(title, value, unit, warn_val, danger_val, min_val, max_val, info_normal, info_warn, info_danger):
    col_text, col_gauge = st.columns([1, 1])
    with col_text:
        st.subheader(title)
        if value < warn_val:
            st.write(info_normal)
        elif value < danger_val:
            st.write(info_warn)
        else:
            st.write(info_danger)
    with col_gauge:
        st.plotly_chart(create_modern_gauge(value, title, min_val, max_val, warn_val, danger_val), use_container_width=True)

display_parameter_status(
    "🌡️ Suhu Motor", temp_motor, "°C", TEMP_MOTOR_PERINGATAN, TEMP_MOTOR_BAHAYA, 20, 120,
    "Suhu motor berada dalam rentang **normal** dan aman.",
    "Suhu motor telah memasuki level **peringatan**. Perlu perhatian lebih lanjut untuk mencegah overheating.",
    "Suhu motor telah mencapai level **bahaya**. Risiko kerusakan komponen sangat tinggi."
)

display_parameter_status(
    "🌡️ Suhu Bearing", max_temp_bearing, "°C", TEMP_BEARING_PERINGATAN, TEMP_BEARING_BAHAYA, 20, 120,
    "Suhu bearing berada dalam kondisi **normal**.",
    "Suhu bearing **meningkat** dan memasuki level **peringatan**. Ini bisa menjadi indikasi awal masalah lubrikasi atau keausan.",
    "Suhu bearing sangat tinggi dan dalam kondisi **bahaya**. Risiko kegagalan bearing sangat besar."
)

display_parameter_status(
    " shaky_face: Vibrasi", vibrasi_max_input, "mm/s", VIBRASI_PERINGATAN, VIBRASI_BAHAYA, 0, 10,
    "Tingkat getaran mesin dalam batas **normal**.",
    "Getaran mesin telah melebihi batas wajar dan masuk level **peringatan**. Ini bisa disebabkan oleh ketidakseimbangan atau awal kerusakan.",
    "Tingkat getaran mesin sangat tinggi dan dalam kondisi **bahaya**. Risiko kerusakan struktural pada motor atau komponen terkait."
)

st.markdown("---")

# --- BAGIAN 2: PROYEKSI FORECASTING DENGAN LAYOUT BARU ---
st.header("2. Analisa & Proyeksi Forecasting")

# Fungsi untuk menghitung sisa waktu
def hitung_waktu_prediksi(nilai_awal, laju_kenaikan, ambang_batas):
    if laju_kenaikan <= 0:
        return np.inf
    if nilai_awal >= ambang_batas:
        return 0
    return (ambang_batas - nilai_awal) / laju_kenaikan

# Fungsi untuk menghitung proyeksi data
def hitung_proyeksi(nilai_awal, laju_kenaikan, waktu_maks=48):
    if laju_kenaikan > 0:
        waktu = np.arange(0, waktu_maks + 1, 1)
    else:
        waktu = np.array([0, waktu_maks])
    proyeksi = nilai_awal + laju_kenaikan * waktu
    return waktu, proyeksi

# Cek apakah ada tren kenaikan
has_trend = kenaikan_temp_motor_per_jam > 0 or kenaikan_temp_bearing_per_jam > 0 or kenaikan_vibrasi_per_jam > 0

if not has_trend:
    st.info("Tidak ada tren kenaikan yang diinputkan. Grafik dan analisa proyeksi tidak ditampilkan.")
else:
    col_text, col_chart = st.columns([2, 3]) # Memberi ruang lebih untuk grafik

    with col_text:
        st.subheader("📝 Analisa Prediksi")
        st.write("Berdasarkan tren kenaikan yang diinputkan, berikut adalah estimasi sisa waktu operasi sebelum mencapai ambang batas.")

        # Analisa Suhu Motor
        waktu_warn = hitung_waktu_prediksi(temp_motor, kenaikan_temp_motor_per_jam, TEMP_MOTOR_PERINGATAN)
        waktu_danger = hitung_waktu_prediksi(temp_motor, kenaikan_temp_motor_per_jam, TEMP_MOTOR_BAHAYA)
        if waktu_danger < np.inf and waktu_danger > 0:
            st.metric(label="Prediksi Suhu Motor ke Bahaya", value=f"{waktu_danger:.1f} Jam")
        elif waktu_danger == 0:
            st.metric(label="Prediksi Suhu Motor ke Bahaya", value="Sudah Tercapai")
        
        # Analisa Suhu Bearing
        waktu_warn = hitung_waktu_prediksi(max_temp_bearing, kenaikan_temp_bearing_per_jam, TEMP_BEARING_PERINGATAN)
        waktu_danger = hitung_waktu_prediksi(max_temp_bearing, kenaikan_temp_bearing_per_jam, TEMP_BEARING_BAHAYA)
        if waktu_danger < np.inf and waktu_danger > 0:
            st.metric(label="Prediksi Suhu Bearing ke Bahaya", value=f"{waktu_danger:.1f} Jam")
        elif waktu_danger == 0:
             st.metric(label="Prediksi Suhu Bearing ke Bahaya", value="Sudah Tercapai")
       
        # Analisa Vibrasi
        waktu_warn = hitung_waktu_prediksi(vibrasi_max_input, kenaikan_vibrasi_per_jam, VIBRASI_PERINGATAN)
        waktu_danger = hitung_waktu_prediksi(vibrasi_max_input, kenaikan_vibrasi_per_jam, VIBRASI_BAHAYA)
        if waktu_danger < np.inf and waktu_danger > 0:
            st.metric(label="Prediksi Vibrasi ke Bahaya", value=f"{waktu_danger:.1f} Jam")
        elif waktu_danger == 0:
            st.metric(label="Prediksi Vibrasi ke Bahaya", value="Sudah Tercapai")


    with col_chart:
        # Membuat Subplots
        fig_forecast = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=('Proyeksi Suhu Motor', 'Proyeksi Suhu Bearing', 'Proyeksi Vibrasi'))
        
        # Proyeksi Suhu Motor
        waktu, proyeksi = hitung_proyeksi(temp_motor, kenaikan_temp_motor_per_jam)
        fig_forecast.add_trace(go.Scatter(x=waktu, y=proyeksi, mode='lines', name='Suhu Motor', line={'color':'#636EFA'}), row=1, col=1)
        fig_forecast.add_hline(y=TEMP_MOTOR_PERINGATAN, line_dash="dash", line_color="orange", annotation_text="Peringatan", row=1, col=1)
        fig_forecast.add_hline(y=TEMP_MOTOR_BAHAYA, line_dash="dash", line_color="red", annotation_text="Bahaya", row=1, col=1)

        # Proyeksi Suhu Bearing
        waktu, proyeksi = hitung_proyeksi(max_temp_bearing, kenaikan_temp_bearing_per_jam)
        fig_forecast.add_trace(go.Scatter(x=waktu, y=proyeksi, mode='lines', name='Suhu Bearing', line={'color':'#EF553B'}), row=2, col=1)
        fig_forecast.add_hline(y=TEMP_BEARING_PERINGATAN, line_dash="dash", line_color="orange", annotation_text="Peringatan", row=2, col=1)
        fig_forecast.add_hline(y=TEMP_BEARING_BAHAYA, line_dash="dash", line_color="red", annotation_text="Bahaya", row=2, col=1)

        # Proyeksi Vibrasi
        waktu, proyeksi = hitung_proyeksi(vibrasi_max_input, kenaikan_vibrasi_per_jam)
        fig_forecast.add_trace(go.Scatter(x=waktu, y=proyeksi, mode='lines', name='Vibrasi', line={'color':'#00CC96'}), row=3, col=1)
        fig_forecast.add_hline(y=VIBRASI_PERINGATAN, line_dash="dash", line_color="orange", annotation_text="Peringatan", row=3, col=1)
        fig_forecast.add_hline(y=VIBRASI_BAHAYA, line_dash="dash", line_color="red", annotation_text="Bahaya", row=3, col=1)

        # Update layout
        fig_forecast.update_layout(height=600, showlegend=False, margin={'t':50, 'b':30})
        fig_forecast.update_yaxes(title_text="Suhu (°C)", row=1, col=1)
        fig_forecast.update_yaxes(title_text="Suhu (°C)", row=2, col=1)
        fig_forecast.update_yaxes(title_text="Vibrasi (mm/s)", row=3, col=1)
        fig_forecast.update_xaxes(title_text="Waktu (Jam ke Depan)", row=3, col=1)

        st.plotly_chart(fig_forecast, use_container_width=True)

st.markdown("---")
st.caption("Aplikasi Simulasi & Forecasting Kondisi Motor v3.0")
