import streamlit as st
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIG HALAMAN & TEMA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Kalkulator Proyeksi Paid Ads - Lembaga Zakat",
    page_icon="🕋",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. HELPER FORMATTING (Rupiah & Angka Format Indonesia)
# -----------------------------------------------------------------------------
def fmt_rp(val):
    """Format angka ke Rupiah dengan pemisah titik (Contoh: Rp 1.875.000.000)"""
    return f"Rp {val:,.0f}".replace(",", ".")

def fmt_num(val, decimals=0):
    """Format angka biasa dengan pemisah titik (Contoh: 19.230.769)"""
    if decimals > 0:
        formatted = f"{val:,.{decimals}f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{val:,.0f}".replace(",", ".")

# -----------------------------------------------------------------------------
# 3. HEADER
# -----------------------------------------------------------------------------
st.title("🕋 Kalkulator Proyeksi Paid Ads - Lembaga Zakat")
st.caption("Simulasi perolehan donasi digital berdasarkan anggaran & asumsi konversi iklan")
st.write("---")

# -----------------------------------------------------------------------------
# 4. SIDEBAR (FORM ISIAN / INPUT)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Form Input Parameter")

budget = st.sidebar.number_input(
    "1. Budget Iklan Paid Ads (Rp)", 
    min_value=0, 
    value=50000000, 
    step=1000000,
    help="Total anggaran iklan yang akan dialokasikan"
)

cpc = st.sidebar.number_input(
    "2. Proyeksi CPC / Cost Per Click (Rp)", 
    min_value=1, 
    value=40, 
    step=5,
    help="Estimasi biaya per satu klik iklan"
)

ctr = st.sidebar.number_input(
    "3. Target CTR / Click-Through Rate (%)", 
    min_value=0.01, 
    value=6.5, 
    step=0.1,
    help="Persentase audiens yang mengklik iklan dari total tayangan"
)

cvr = st.sidebar.number_input(
    "4. Target CVR / Rate Konversi Donatur (%)", 
    min_value=0.01, 
    value=1.5, 
    step=0.1,
    help="Persentase pengunjung web yang akhirnya berdonasi/berzakat"
)

avg_donasi = st.sidebar.number_input(
    "5. Rata-rata Donasi / Zakat per Donatur (Rp)", 
    min_value=1000, 
    value=100000, 
    step=10000,
    help="Estimasi rata-rata nominal zakat/sedekah per donatur"
)

# -----------------------------------------------------------------------------
# 5. RUMUS KALKULASI PROYEKSI
# -----------------------------------------------------------------------------
klik = budget / cpc if cpc > 0 else 0
reach = klik / (ctr / 100) if ctr > 0 else 0
donatur = klik * (cvr / 100)
total_dana = donatur * avg_donasi
cpa = budget / donatur if donatur > 0 else 0
roas = total_dana / budget if budget > 0 else 0

# -----------------------------------------------------------------------------
# 6. SUMMARY: "Proyeksi Hasil Paid Ads" (MEMUNCULKAN INPUT + OUTPUT)
# -----------------------------------------------------------------------------
st.subheader("Proyeksi Hasil Paid Ads")

# --- KELOMPOK A: ANGKA ISIAN / INPUT PARAMETER ---
st.markdown("##### 📌 Parameter Input (Asumsi Isian)")
col_in1, col_in2, col_in3, col_in4 = st.columns(4)

with col_in1:
    st.metric(label="Budget Iklan", value=fmt_rp(budget))
with col_in2:
    st.metric(label="Target CTR / CVR", value=f"{ctr}% / {cvr}%")
with col_in3:
    st.metric(label="Rata-rata Zakat/Donasi", value=fmt_rp(avg_donasi))
with col_in4:
    st.metric(label="Proyeksi CPC", value=fmt_rp(cpc))

st.divider() # Garis pemisah tipis

# --- KELOMPOK B: HASIL PROYEKSI / OUTPUT ---
st.markdown("##### 📊 Hasil Proyeksi (Output)")

# Baris 1 Output
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Estimasi Reach", value=fmt_num(reach))
with col2:
    st.metric(label="Estimasi Klik", value=fmt_num(klik))
with col3:
    st.metric(label="Proyeksi Donatur", value=fmt_num(donatur, decimals=1))
with col4:
    st.metric(label="Total Dana Terhimpun", value=fmt_rp(total_dana))

st.write("") # Margin penjelas

# Baris 2 Output
col5, col6, col7 = st.columns([1, 1, 2])
with col5:
    st.metric(label="Proyeksi CPC", value=fmt_rp(cpc))
with col6:
    st.metric(label="Target CPA (Cost/Donor)", value=fmt_rp(cpa))
with col7:
    st.metric(label="Proyeksi ROAS", value=f"{roas:.2f} x")

st.write("---")

# -----------------------------------------------------------------------------
# 7. VISUALISASI FUNNEL (EXPANDER)
# -----------------------------------------------------------------------------
with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) Paid Ads"):
    st.write("### Corong Konversi Paid Ads Zakat")
    
    # Grafik Funnel Interactive pakai Plotly
    fig = go.Figure(go.Funnel(
        y = ["Estimasi Reach (Impression)", "Estimasi Klik (Web Visit)", "Proyeksi Donatur (Muzakki)"],
        x = [reach, klik, donatur],
        textinfo = "value+percent initial",
        marker = {"color": ["#3b82f6", "#10b981", "#f59e0b"]}
    ))
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ffffff")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"""
    💡 **Ringkasan Perjalanan Funnel:**
    * Dari total **{fmt_num(reach)}** tayangan iklan (Reach), diperkirakan **{fmt_num(klik)}** orang akan mengklik ke landing page.
    * Dari **{fmt_num(klik)}** pengunjung, diperkirakan **{fmt_num(donatur, 1)}** orang akan menuntaskan zakat/donasinya.
    * Estimasi total dana zakat/donasi terhimpun adalah **{fmt_rp(total_dana)}** dengan efisiensi iklan (ROAS) sebesar **{roas:.2f}x**.
    """)
