import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- Konfigurasi Aplikasi Streamlit ---
st.set_page_config(
    page_title="Forecasting Kondisi Motor",
    page_icon="📈",
    layout="wide"
)

# --- Konfigurasi Awal & Ambang Batas ---
ARUS_NORMAL = 5.0
TEMP_MOTOR_PERINGATAN = 70.0
TEMP_MOTOR_BAHAYA = 90.0
TEMP_BEARING_PERINGATAN = 65.0
TEMP_BEARING_BAHAYA = 85.0
VIBRASI_PERINGATAN = 2.8
VIBRASI_BAHAYA = 4.5
ARUS_PERINGATAN = ARUS_NORMAL * 1.15
ARUS_BAHAYA = ARUS_NORMAL * 1.30

# ==============================================================================
# --- UI Sidebar untuk Input ---
# ==============================================================================
st.sidebar.title("🔧 Panel Kontrol")
st.sidebar.info("Geser slider untuk mengubah nilai pengukuran dan tren kenaikan.")

st.sidebar.subheader("📊 Nilai Pengukuran Saat Ini")
temp_motor = st.sidebar.slider('Suhu Badan Motor', 20.0, 120.0, 45.0, 0.5, '%.1f°C')
temp_bearing_depan = st.sidebar.slider('Suhu Bearing Depan', 20.0, 120.0, 40.0, 0.5, '%.1f°C')
temp_bearing_belakang = st.sidebar.slider('Suhu Bearing Belakang', 20.0, 120.0, 40.0, 0.5, '%.1f°C')
vibrasi_max_input = st.sidebar.slider('Vibrasi Maksimum Terukur', 0.0, 10.0, 1.5, 0.1, '%.1f mm/s')
arus = st.sidebar.slider('Arus Motor (Ampere)', 0.0, 10.0, 5.1, 0.1, '%.1f A')

st.sidebar.subheader("📈 Tren Kenaikan (Input Forecasting)")
st.sidebar.caption("Inputkan laju kenaikan nilai per jam untuk memprediksi sisa waktu operasi.")
kenaikan_temp_motor_per_jam = st.sidebar.slider('Kenaikan Suhu Motor/Jam', 0.0, 5.0, 0.1, 0.1, '%.1f °C/jam')
kenaikan_temp_bearing_per_jam = st.sidebar.slider('Kenaikan Suhu Bearing/Jam', 0.0, 5.0, 0.0, 0.1, '%.1f °C/jam')
kenaikan_vibrasi_per_jam = st.sidebar.slider('Kenaikan Vibrasi/Jam', 0.0, 2.0, 0.0, 0.05, '%.2f mm/s/jam')
kenaikan_arus_per_jam = st.sidebar.slider('Kenaikan Arus/Jam', 0.0, 1.0, 0.0, 0.05, '%.2f A/jam')

# ==============================================================================
# --- Main Panel untuk Output ---
# ==============================================================================
st.title("📈 Dashboard Forecasting & Kesehatan Motor Listrik")

# Menampilkan parameter operasional statis
col_ops1, col_ops2 = st.columns(2)
col_ops1.metric(label="Tegangan Operasional", value="380V AC", delta="3-Phase", delta_color="off")
col_ops2.metric(label="Arus Normal", value=f"{ARUS_NORMAL} A")

st.markdown("---")

# --- BAGIAN 1: ANALISIS KONDISI SAAT INI ---
st.header("1. Kondisi Saat Ini")

def create_modern_gauge(value, title, min_val, max_val, warn_val, danger_val):
    fig = go.Figure(go.Indicator(
        mode="number+gauge",
        gauge={
            'shape': "bullet", 'axis': {'range': [None, max_val]},
            'threshold': {'line': {'color': "black", 'width': 3}, 'thickness': 0.8, 'value': value},
            'steps': [
                {'range': [min_val, warn_val], 'color': "#2ECC71"}, # Hijau
                {'range': [warn_val, danger_val], 'color': "#F1C40F"}, # Kuning
                {'range': [danger_val, max_val], 'color': "#E74C3C"}], # Merah
        },
        value=value,
        number={'font': {'size': 48, 'color': '#34495E'}},
        domain={'x': [0.1, 1], 'y': [0.2, 0.8]}
    ))
    fig.update_layout(height=120, margin={'t':10, 'b':10, 'l':10, 'r':10}, paper_bgcolor='rgba(0,0,0,0)')
    return fig

max_temp_bearing = max(temp_bearing_depan, temp_bearing_belakang)
status = "Normal"
if (temp_motor >= TEMP_MOTOR_BAHAYA or max_temp_bearing >= TEMP_BEARING_BAHAYA or vibrasi_max_input >= VIBRASI_BAHAYA or arus >= ARUS_BAHAYA):
    status = "Bahaya"
elif (temp_motor >= TEMP_MOTOR_PERINGATAN or max_temp_bearing >= TEMP_BEARING_PERINGATAN or vibrasi_max_input >= VIBRASI_PERINGATAN or arus >= ARUS_PERINGATAN):
    status = "Peringatan"

if status == "Normal":
    st.success("✅ **KONDISI KESELURUHAN: NORMAL**")
elif status == "Peringatan":
    st.warning("⚠️ **KONDISI KESELURUHAN: PERINGATAN**")
else:
    st.error("🛑 **KONDISI KESELURUHAN: BAHAYA**")

st.markdown("---")

# Layout 2x2 untuk gauges
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

with row1_col1:
    st.subheader("🌡️ Suhu Motor")
    st.plotly_chart(create_modern_gauge(temp_motor, "Suhu Motor", 20, 120, TEMP_MOTOR_PERINGATAN, TEMP_MOTOR_BAHAYA), use_container_width=True)
with row1_col2:
    st.subheader("🌡️ Suhu Bearing")
    st.plotly_chart(create_modern_gauge(max_temp_bearing, "Suhu Bearing", 20, 120, TEMP_BEARING_PERINGATAN, TEMP_BEARING_BAHAYA), use_container_width=True)
with row2_col1:
    st.subheader(" shaky_face: Vibrasi")
    st.plotly_chart(create_modern_gauge(vibrasi_max_input, "Vibrasi", 0, 10, VIBRASI_PERINGATAN, VIBRASI_BAHAYA), use_container_width=True)
with row2_col2:
    st.subheader("⚡ Arus")
    st.plotly_chart(create_modern_gauge(arus, "Arus", 0, 10, ARUS_PERINGATAN, ARUS_BAHAYA), use_container_width=True)

st.markdown("---")

# --- BAGIAN 2: ANALISA & PROYEKSI FORECASTING ---
st.header("2. Analisa & Proyeksi Forecasting")

def hitung_waktu_prediksi(nilai_awal, laju_kenaikan, ambang_batas):
    if laju_kenaikan <= 0 or nilai_awal >= ambang_batas:
        return 0
    return (ambang_batas - nilai_awal) / laju_kenaikan

def hitung_proyeksi(nilai_awal, laju_kenaikan, waktu_maks=48):
    waktu = np.arange(0, waktu_maks + 1, 1)
    proyeksi = nilai_awal + laju_kenaikan * waktu
    return waktu, proyeksi

has_trend = any(k > 0 for k in [kenaikan_temp_motor_per_jam, kenaikan_temp_bearing_per_jam, kenaikan_vibrasi_per_jam, kenaikan_arus_per_jam])

if not has_trend:
    st.info("Tidak ada tren kenaikan yang diinputkan. Grafik dan analisa proyeksi tidak ditampilkan.")
else:
    col_text, col_chart = st.columns([2, 3])

    with col_text:
        st.subheader("📝 Analisa Prediksi")
        st.write("Estimasi sisa waktu operasi sebelum mencapai ambang batas bahaya, berdasarkan tren kenaikan yang diinputkan.")
        
        params = {
            "Suhu Motor": (temp_motor, kenaikan_temp_motor_per_jam, TEMP_MOTOR_BAHAYA),
            "Suhu Bearing": (max_temp_bearing, kenaikan_temp_bearing_per_jam, TEMP_BEARING_BAHAYA),
            "Vibrasi": (vibrasi_max_input, kenaikan_vibrasi_per_jam, VIBRASI_BAHAYA),
            "Arus": (arus, kenaikan_arus_per_jam, ARUS_BAHAYA)
        }

        for param, (val, rate, danger_thresh) in params.items():
            if rate > 0:
                waktu_danger = hitung_waktu_prediksi(val, rate, danger_thresh)
                st.metric(label=f"Prediksi {param} ke Bahaya", value=f"{waktu_danger:.1f} Jam")

    with col_chart:
        fig_forecast = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                                     subplot_titles=('Suhu Motor', 'Suhu Bearing', 'Vibrasi', 'Arus'))
        
        # Plot Suhu Motor
        w, p = hitung_proyeksi(temp_motor, kenaikan_temp_motor_per_jam)
        fig_forecast.add_trace(go.Scatter(x=w, y=p, name='Suhu Motor', line={'color':'#636EFA'}), row=1, col=1)
        fig_forecast.add_hline(y=TEMP_MOTOR_BAHAYA, line_dash="dash", line_color="red", row=1, col=1)
        
        # Plot Suhu Bearing
        w, p = hitung_proyeksi(max_temp_bearing, kenaikan_temp_bearing_per_jam)
        fig_forecast.add_trace(go.Scatter(x=w, y=p, name='Suhu Bearing', line={'color':'#EF553B'}), row=2, col=1)
        fig_forecast.add_hline(y=TEMP_BEARING_BAHAYA, line_dash="dash", line_color="red", row=2, col=1)

        # Plot Vibrasi
        w, p = hitung_proyeksi(vibrasi_max_input, kenaikan_vibrasi_per_jam)
        fig_forecast.add_trace(go.Scatter(x=w, y=p, name='Vibrasi', line={'color':'#00CC96'}), row=3, col=1)
        fig_forecast.add_hline(y=VIBRASI_BAHAYA, line_dash="dash", line_color="red", row=3, col=1)

        # Plot Arus
        w, p = hitung_proyeksi(arus, kenaikan_arus_per_jam)
        fig_forecast.add_trace(go.Scatter(x=w, y=p, name='Arus', line={'color':'#AB63FA'}), row=4, col=1)
        fig_forecast.add_hline(y=ARUS_BAHAYA, line_dash="dash", line_color="red", row=4, col=1)

        fig_forecast.update_layout(height=700, showlegend=False, margin={'t':50, 'b':0})
        fig_forecast.update_yaxes(title_text="°C", row=1, col=1); fig_forecast.update_yaxes(title_text="°C", row=2, col=1)
        fig_forecast.update_yaxes(title_text="mm/s", row=3, col=1); fig_forecast.update_yaxes(title_text="A", row=4, col=1)
        fig_forecast.update_xaxes(title_text="Waktu (Jam ke Depan)", row=4, col=1)
        
        st.plotly_chart(fig_forecast, use_container_width=True)

st.markdown("---")
st.caption("Aplikasi Simulasi & Forecasting Kondisi Motor v4.0")
