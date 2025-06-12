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

# Fungsi untuk membuat grafik gauge yang lebih kecil
def create_gauge(value, min_val, max_val, warn_val, danger_val):
    """Membuat grafik gauge setengah lingkaran yang lebih ringkas."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'font': {'size': 36}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'steps': [
                {'range': [min_val, warn_val], 'color': "lightgreen"},
                {'range': [warn_val, danger_val], 'color': "yellow"},
                {'range': [danger_val, max_val], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 1,
                'value': value
            }
        }
    ))
    fig.update_layout(height=180, margin={'t':10, 'b':10, 'l':10, 'r':10})
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

# --- Layout untuk Suhu Motor ---
col1_text, col1_gauge = st.columns([1, 1])
with col1_text:
    st.subheader("🌡️ Suhu Motor")
    if temp_motor < TEMP_MOTOR_PERINGATAN:
        st.write("Suhu motor berada dalam rentang **normal** dan aman.")
    elif temp_motor < TEMP_MOTOR_BAHAYA:
        st.write("Suhu motor telah memasuki level **peringatan**. Perlu perhatian lebih lanjut untuk mencegah overheating.")
    else:
        st.write("Suhu motor telah mencapai level **bahaya**. Risiko kerusakan komponen sangat tinggi.")
    st.write(f"Nilai saat ini: **{temp_motor}°C**")

with col1_gauge:
    st.plotly_chart(create_gauge(temp_motor, 20, 120, TEMP_MOTOR_PERINGATAN, TEMP_MOTOR_BAHAYA), use_container_width=True)

# --- Layout untuk Suhu Bearing ---
col2_text, col2_gauge = st.columns([1, 1])
with col2_text:
    st.subheader("🌡️ Suhu Bearing")
    if max_temp_bearing < TEMP_BEARING_PERINGATAN:
        st.write("Suhu bearing berada dalam kondisi **normal**.")
    elif max_temp_bearing < TEMP_BEARING_BAHAYA:
        st.write("Suhu bearing **meningkat** dan memasuki level **peringatan**. Ini bisa menjadi indikasi awal masalah lubrikasi atau keausan.")
    else:
        st.write("Suhu bearing sangat tinggi dan dalam kondisi **bahaya**. Risiko kegagalan bearing sangat besar.")
    st.write(f"Nilai tertinggi saat ini: **{max_temp_bearing}°C**")

with col2_gauge:
    st.plotly_chart(create_gauge(max_temp_bearing, 20, 120, TEMP_BEARING_PERINGATAN, TEMP_BEARING_BAHAYA), use_container_width=True)

# --- Layout untuk Vibrasi ---
col3_text, col3_gauge = st.columns([1, 1])
with col3_text:
    st.subheader(" shaky_face: Vibrasi")
    if vibrasi_max_input < VIBRASI_PERINGATAN:
        st.write("Tingkat getaran mesin dalam batas **normal**.")
    elif vibrasi_max_input < VIBRASI_BAHAYA:
        st.write("Getaran mesin telah melebihi batas wajar dan masuk level **peringatan**. Ini bisa disebabkan oleh ketidakseimbangan, kelonggaran baut, atau awal kerusakan.")
    else:
        st.write("Tingkat getaran mesin sangat tinggi dan dalam kondisi **bahaya**. Risiko kerusakan struktural pada motor atau komponen terkait.")
    st.write(f"Nilai saat ini: **{vibrasi_max_input} mm/s**")

with col3_gauge:
    st.plotly_chart(create_gauge(vibrasi_max_input, 0, 10, VIBRASI_PERINGATAN, VIBRASI_BAHAYA), use_container_width=True)


st.markdown("---")

# --- BAGIAN 2: PROYEKSI FORECASTING DENGAN GRAFIK GARIS ---
st.header("2. Proyeksi Forecasting")

# Fungsi untuk menghitung proyeksi waktu
def hitung_proyeksi(nilai_awal, laju_kenaikan, waktu_maks=24):
    if laju_kenaikan > 0:
        waktu = np.arange(0, waktu_maks + 0.1, 0.5)
    else:
        waktu = np.array([0, waktu_maks])
    proyeksi = nilai_awal + laju_kenaikan * waktu
    return waktu, proyeksi

# Cek apakah ada tren kenaikan untuk ditampilkan di grafik
if kenaikan_temp_motor_per_jam == 0 and kenaikan_temp_bearing_per_jam == 0 and kenaikan_vibrasi_per_jam == 0:
    st.info("Tidak ada tren kenaikan yang diinputkan. Grafik proyeksi tidak ditampilkan.")
else:
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
    fig_forecast.update_layout(height=700, showlegend=False, margin={'t':50, 'b':30})
    fig_forecast.update_yaxes(title_text="Suhu (°C)", row=1, col=1)
    fig_forecast.update_yaxes(title_text="Suhu (°C)", row=2, col=1)
    fig_forecast.update_yaxes(title_text="Vibrasi (mm/s)", row=3, col=1)
    fig_forecast.update_xaxes(title_text="Waktu (Jam ke Depan)", row=3, col=1)

    st.plotly_chart(fig_forecast, use_container_width=True)

st.markdown("---")
st.caption("Aplikasi Simulasi & Forecasting Kondisi Motor v2.0")
