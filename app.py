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
    
    st.divider()
    
    st.header("⚠️ 2. What-If Analysis (Risiko)")
    st.write("Simulasikan jika terjadi kondisi pasar yang memburuk (Peak Season).")
    risk_cpm = st.slider("Kenaikan Harga Iklan (CPM) %", 0, 100, 0) / 100
    risk_cr = st.slider("Penurunan Conversion Rate %", 0, 50, 0) / 100

# ================= TAB NAVIGATION =================
tab_ads, tab_org, tab_wa, tab_email, tab_sum, tab_goal, tab_ab = st.tabs([
    "📢 Paid Ads", 
    "📱 Organik", 
    "💬 WA Blast", 
    "✉️ Email", 
    "📈 Ekspor & Total",
    "🎯 Goal-Seek", 
    "⚖️ A/B Skenario"
])

# ================= INPUT KANAL =================
with tab_ads:
    st.header("Kanal Paid Ads")
    c1, c2 = st.columns(2)
    # Default value disesuaikan dengan screenshot terbaru
    budget_ads = c1.number_input("Budget Iklan (Rp)", min_value=0, value=50000000, step=500000)
    base_cpm = c1.number_input("Target CPM (Rp)", min_value=0, value=2000, step=1000)
    freq_ads = c1.number_input("Target Frequency", min_value=0.0, value=1.30, step=0.1)
    ctr_ads = c1.number_input("Target CTR (%)", min_value=0.0, value=5.00, step=0.1) / 100
    
    lp_rate_ads = c2.number_input("Target LP View Rate (%)", min_value=0.0, value=75.00, step=1.0) / 100
    base_cr_ads = c2.number_input("Target CR Ads (%)", min_value=0.0, value=2.00, step=0.1) / 100
    avg_don_ads = c2.number_input("Rata-rata Donasi Ads (Rp)", min_value=0, value=100000, step=10000)

    # Kalkulasi Ads
    actual_cpm_ads = base_cpm * (1 + risk_cpm)
    actual_cr_ads = base_cr_ads * (1 - risk_cr)
    
    imp_ads = (budget_ads / actual_cpm_ads) * 1000 if actual_cpm_ads > 0 else 0
    reach_ads = imp_ads / freq_ads if freq_ads > 0 else 0
    clicks_ads = imp_ads * ctr_ads
    cpc_ads = budget_ads / clicks_ads if clicks_ads > 0 else 0
    lp_views_ads = clicks_ads * lp_rate_ads
    donatur_ads = lp_views_ads * actual_cr_ads
    dana_ads = donatur_ads * avg_don_ads
    cpa_ads = budget_ads / donatur_ads if donatur_ads > 0 else 0
    roas_ads = dana_ads / budget_ads if budget_ads > 0 else 0

    st.divider()
    
    st.subheader("Proyeksi Hasil Paid Ads")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimasi Reach", f"{reach_ads:,.0f}")
    m2.metric("Estimasi Klik", f"{clicks_ads:,.0f}")
    m3.metric("Proyeksi Donatur", f"{donatur_ads:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_ads:,.0f}")

    m5, m6, m7 = st.columns(3)
    m5.metric("Proyeksi CPC", f"Rp {cpc_ads:,.0f}")
    m6.metric("Target CPA (Cost/Donor)", f"Rp {cpa_ads:,.0f}")
    m7.metric("Proyeksi ROAS", f"{roas_ads:.2f} x")
    
    st.write("") 
    with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) Paid Ads"):
        fig_funnel_ads = go.Figure(go.Funnel(
            y = ["Impressions (Jangkauan)", "Ad Clicks (Klik Iklan)", "LP Views (Masuk Web Zakat)", "Donatur Berhasil"],
            x = [imp_ads, clicks_ads, lp_views_ads, donatur_ads],
            textinfo = "value+percent initial",
            marker = {"color": ["#4C78A8", "#72B7B2", "#F58518", "#E45756"]}
        ))
        fig_funnel_ads.update_layout(title="Corong Konversi (Funnel) - Paid Ads", margin=dict(t=40, b=0))
        st.plotly_chart(fig_funnel_ads, use_container_width=True)

with tab_org:
    st.header("Kanal Organic Content")
    c1, c2 = st.columns(2)
    reach_org = c1.number_input("Estimasi Reach Organik", min_value=0, value=100000, step=5000)
    interactions_org = c1.number_input("Total Interactions", min_value=0, value=5000, step=500)
    pv_org = c1.number_input("Profile Visits", min_value=0, value=1000, step=100)
    
    lc_org = c2.number_input("Link in Bio Clicks", min_value=0, value=300, step=50)
    base_cr_org = c2.number_input("Target CR Organik (%)", min_value=0.0, value=5.0, step=0.5) / 100
    avg_don_org = c2.number_input("Rata-rata Donasi Organik (Rp)", min_value=0, value=200000, step=25000)

    # Kalkulasi Organik
    actual_cr_org = base_cr_org * (1 - risk_cr)
    er_org = (interactions_org / reach_org) if reach_org > 0 else 0
    ctr_org = (lc_org / pv_org) if pv_org > 0 else 0
    donatur_org = lc_org * actual_cr_org
    dana_org = donatur_org * avg_don_org

    st.divider()
    
    st.subheader("Proyeksi Hasil Organik")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Engagement Rate (ER)", f"{er_org*100:.2f}%")
    m2.metric("Click-Through Rate (CTR)", f"{ctr_org*100:.2f}%")
    m3.metric("Estimasi Donatur", f"{donatur_org:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_org:,.0f}")
    
    st.write("") 
    with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) Organik"):
        fig_funnel_org = go.Figure(go.Funnel(
            y = ["Reach (Jangkauan Konten)", "Profile Visits (Kunjungan Profil)", "Link Clicks (Klik Link Bio)", "Donatur Berhasil"],
            x = [reach_org, pv_org, lc_org, donatur_org],
            textinfo = "value+percent initial",
            marker = {"color": ["#4C78A8", "#72B7B2", "#F58518", "#E45756"]}
        ))
        fig_funnel_org.update_layout(title="Corong Konversi (Funnel) - Organic Content", margin=dict(t=40, b=0))
        st.plotly_chart(fig_funnel_org, use_container_width=True)

with tab_wa:
    st.header("Kanal WA Blast")
    c1, c2 = st.columns(2)
    db_wa = c1.number_input("Total Database WA", min_value=0, value=10000, step=1000)
    cpc_wa = c1.number_input("Biaya per Chat (Rp)", min_value=0, value=450, step=50)
    del_wa = c1.number_input("Target Delivered WA (%)", min_value=0.0, value=95.0, step=1.0) / 100
    read_wa = c1.number_input("Target Read Rate (%)", min_value=0.0, value=70.0, step=1.0) / 100
    
    ctr_wa = c2.number_input("Target CTR Link WA (%)", min_value=0.0, value=15.0, step=1.0) / 100
    base_cr_wa = c2.number_input("Target CR WA (%)", min_value=0.0, value=20.0, step=1.0) / 100
    avg_don_wa = c2.number_input("Rata-rata Donasi WA (Rp)", min_value=0, value=350000, step=25000)

    # Kalkulasi WA
    actual_cr_wa = base_cr_wa * (1 - risk_cr)
    total_cost_wa = db_wa * cpc_wa
    
    msg_delivered = db_wa * del_wa
    msg_read = msg_delivered * read_wa
    link_clicks_wa = msg_read * ctr_wa
    donatur_wa = link_clicks_wa * actual_cr_wa
    dana_wa = donatur_wa * avg_don_wa
    roas_wa = dana_wa / total_cost_wa if total_cost_wa > 0 else 0
    cpa_wa = total_cost_wa / donatur_wa if donatur_wa > 0 else 0

    st.divider()
    
    st.subheader("Proyeksi Hasil WA Blast")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Biaya Blast", f"Rp {total_cost_wa:,.0f}")
    m2.metric("Pesan Dibaca", f"{msg_read:,.0f}")
    m3.metric("Estimasi Donatur", f"{donatur_wa:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_wa:,.0f}")
    st.metric("Proyeksi ROAS WA Blast", f"{roas_wa:.2f} x")
    
    st.write("") 
    with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) WA Blast"):
        fig_funnel_wa = go.Figure(go.Funnel(
            y = ["Database Nomor", "Pesan Terkirim (Delivered)", "Pesan Dibaca (Read)", "Klik Link (CTR)", "Donatur Berhasil"],
            x = [db_wa, msg_delivered, msg_read, link_clicks_wa, donatur_wa],
            textinfo = "value+percent initial",
            marker = {"color": ["#4C78A8", "#54A24B", "#72B7B2", "#F58518", "#E45756"]}
        ))
        fig_funnel_wa.update_layout(title="Corong Konversi (Funnel) - WA Blast", margin=dict(t=40, b=0))
        st.plotly_chart(fig_funnel_wa, use_container_width=True)

with tab_email:
    st.header("Kanal Email Marketing")
    c1, c2 = st.columns(2)
    db_em = c1.number_input("Total Database Email", min_value=0, value=40000, step=5000)
    del_em = c1.number_input("Target Delivery Email (%)", min_value=0.0, value=98.0, step=1.0) / 100
    open_em = c1.number_input("Target Open Rate (%)", min_value=0.0, value=22.0, step=1.0) / 100
    ctr_em = c1.number_input("Target CTR Email (%)", min_value=0.0, value=4.0, step=0.5) / 100
    
    base_cr_em = c2.number_input("Target CR Email (%)", min_value=0.0, value=8.0, step=1.0) / 100
    avg_don_em = c2.number_input("Rata-rata Donasi Email (Rp)", min_value=0, value=450000, step=50000)
    cost_em = c2.number_input("Biaya Campaign Email (Rp)", min_value=0, value=200000, step=50000)

    # Kalkulasi Email
    actual_cr_em = base_cr_em * (1 - risk_cr)
    
    em_delivered = db_em * del_em
    em_opened = em_delivered * open_em
    em_clicks = em_opened * ctr_em
    donatur_em = em_clicks * actual_cr_em
    dana_em = donatur_em * avg_don_em
    roas_em = dana_em / cost_em if cost_em > 0 else 0
    cpa_em = cost_em / donatur_em if donatur_em > 0 else 0

    st.divider()
    
    st.subheader("Proyeksi Hasil Email Marketing")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Email Dibuka", f"{em_opened:,.0f}")
    m2.metric("Estimasi Klik", f"{em_clicks:,.0f}")
    m3.metric("Estimasi Donatur", f"{donatur_em:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_em:,.0f}")
    st.metric("Proyeksi ROAS Email", f"{roas_em:.2f} x")
    
    st.write("") 
    with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) Email"):
        fig_funnel_em = go.Figure(go.Funnel(
            y = ["Database Email", "Email Terkirim", "Email Dibuka (Open)", "Klik Link", "Donatur Berhasil"],
            x = [db_em, em_delivered, em_opened, em_clicks, donatur_em],
            textinfo = "value+percent initial",
            marker = {"color": ["#4C78A8", "#54A24B", "#72B7B2", "#F58518", "#E45756"]}
        ))
        fig_funnel_em.update_layout(title="Corong Konversi (Funnel) - Email Marketing", margin=dict(t=40, b=0))
        st.plotly_chart(fig_funnel_em, use_container_width=True)

# ================= PERHITUNGAN TOTAL =================
total_biaya = budget_ads + total_cost_wa + cost_em
total_dana = dana_ads + dana_org + dana_wa + dana_em
overall_donatur = donatur_ads + donatur_org + donatur_wa + donatur_em

current_metrics = {
    "Biaya Total": total_biaya,
    "Dana Terhimpun": total_dana,
    "Donatur": overall_donatur,
    "ROAS Ads": roas_ads,
    "ROAS WA": roas_wa,
    "ROAS Email": roas_em
}

# ================= TAB: EKSPOR & SUMMARY (VERSI LENGKAP) =================
with tab_sum:
    st.header("📈 Ringkasan & Ekspor Data")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Biaya Investasi", f"Rp {total_biaya:,.0f}")
    c2.metric("Total Donatur", f"{current_metrics['Donatur']:,.1f}")
    c3.metric("Dana Terhimpun", f"Rp {total_dana:,.0f}")
    overall_roas = total_dana / total_biaya if total_biaya > 0 else 0
    c4.metric("Overall ROAS", f"{overall_roas:.2f} x")

    # DF SUPER LENGKAP: Mengambil Seluruh Parameter Input dan Hasil Kalkulasi
    df_summary = pd.DataFrame({
        "Kanal Digital": ["Paid Ads", "Organic Content", "WA Blast", "Email Marketing"],
        "Biaya Investasi (Rp)": [budget_ads, 0, total_cost_wa, cost_em],
        "Biaya Satuan (Rp)": [base_cpm, None, cpc_wa, None],
        "Target Frequency": [freq_ads, None, None, None],
        "Basis Audiens (Database/Jangkauan)": [imp_ads, reach_org, db_wa, db_em],
        "Interaksi Organik": [None, interactions_org, None, None],
        "Target Delivered (%)": [None, None, del_wa*100, del_em*100],
        "Total Pesan Terkirim": [None, None, msg_delivered, em_delivered],
        "Target Read/Open (%)": [None, None, read_wa*100, open_em*100],
        "Total Dibaca / Profile Visits": [None, pv_org, msg_read, em_opened],
        "Target CTR (%)": [ctr_ads*100, ctr_org*100, ctr_wa*100, ctr_em*100],
        "Total Klik (Clicks)": [clicks_ads, lc_org, link_clicks_wa, em_clicks],
        "Target LP View Rate (%)": [lp_rate_ads*100, None, None, None],
        "Total LP Views": [lp_views_ads, None, None, None],
        "Target Conversion Rate (%)": [base_cr_ads*100, base_cr_org*100, base_cr_wa*100, base_cr_em*100],
        "Rata-rata Donasi (Rp)": [avg_don_ads, avg_don_org, avg_don_wa, avg_don_em],
        "Estimasi Donatur Berhasil": [donatur_ads, donatur_org, donatur_wa, donatur_em],
        "Target CPA (Rp)": [cpa_ads, None, cpa_wa, cpa_em],
        "Dana Terhimpun (Rp)": [dana_ads, dana_org, dana_wa, dana_em],
        "Proyeksi ROAS (x)": [roas_ads, None, roas_wa, roas_em]
    })
    
    # Custom Formatter agar tampilan Streamlit rapi, tetapi export tetap berupa angka murni
    def format_rp(val):
        return f"Rp {val:,.0f}" if pd.notnull(val) else "-"
    def format_pct(val):
        return f"{val:,.2f}%" if pd.notnull(val) else "-"
    def format_num(val):
        return f"{val:,.1f}" if pd.notnull(val) else "-"
    def format_roas(val):
        return f"{val:,.2f} x" if pd.notnull(val) else "-"

    st.subheader("Data Lengkap Parameter & Proyeksi")
    st.write("Tabel ini menyertakan seluruh komponen input dan kalkulasi. Geser ke kanan untuk melihat kolom selengkapnya.")
    st.dataframe(df_summary.style.format({
        "Biaya Investasi (Rp)": format_rp,
        "Biaya Satuan (Rp)": format_rp,
        "Target Frequency": format_num,
        "Basis Audiens (Database/Jangkauan)": format_num,
        "Interaksi Organik": format_num,
        "Target Delivered (%)": format_pct,
        "Total Pesan Terkirim": format_num,
        "Target Read/Open (%)": format_pct,
        "Total Dibaca / Profile Visits": format_num,
        "Target CTR (%)": format_pct,
        "Total Klik (Clicks)": format_num,
        "Target LP View Rate (%)": format_pct,
        "Total LP Views": format_num,
        "Target Conversion Rate (%)": format_pct,
        "Rata-rata Donasi (Rp)": format_rp,
        "Estimasi Donatur Berhasil": format_num,
        "Target CPA (Rp)": format_rp,
        "Dana Terhimpun (Rp)": format_rp,
        "Proyeksi ROAS (x)": format_roas
    }), use_container_width=True)

    col_dl1, col_dl2 = st.columns(2)
    # Unduh CSV
    csv_data = df_summary.to_csv(index=False).encode('utf-8')
    col_dl1.download_button("📥 Unduh CSV", data=csv_data, file_name='proyeksi_zis_lengkap.csv', mime='text/csv', use_container_width=True)
        
    # Unduh Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='Proyeksi_Lengkap', index=False)
    col_dl2.download_button("📥 Unduh Excel (.xlsx)", data=buffer.getvalue(), file_name="proyeksi_zis_lengkap.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# ================= TAB: GOAL SEEK =================
with tab_goal:
    st.header("🎯 Kalkulator Mundur (Goal-Seek)")
    st.write("Masukkan Target Penghimpunan ZIS Anda bulan ini, dan sistem akan menghitung mundur kebutuhan budget & database berdasar performa saat ini.")
    
    target_dana = st.number_input("Target Total Penghimpunan (Rp)", min_value=0, value=1000000000, step=100000000)
    
    st.subheader("Distribusi Target per Kanal (%)")
    col_pct1, col_pct2, col_pct3 = st.columns(3)
    
    pct_ads = col_pct1.number_input("Porsi Paid Ads (%)", min_value=0, max_value=100, value=50, step=5) / 100
    pct_wa = col_pct2.number_input("Porsi WA Blast (%)", min_value=0, max_value=100, value=30, step=5) / 100
    pct_em = col_pct3.number_input("Porsi Email (%)", min_value=0, max_value=100, value=20, step=5) / 100
    
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
    
    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("💾 Simpan Angka Saat Ini sbg Skenario A", use_container_width=True):
        st.session_state['scen_a'] = current_metrics
        st.success("Skenario A tersimpan!")
        
    if col_btn2.button("💾 Simpan Angka Saat Ini sbg Skenario B", use_container_width=True):
        st.session_state['scen_b'] = current_metrics
        st.success("Skenario B tersimpan!")

    if st.session_state['scen_a'] and st.session_state['scen_b']:
        df_ab = pd.DataFrame([
            {"Skenario": "Skenario A", "Dana Terhimpun (Rp)": st.session_state['scen_a']["Dana Terhimpun"], "Biaya Investasi (Rp)": st.session_state['scen_a']["Biaya Total"]},
            {"Skenario": "Skenario B", "Dana Terhimpun (Rp)": st.session_state['scen_b']["Dana Terhimpun"], "Biaya Investasi (Rp)": st.session_state['scen_b']["Biaya Total"]}
        ])
        fig_ab = px.bar(df_ab, x="Skenario", y=["Biaya Investasi (Rp)", "Dana Terhimpun (Rp)"], barmode="group", title="Perbandingan Biaya vs Hasil")
        st.plotly_chart(fig_ab, use_container_width=True)
    else:
        st.info("Silakan simpan Skenario A dan Skenario B terlebih dahulu untuk melihat grafik perbandingan.")
