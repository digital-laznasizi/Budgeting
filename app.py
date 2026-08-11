import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="ZIS Digital Strategy Engine", layout="wide")

# Inisialisasi Session State untuk A/B Testing
if 'scen_a' not in st.session_state:
    st.session_state['scen_a'] = None
if 'scen_b' not in st.session_state:
    st.session_state['scen_b'] = None

st.title("🚀 ZIS Digital Strategy Engine")
st.caption("Simulator Budgeting, Manajemen Risiko, & Penentu Target Zakat")

# ================= SIDEBAR: WHAT-IF & UPLOAD =================
with st.sidebar:
    st.header("⚙️ 1. Auto-Fill Data (Opsional)")
    st.write("Upload data performa bulan lalu untuk mengisi angka otomatis.")
    uploaded_file = st.file_uploader("Upload CSV Performa", type=['csv'])
    if uploaded_file is not None:
        st.success("Data berhasil dimuat! (Simulasi)")
        # Di versi nyata, di sini logika parsing CSV ke session_state diletakkan
    
    st.divider()
    
    st.header("⚠️ 2. What-If Analysis (Risiko)")
    st.write("Simulasikan jika terjadi kondisi pasar yang memburuk (Peak Season).")
    risk_cpm = st.slider("Kenaikan Harga Iklan (CPM) %", 0, 100, 0, help="Contoh: Saat Ramadhan harga iklan naik") / 100
    risk_cr = st.slider("Penurunan Conversion Rate %", 0, 50, 0, help="Muzakki makin sulit berdonasi") / 100

# ================= TAB NAVIGATION =================
tab_goal, tab_ab, tab_ads, tab_org, tab_wa, tab_email, tab_sum = st.tabs([
    "🎯 Goal-Seek", 
    "⚖️ A/B Skenario", 
    "📢 Paid Ads", 
    "📱 Organik", 
    "💬 WA Blast", 
    "✉️ Email", 
    "📈 Ekspor & Total"
])

# ================= INPUT KANAL (DENGAN FAKTOR RISIKO) =================
# Pengumpulan input dilakukan di awal untuk bisa dipakai oleh semua fitur
with tab_ads:
    st.header("Kanal Paid Ads")
    c1, c2 = st.columns(2)
    budget_ads = c1.number_input("Budget Iklan (Rp)", 5000000, step=500000)
    base_cpm = c1.number_input("Target CPM (Rp)", 30000, step=1000)
    freq_ads = c1.number_input("Target Frequency", 1.8, step=0.1)
    ctr_ads = c1.number_input("Target CTR (%)", 3.0, step=0.1) / 100
    
    lp_rate_ads = c2.number_input("Target LP View Rate (%)", 75.0, step=1.0) / 100
    base_cr_ads = c2.number_input("Target CR Ads (%)", 2.0, step=0.1) / 100
    avg_don_ads = c2.number_input("Rata-rata Donasi Ads (Rp)", 100000, step=10000)

with tab_org:
    st.header("Kanal Organic Content")
    c1, c2 = st.columns(2)
    reach_org = c1.number_input("Estimasi Reach Organik", 100000, step=5000)
    interactions_org = c1.number_input("Total Interactions", 5000, step=500)
    pv_org = c1.number_input("Profile Visits", 1000, step=100)
    
    lc_org = c2.number_input("Link in Bio Clicks", 300, step=50)
    base_cr_org = c2.number_input("Target CR Organik (%)", 5.0, step=0.5) / 100
    avg_don_org = c2.number_input("Rata-rata Donasi Organik (Rp)", 200000, step=25000)

with tab_wa:
    st.header("Kanal WA Blast")
    c1, c2 = st.columns(2)
    db_wa = c1.number_input("Total Database WA", 10000, step=1000)
    cpc_wa = c1.number_input("Biaya per Chat (Rp)", 450, step=50)
    del_wa = c1.number_input("Target Delivered WA (%)", 95.0, step=1.0) / 100
    read_wa = c1.number_input("Target Read Rate (%)", 70.0, step=1.0) / 100
    
    ctr_wa = c2.number_input("Target CTR Link WA (%)", 15.0, step=1.0) / 100
    base_cr_wa = c2.number_input("Target CR WA (%)", 20.0, step=1.0) / 100
    avg_don_wa = c2.number_input("Rata-rata Donasi WA (Rp)", 350000, step=25000)

with tab_email:
    st.header("Kanal Email Marketing")
    c1, c2 = st.columns(2)
    db_em = c1.number_input("Total Database Email", 40000, step=5000)
    del_em = c1.number_input("Target Delivery Email (%)", 98.0, step=1.0) / 100
    open_em = c1.number_input("Target Open Rate (%)", 22.0, step=1.0) / 100
    ctr_em = c1.number_input("Target CTR Email (%)", 4.0, step=0.5) / 100
    
    base_cr_em = c2.number_input("Target CR Email (%)", 8.0, step=1.0) / 100
    avg_don_em = c2.number_input("Rata-rata Donasi Email (Rp)", 450000, step=50000)
    cost_em = c2.number_input("Biaya Campaign Email (Rp)", 200000, step=50000)

# ================= ENGINE KALKULASI DENGAN RISK FACTOR =================
# Terapkan What-If Risk
actual_cpm_ads = base_cpm * (1 + risk_cpm)
actual_cr_ads = base_cr_ads * (1 - risk_cr)
actual_cr_org = base_cr_org * (1 - risk_cr)
actual_cr_wa = base_cr_wa * (1 - risk_cr)
actual_cr_em = base_cr_em * (1 - risk_cr)

# Ads Calc
imp_ads = (budget_ads / actual_cpm_ads) * 1000 if actual_cpm_ads > 0 else 0
clicks_ads = imp_ads * ctr_ads
donatur_ads = clicks_ads * lp_rate_ads * actual_cr_ads
dana_ads = donatur_ads * avg_don_ads
roas_ads = dana_ads / budget_ads if budget_ads > 0 else 0

# Org Calc
donatur_org = lc_org * actual_cr_org
dana_org = donatur_org * avg_don_org

# WA Calc
total_cost_wa = db_wa * cpc_wa
donatur_wa = db_wa * del_wa * read_wa * ctr_wa * actual_cr_wa
dana_wa = donatur_wa * avg_don_wa
roas_wa = dana_wa / total_cost_wa if total_cost_wa > 0 else 0

# Email Calc
donatur_em = db_em * del_em * open_em * ctr_em * actual_cr_em
dana_em = donatur_em * avg_don_em
roas_em = dana_em / cost_em if cost_em > 0 else 0

total_biaya = budget_ads + total_cost_wa + cost_em
total_dana = dana_ads + dana_org + dana_wa + dana_em

# Simpan state perhitungan saat ini untuk A/B Test
current_metrics = {
    "Biaya Total": total_biaya,
    "Dana Terhimpun": total_dana,
    "Donatur": donatur_ads + donatur_org + donatur_wa + donatur_em,
    "ROAS Ads": roas_ads,
    "ROAS WA": roas_wa,
    "ROAS Email": roas_em
}

# ================= TAB: GOAL SEEK (KALKULATOR MUNDUR) =================
with tab_goal:
    st.header("🎯 Kalkulator Mundur (Goal-Seek)")
    st.write("Masukkan Target Penghimpunan ZIS Anda bulan ini, dan sistem akan menghitung mundur kebutuhan budget & database berdasar performa saat ini.")
    
    target_dana = st.number_input("Target Total Penghimpunan (Rp)", value=1000000000, step=100000000)
    
    st.subheader("Distribusi Target per Kanal (%)")
    col_pct1, col_pct2, col_pct3 = st.columns(3)
    pct_ads = col_pct1.number_input("Porsi Paid Ads (%)", 50, step=5) / 100
    pct_wa = col_pct2.number_input("Porsi WA Blast (%)", 30, step=5) / 100
    pct_em = col_pct3.number_input("Porsi Email (%)", 20, step=5) / 100
    
    if pct_ads + pct_wa + pct_em != 1.0:
        st.warning("⚠️ Total Porsi harus tepat 100%")
    else:
        req_budget_ads = (target_dana * pct_ads) / roas_ads if roas_ads > 0 else 0
        req_cost_wa = (target_dana * pct_wa) / roas_wa if roas_wa > 0 else 0
        req_db_wa = req_cost_wa / cpc_wa if cpc_wa > 0 else 0
        req_cost_em = (target_dana * pct_em) / roas_em if roas_em > 0 else 0
        
        st.success("✅ Rekomendasi Strategi untuk Mencapai Target:")
        m1, m2, m3 = st.columns(3)
        m1.metric("Kebutuhan Budget Ads", f"Rp {req_budget_ads:,.0f}")
        m2.metric("Kebutuhan Database WA", f"{req_db_wa:,.0f} Kontak")
        m3.metric("Kebutuhan Budget Email", f"Rp {req_cost_em:,.0f}")

# ================= TAB: A/B SKENARIO =================
with tab_ab:
    st.header("⚖️ Bandingkan Skenario A vs B")
    st.write("Ubah parameter di Tab Kanal, lalu simpan sebagai Skenario A. Ubah lagi angkanya, simpan sebagai Skenario B.")
    
    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("💾 Simpan Angka Saat Ini sbg Skenario A", use_container_width=True):
        st.session_state['scen_a'] = current_metrics
        st.success("Skenario A tersimpan!")
        
    if col_btn2.button("💾 Simpan Angka Saat Ini sbg Skenario B", use_container_width=True):
        st.session_state['scen_b'] = current_metrics
        st.success("Skenario B tersimpan!")

    if st.session_state['scen_a'] and st.session_state['scen_b']:
        df_ab = pd.DataFrame([
            {"Skenario": "Skenario A", "Dana Terhimpun (Rp)": st.session_state['scen_a']["Dana Terhimpun"], "Biaya (Rp)": st.session_state['scen_a']["Biaya Total"]},
            {"Skenario": "Skenario B", "Dana Terhimpun (Rp)": st.session_state['scen_b']["Dana Terhimpun"], "Biaya (Rp)": st.session_state['scen_b']["Biaya Total"]}
        ])
        fig_ab = px.bar(df_ab, x="Skenario", y=["Biaya (Rp)", "Dana Terhimpun (Rp)"], barmode="group", title="Perbandingan Biaya vs Hasil")
        st.plotly_chart(fig_ab, use_container_width=True)
    else:
        st.info("Silakan simpan Skenario A dan Skenario B terlebih dahulu untuk melihat grafik perbandingan.")

# ================= TAB: EKSPOR & SUMMARY =================
with tab_sum:
    st.header("📈 Ringkasan & Ekspor Data")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Biaya Investasi", f"Rp {total_biaya:,.0f}")
    c2.metric("Total Donatur", f"{current_metrics['Donatur']:,.1f}")
    c3.metric("Dana Terhimpun", f"Rp {total_dana:,.0f}")
    overall_roas = total_dana / total_biaya if total_biaya > 0 else 0
    c4.metric("Overall ROAS", f"{overall_roas:.2f} x")

    df_summary = pd.DataFrame({
        "Kanal Digital": ["Paid Ads", "Organic Content", "WA Blast", "Email Marketing"],
        "Biaya (Rp)": [budget_ads, 0, total_cost_wa, cost_em],
        "Dana Terhimpun (Rp)": [dana_ads, dana_org, dana_wa, dana_em],
        "ROAS (x)": [roas_ads, 0, roas_wa, roas_em]
    })
    
    st.dataframe(df_summary.style.format({
        "Biaya (Rp)": "Rp {:,.0f}",
        "Dana Terhimpun (Rp)": "Rp {:,.0f}",
        "ROAS (x)": "{:,.2f}"
    }), use_container_width=True)

    col_dl1, col_dl2 = st.columns(2)
    # 1. Export ke CSV
    csv_data = df_summary.to_csv(index=False).encode('utf-8')
    col_dl1.download_button("📥 Unduh CSV", data=csv_data, file_name='proyeksi_zis.csv', mime='text/csv', use_container_width=True)
        
    # 2. Export ke Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='Proyeksi', index=False)
    col_dl2.download_button("📥 Unduh Excel (.xlsx)", data=buffer.getvalue(), file_name="proyeksi_zis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
