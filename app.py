import streamlit as st
import plotly.graph_objects as go

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Kalkulator Proyeksi Paid Ads - Lembaga Zakat",
    page_icon="🕋",
    layout="wide"
)

# 2. FUNGSI FORMAT ANGKA
def fmt_rp(val):
    return f"Rp {val:,.0f}".replace(",", ".")

def fmt_num(val):
    return f"{val:,.0f}".replace(",", ".")

def fmt_dec(val):
    return f"{val:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")

# 3. HEADER UTAMA
st.title("🕋 Kalkulator Proyeksi Paid Ads - Lembaga Zakat")
st.caption("Simulasi perolehan donasi digital berdasarkan anggaran & asumsi konversi iklan")
st.write("---")

# 4. AREA INPUT (Sekarang langsung di halaman utama, BUKAN di sidebar)
st.subheader("⚙️ Form Input Asumsi Iklan")
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    budget = st.number_input("Budget Iklan (Rp)", value=50000000, step=1000000)
    avg_donasi = st.number_input("Rata-rata Zakat/Donasi (Rp)", value=100000, step=10000)

with col_in2:
    cpc = st.number_input("Proyeksi CPC (Rp)", value=40, step=5)
    ctr = st.number_input("Target CTR (%)", value=6.5, step=0.1)

with col_in3:
    cvr = st.number_input("Target CVR (%)", value=1.5, step=0.1)

st.write("---")

# 5. RUMUS KALKULASI PROYEKSI
klik = budget / cpc if cpc > 0 else 0
reach = klik / (ctr / 100) if ctr > 0 else 0
donatur = klik * (cvr / 100)
total_dana = donatur * avg_donasi
cpa = budget / donatur if donatur > 0 else 0
roas = total_dana / budget if budget > 0 else 0

# 6. AREA SUMMARY (PROYEKSI HASIL PAID ADS)
st.subheader("Proyeksi Hasil Paid Ads")

# Kelompok Parameter Input (Sesuai Gambar)
st.markdown("##### 📌 Parameter Input (Asumsi Isian)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Budget Iklan", fmt_rp(budget))
col2.metric("Target CTR / CVR", f"{ctr}% / {cvr}%")
col3.metric("Rata-rata Zakat/Donasi", fmt_rp(avg_donasi))
col4.metric("Proyeksi CPC", fmt_rp(cpc))

st.write("")

# Kelompok Hasil Proyeksi (Sesuai Gambar)
st.markdown("##### 📊 Hasil Proyeksi (Output)")
col5, col6, col7, col8 = st.columns(4)
col5.metric("Estimasi Reach", fmt_num(reach))
col6.metric("Estimasi Klik", fmt_num(klik))
col7.metric("Proyeksi Donatur", fmt_dec(donatur))
col8.metric("Total Dana Terhimpun", fmt_rp(total_dana))

st.write("")

col9, col10, col11, col12 = st.columns(4)
col9.metric("Proyeksi CPC", fmt_rp(cpc))
col10.metric("Target CPA (Cost/Donor)", fmt_rp(cpa))
col11.metric("Proyeksi ROAS", f"{roas:.2f} x")
col12.empty()

st.write("---")

# 7. VISUALISASI FUNNEL (EXPANDER)
with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) Paid Ads"):
    st.write("### Corong Konversi Paid Ads Zakat")
    
    fig = go.Figure(go.Funnel(
        y=["Estimasi Reach", "Estimasi Klik (Web Visit)", "Proyeksi Donatur (Muzakki)"],
        x=[reach, klik, donatur],
        textinfo="value+percent initial",
        marker={"color": ["#3b82f6", "#10b981", "#f59e0b"]}
    ))
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    st.plotly_chart(fig, use_container_width=True)
