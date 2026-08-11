import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="ZIS Digital Strategy Engine", layout="wide")

# ================= HELPER FUNCTIONS =================
def safe_div(numerator, denominator, default=0.0):
    """Mencegah zero-division error dengan mengembalikan nilai default."""
    return numerator / denominator if denominator > 0 else default

def format_cpa(cpa_value, donatur_count):
    """Memformat CPA agar menunjukkan tak terhingga jika donatur 0."""
    if donatur_count > 0:
        return f"Rp {cpa_value:,.0f}"
    return "N/A"

# ================= SESSION STATE INIT =================
if 'scen_a' not in st.session_state:
    st.session_state['scen_a'] = None
if 'scen_b' not in st.session_state:
    st.session_state['scen_b'] = None

default_params = {
    'budget_ads': 5000000, 'base_cpm': 30000, 'freq_ads': 1.8, 'ctr_ads': 3.0, 'lp_rate_ads': 75.0, 'base_cr_ads': 2.0, 'avg_don_ads': 100000,
    'reach_org': 100000, 'interactions_org': 5000, 'pv_org': 1000, 'lc_org': 300, 'base_cr_org': 5.0, 'avg_don_org': 200000,
    'db_wa': 10000, 'cpc_wa': 450, 'del_wa': 95.0, 'read_wa': 70.0, 'ctr_wa': 15.0, 'base_cr_wa': 20.0, 'avg_don_wa': 350000,
    'db_em': 40000, 'del_em': 98.0, 'open_em': 22.0, 'ctr_em': 4.0, 'base_cr_em': 8.0, 'avg_don_em': 450000, 'cost_em': 200000
}

for key, value in default_params.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.title("🚀 ZIS Digital Strategy Engine")
st.caption("Simulator Budgeting, Manajemen Risiko, & Penentu Target Zakat")

# ================= SIDEBAR: WHAT-IF & UPLOAD =================
with st.sidebar:
    st.header("⚙️ 1. Auto-Fill Data")
    st.write("Upload CSV untuk mengisi input secara otomatis (header harus sesuai parameter).")
    uploaded_file = st.file_uploader("Upload CSV Performa", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            updated_keys = 0
            for key, default_val in default_params.items():
                if key in df_upload.columns:
                    val = df_upload[key].iloc[0]
                    if isinstance(default_val, int):
                        st.session_state[key] = int(val)
                    else:
                        st.session_state[key] = float(val)
                    updated_keys += 1
            if updated_keys > 0:
                st.success(f"Berhasil memuat {updated_keys} parameter dari CSV.")
            else:
                st.warning("File CSV dibaca, tetapi tidak ada header kolom yang cocok dengan parameter.")
        except Exception as e:
            st.error(f"Gagal membaca file CSV: {e}")
    
    st.divider()
    
    st.header("⚠️ 2. What-If Analysis (Risiko)")
    st.write("Simulasikan penurunan kondisi performa (misal di luar Peak Season).")
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

# ================= TAB: PAID ADS =================
with tab_ads:
    st.header("Kanal Paid Ads")
    c1, c2 = st.columns(2)
    budget_ads = c1.number_input("Budget Iklan (Rp)", min_value=0, value=int(st.session_state['budget_ads']), step=500000)
    base_cpm = c1.number_input("Target CPM (Rp)", min_value=0, value=int(st.session_state['base_cpm']), step=1000)
    freq_ads = c1.number_input("Target Frequency", min_value=0.0, value=float(st.session_state['freq_ads']), step=0.1, format="%g")
    ctr_ads = c1.number_input("Target CTR (%)", min_value=0.0, value=float(st.session_state['ctr_ads']), step=0.1, format="%g") / 100
    
    lp_rate_ads = c2.number_input("Target LP View Rate (%)", min_value=0.0, value=float(st.session_state['lp_rate_ads']), step=1.0, format="%g") / 100
    base_cr_ads = c2.number_input("Target CR Ads (%)", min_value=0.0, value=float(st.session_state['base_cr_ads']), step=0.1, format="%g") / 100
    avg_don_ads = c2.number_input("Rata-rata Donasi Ads (Rp)", min_value=0, value=int(st.session_state['avg_don_ads']), step=10000)

    actual_cpm_ads = base_cpm * (1 + risk_cpm)
    actual_cr_ads = base_cr_ads * (1 - risk_cr)
    
    imp_ads = safe_div(budget_ads, actual_cpm_ads) * 1000
    reach_ads = safe_div(imp_ads, freq_ads)
    clicks_ads = imp_ads * ctr_ads
    cpc_ads = safe_div(budget_ads, clicks_ads)
    lp_views_ads = clicks_ads * lp_rate_ads
    donatur_ads = lp_views_ads * actual_cr_ads
    dana_ads = donatur_ads * avg_don_ads
    cpa_ads = safe_div(budget_ads, donatur_ads)
    roas_ads = safe_div(dana_ads, budget_ads)

    st.divider()
    st.subheader("Ringkasan Parameter & Hasil Paid Ads")
    
    # 1-Row Table for Ads
    df_ads_summary = pd.DataFrame([{
        "Budget": f"Rp {budget_ads:,.0f}",
        "CPM": f"Rp {base_cpm:,.0f}",
        "Freq": f"{freq_ads:g}",
        "CTR": f"{ctr_ads*100:g}%",
        "LP View": f"{lp_rate_ads*100:g}%",
        "CR": f"{base_cr_ads*100:g}%",
        "Avg Donasi": f"Rp {avg_don_ads:,.0f}",
        "Reach": f"{reach_ads:,.0f}",
        "Klik": f"{clicks_ads:,.0f}",
        "Donatur": f"{donatur_ads:,.1f}",
        "CPA": format_cpa(cpa_ads, donatur_ads),
        "Dana Terhimpun": f"Rp {dana_ads:,.0f}",
        "ROAS": f"{roas_ads:.2f} x"
    }])
    st.dataframe(df_ads_summary, use_container_width=True, hide_index=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimasi Reach", f"{reach_ads:,.0f}")
    m2.metric("Estimasi Klik", f"{clicks_ads:,.0f}")
    m3.metric("Proyeksi Donatur", f"{donatur_ads:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_ads:,.0f}")
    
    with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) Paid Ads"):
        fig_funnel_ads = go.Figure(go.Funnel(
            y = ["Impressions", "Ad Clicks", "LP Views", "Donatur Berhasil"],
            x = [imp_ads, clicks_ads, lp_views_ads, donatur_ads],
            textinfo = "value+percent initial",
            marker = {"color": ["#4C78A8", "#72B7B2", "#F58518", "#E45756"]}
        ))
        fig_funnel_ads.update_layout(margin=dict(t=20, b=0))
        st.plotly_chart(fig_funnel_ads, use_container_width=True)

# ================= TAB: ORGANIK =================
with tab_org:
    st.header("Kanal Organic Content")
    c1, c2 = st.columns(2)
    reach_org = c1.number_input("Estimasi Reach Organik", min_value=0, value=int(st.session_state['reach_org']), step=5000)
    interactions_org = c1.number_input("Total Interactions", min_value=0, value=int(st.session_state['interactions_org']), step=500)
    pv_org = c1.number_input("Profile Visits", min_value=0, value=int(st.session_state['pv_org']), step=100)
    
    lc_org = c2.number_input("Link in Bio Clicks", min_value=0, value=int(st.session_state['lc_org']), step=50)
    base_cr_org = c2.number_input("Target CR Organik (%)", min_value=0.0, value=float(st.session_state['base_cr_org']), step=0.5, format="%g") / 100
    avg_don_org = c2.number_input("Rata-rata Donasi Organik (Rp)", min_value=0, value=int(st.session_state['avg_don_org']), step=25000)

    actual_cr_org = base_cr_org * (1 - risk_cr)
    er_org = safe_div(interactions_org, reach_org)
    ctr_org = safe_div(lc_org, pv_org)
    donatur_org = lc_org * actual_cr_org
    dana_org = donatur_org * avg_don_org

    st.divider()
    st.subheader("Ringkasan Parameter & Hasil Organik")
    
    # 1-Row Table for Organik
    df_org_summary = pd.DataFrame([{
        "Reach": f"{reach_org:,.0f}",
        "Interactions": f"{interactions_org:,.0f}",
        "Profile Visits": f"{pv_org:,.0f}",
        "Link Clicks": f"{lc_org:,.0f}",
        "CR": f"{base_cr_org*100:g}%",
        "Avg Donasi": f"Rp {avg_don_org:,.0f}",
        "ER": f"{er_org*100:.2f}%",
        "CTR": f"{ctr_org*100:.2f}%",
        "Donatur": f"{donatur_org:,.1f}",
        "Dana Terhimpun": f"Rp {dana_org:,.0f}"
    }])
    st.dataframe(df_org_summary, use_container_width=True, hide_index=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Engagement Rate (ER)", f"{er_org*100:.2f}%")
    m2.metric("Click-Through Rate (CTR)", f"{ctr_org*100:.2f}%")
    m3.metric("Estimasi Donatur", f"{donatur_org:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_org:,.0f}")
    
    with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) Organik"):
        fig_funnel_org = go.Figure(go.Funnel(
            y = ["Reach", "Profile Visits", "Link Clicks", "Donatur Berhasil"],
            x = [reach_org, pv_org, lc_org, donatur_org],
            textinfo = "value+percent initial",
            marker = {"color": ["#4C78A8", "#72B7B2", "#F58518", "#E45756"]}
        ))
        fig_funnel_org.update_layout(margin=dict(t=20, b=0))
        st.plotly_chart(fig_funnel_org, use_container_width=True)

# ================= TAB: WA BLAST =================
with tab_wa:
    st.header("Kanal WA Blast")
    c1, c2 = st.columns(2)
    db_wa = c1.number_input("Total Database WA", min_value=0, value=int(st.session_state['db_wa']), step=1000)
    cpc_wa = c1.number_input("Biaya per Chat (Rp)", min_value=0, value=int(st.session_state['cpc_wa']), step=50)
    del_wa = c1.number_input("Target Delivered WA (%)", min_value=0.0, value=float(st.session_state['del_wa']), step=1.0, format="%g") / 100
    read_wa = c1.number_input("Target Read Rate (%)", min_value=0.0, value=float(st.session_state['read_wa']), step=1.0, format="%g") / 100
    
    ctr_wa = c2.number_input("Target CTR Link WA (%)", min_value=0.0, value=float(st.session_state['ctr_wa']), step=1.0, format="%g") / 100
    base_cr_wa = c2.number_input("Target CR WA (%)", min_value=0.0, value=float(st.session_state['base_cr_wa']), step=1.0, format="%g") / 100
    avg_don_wa = c2.number_input("Rata-rata Donasi WA (Rp)", min_value=0, value=int(st.session_state['avg_don_wa']), step=25000)

    actual_cr_wa = base_cr_wa * (1 - risk_cr)
    total_cost_wa = db_wa * cpc_wa
    
    msg_delivered = db_wa * del_wa
    msg_read = msg_delivered * read_wa
    link_clicks_wa = msg_read * ctr_wa
    donatur_wa = link_clicks_wa * actual_cr_wa
    dana_wa = donatur_wa * avg_don_wa
    roas_wa = safe_div(dana_wa, total_cost_wa)

    st.divider()
    st.subheader("Ringkasan Parameter & Hasil WA Blast")
    
    # 1-Row Table for WA
    df_wa_summary = pd.DataFrame([{
        "Database": f"{db_wa:,.0f}",
        "Cost/Chat": f"Rp {cpc_wa:,.0f}",
        "Delivered": f"{del_wa*100:g}%",
        "Read": f"{read_wa*100:g}%",
        "CTR": f"{ctr_wa*100:g}%",
        "CR": f"{base_cr_wa*100:g}%",
        "Avg Donasi": f"Rp {avg_don_wa:,.0f}",
        "Biaya Blast": f"Rp {total_cost_wa:,.0f}",
        "Pesan Dibaca": f"{msg_read:,.0f}",
        "Donatur": f"{donatur_wa:,.1f}",
        "Dana Terhimpun": f"Rp {dana_wa:,.0f}",
        "ROAS": f"{roas_wa:.2f} x"
    }])
    st.dataframe(df_wa_summary, use_container_width=True, hide_index=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Biaya Blast", f"Rp {total_cost_wa:,.0f}")
    m2.metric("Pesan Dibaca", f"{msg_read:,.0f}")
    m3.metric("Estimasi Donatur", f"{donatur_wa:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_wa:,.0f}")
    
    with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) WA Blast"):
        fig_funnel_wa = go.Figure(go.Funnel(
            y = ["Database", "Delivered", "Read", "Clicks", "Donatur"],
            x = [db_wa, msg_delivered, msg_read, link_clicks_wa, donatur_wa],
            textinfo = "value+percent initial",
            marker = {"color": ["#4C78A8", "#54A24B", "#72B7B2", "#F58518", "#E45756"]}
        ))
        fig_funnel_wa.update_layout(margin=dict(t=20, b=0))
        st.plotly_chart(fig_funnel_wa, use_container_width=True)

# ================= TAB: EMAIL MARKETING =================
with tab_email:
    st.header("Kanal Email Marketing")
    c1, c2 = st.columns(2)
    db_em = c1.number_input("Total Database Email", min_value=0, value=int(st.session_state['db_em']), step=5000)
    del_em = c1.number_input("Target Delivery Email (%)", min_value=0.0, value=float(st.session_state['del_em']), step=1.0, format="%g") / 100
    open_em = c1.number_input("Target Open Rate (%)", min_value=0.0, value=float(st.session_state['open_em']), step=1.0, format="%g") / 100
    ctr_em = c1.number_input("Target CTR Email (%)", min_value=0.0, value=float(st.session_state['ctr_em']), step=0.5, format="%g") / 100
    
    base_cr_em = c2.number_input("Target CR Email (%)", min_value=0.0, value=float(st.session_state['base_cr_em']), step=1.0, format="%g") / 100
    avg_don_em = c2.number_input("Rata-rata Donasi Email (Rp)", min_value=0, value=int(st.session_state['avg_don_em']), step=50000)
    cost_em = c2.number_input("Biaya Campaign Email (Rp)", min_value=0, value=int(st.session_state['cost_em']), step=50000)

    actual_cr_em = base_cr_em * (1 - risk_cr)
    
    em_delivered = db_em * del_em
    em_opened = em_delivered * open_em
    em_clicks = em_opened * ctr_em
    donatur_em = em_clicks * actual_cr_em
    dana_em = donatur_em * avg_don_em
    roas_em = safe_div(dana_em, cost_em)

    st.divider()
    st.subheader("Ringkasan Parameter & Hasil Email Marketing")
    
    # 1-Row Table for Email
    df_em_summary = pd.DataFrame([{
        "Database": f"{db_em:,.0f}",
        "Biaya Campaign": f"Rp {cost_em:,.0f}",
        "Delivery": f"{del_em*100:g}%",
        "Open": f"{open_em*100:g}%",
        "CTR": f"{ctr_em*100:g}%",
        "CR": f"{base_cr_em*100:g}%",
        "Avg Donasi": f"Rp {avg_don_em:,.0f}",
        "Email Dibuka": f"{em_opened:,.0f}",
        "Klik": f"{em_clicks:,.0f}",
        "Donatur": f"{donatur_em:,.1f}",
        "Dana Terhimpun": f"Rp {dana_em:,.0f}",
        "ROAS": f"{roas_em:.2f} x"
    }])
    st.dataframe(df_em_summary, use_container_width=True, hide_index=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Email Dibuka", f"{em_opened:,.0f}")
    m2.metric("Estimasi Klik", f"{em_clicks:,.0f}")
    m3.metric("Estimasi Donatur", f"{donatur_em:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_em:,.0f}")
    
    with st.expander("📊 Lihat Visualisasi Corong Konversi (Funnel) Email"):
        fig_funnel_em = go.Figure(go.Funnel(
            y = ["Database", "Terkirim", "Dibuka", "Klik Link", "Donatur"],
            x = [db_em, em_delivered, em_opened, em_clicks, donatur_em],
            textinfo = "value+percent initial",
            marker = {"color": ["#4C78A8", "#54A24B", "#72B7B2", "#F58518", "#E45756"]}
        ))
        fig_funnel_em.update_layout(margin=dict(t=20, b=0))
        st.plotly_chart(fig_funnel_em, use_container_width=True)

# ================= PERHITUNGAN TOTAL METRICS =================
total_biaya = budget_ads + total_cost_wa + cost_em
total_dana = dana_ads + dana_org + dana_wa + dana_em
overall_donatur = donatur_ads + donatur_org + donatur_wa + donatur_em
overall_roas = safe_div(total_dana, total_biaya)

current_metrics = {
    "Biaya Total": total_biaya,
    "Dana Terhimpun": total_dana,
    "Total Donatur": overall_donatur,
    "Overall ROAS": overall_roas,
    "ROAS Ads": roas_ads,
    "ROAS WA": roas_wa,
    "ROAS Email": roas_em,
    "Cost Ads": budget_ads,
    "Cost WA": total_cost_wa,
    "Cost Email": cost_em
}

# ================= TAB: EKSPOR & SUMMARY =================
with tab_sum:
    st.header("📈 Ringkasan & Ekspor Data")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Biaya Investasi", f"Rp {total_biaya:,.0f}")
    c2.metric("Total Donatur", f"{overall_donatur:,.1f}")
    c3.metric("Dana Terhimpun", f"Rp {total_dana:,.0f}")
    c4.metric("Overall ROAS", f"{overall_roas:.2f} x")

    # Comprehensive DataFrame - Multi Column
    df_summary = pd.DataFrame({
        "Kanal Digital": ["Paid Ads", "Organic Content", "WA Blast", "Email Marketing"],
        "Basis Target (Reach/DB)": [reach_ads, reach_org, db_wa, db_em],
        "Rasio Klik/Interaksi (%)": [ctr_ads * 100, ctr_org * 100, ctr_wa * 100, ctr_em * 100],
        "Conversion Rate (%)": [base_cr_ads * 100, base_cr_org * 100, base_cr_wa * 100, base_cr_em * 100],
        "Avg Donasi (Rp)": [avg_don_ads, avg_don_org, avg_don_wa, avg_don_em],
        "Biaya Total (Rp)": [budget_ads, 0, total_cost_wa, cost_em],
        "Proyeksi Donatur": [donatur_ads, donatur_org, donatur_wa, donatur_em],
        "Total Dana Terhimpun (Rp)": [dana_ads, dana_org, dana_wa, dana_em],
        "ROAS (x)": [roas_ads, 0, roas_wa, roas_em]
    })
    
    # Formatter dict for the Pandas Styler
    st.dataframe(df_summary.style.format({
        "Basis Target (Reach/DB)": "{:,.0f}",
        "Rasio Klik/Interaksi (%)": "{:,.2f}%",
        "Conversion Rate (%)": "{:,.2f}%",
        "Avg Donasi (Rp)": "Rp {:,.0f}",
        "Biaya Total (Rp)": "Rp {:,.0f}",
        "Proyeksi Donatur": "{:,.1f}",
        "Total Dana Terhimpun (Rp)": "Rp {:,.0f}",
        "ROAS (x)": "{:,.2f}"
    }), use_container_width=True, hide_index=True)

    col_dl1, col_dl2 = st.columns(2)
    csv_data = df_summary.to_csv(index=False).encode('utf-8')
    col_dl1.download_button("📥 Unduh CSV", data=csv_data, file_name='proyeksi_zis.csv', mime='text/csv', use_container_width=True)
        
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='Proyeksi', index=False)
    col_dl2.download_button("📥 Unduh Excel (.xlsx)", data=buffer.getvalue(), file_name="proyeksi_zis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# ================= TAB: GOAL SEEK =================
with tab_goal:
    st.header("🎯 Kalkulator Mundur (Goal-Seek)")
    st.write("Sistem menghitung mundur kebutuhan modal dari sisa target setelah dikurangi kontribusi Organik.")
    
    target_dana = st.number_input("Target Total Penghimpunan (Rp)", min_value=0, value=1000000000, step=100000000)
    
    sisa_target_berbayar = max(0.0, target_dana - dana_org)
    st.info(f"💡 Target total: Rp {target_dana:,.0f} | Proyeksi Organik (Rp 0 Cost): Rp {dana_org:,.0f}")
    st.markdown(f"**Target Sisa yang dialokasikan ke Paid Channels:** Rp {sisa_target_berbayar:,.0f}")

    st.subheader("Distribusi Sisa Target (%)")
    col_pct1, col_pct2, col_pct3 = st.columns(3)
    
    pct_ads = col_pct1.number_input("Porsi Paid Ads (%)", min_value=0.0, max_value=100.0, value=50.0, step=5.0, format="%g") / 100
    pct_wa = col_pct2.number_input("Porsi WA Blast (%)", min_value=0.0, max_value=100.0, value=30.0, step=5.0, format="%g") / 100
    pct_em = col_pct3.number_input("Porsi Email (%)", min_value=0.0, max_value=100.0, value=20.0, step=5.0, format="%g") / 100
    
    if round(pct_ads + pct_wa + pct_em, 2) != 1.0:
        st.error("⚠️ Total Porsi harus tepat 100%")
    else:
        warnings = []
        if pct_ads > 0 and roas_ads <= 0: warnings.append("Paid Ads memiliki porsi target tetapi ROAS bernilai 0.")
        if pct_wa > 0 and roas_wa <= 0: warnings.append("WA Blast memiliki porsi target tetapi ROAS bernilai 0.")
        if pct_em > 0 and roas_em <= 0: warnings.append("Email memiliki porsi target tetapi ROAS bernilai 0.")
        
        if warnings:
            for w in warnings:
                st.warning(f"⚠️ {w} (Sesuaikan konversi di tab terkait untuk melanjutkan perhitungan).")
        else:
            req_budget_ads = safe_div(sisa_target_berbayar * pct_ads, roas_ads)
            req_cost_wa = safe_div(sisa_target_berbayar * pct_wa, roas_wa)
            req_db_wa = safe_div(req_cost_wa, cpc_wa)
            req_cost_em = safe_div(sisa_target_berbayar * pct_em, roas_em)
            
            st.success("✅ Rekomendasi Alokasi Berdasarkan ROAS Saat Ini:")
            m1, m2, m3 = st.columns(3)
            m1.metric("Kebutuhan Budget Ads", f"Rp {req_budget_ads:,.0f}")
            m2.metric("Kebutuhan Database WA", f"{req_db_wa:,.0f} Kontak")
            m3.metric("Kebutuhan Budget Email", f"Rp {req_cost_em:,.0f}")

# ================= TAB: A/B SKENARIO =================
with tab_ab:
    st.header("⚖️ Bandingkan Skenario A vs B")
    
    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("💾 Simpan Sebagai Skenario A", use_container_width=True):
        st.session_state['scen_a'] = current_metrics.copy()
        st.success("Skenario A tersimpan.")
        
    if col_btn2.button("💾 Simpan Sebagai Skenario B", use_container_width=True):
        st.session_state['scen_b'] = current_metrics.copy()
        st.success("Skenario B tersimpan.")

    if st.session_state['scen_a'] and st.session_state['scen_b']:
        df_ab = pd.DataFrame([
            {
                "Skenario": "A", 
                "Biaya Total (Rp)": st.session_state['scen_a']["Biaya Total"],
                "Dana Terhimpun (Rp)": st.session_state['scen_a']["Dana Terhimpun"],
                "Donatur": st.session_state['scen_a']["Total Donatur"],
                "ROAS (x)": st.session_state['scen_a']["Overall ROAS"]
            },
            {
                "Skenario": "B", 
                "Biaya Total (Rp)": st.session_state['scen_b']["Biaya Total"],
                "Dana Terhimpun (Rp)": st.session_state['scen_b']["Dana Terhimpun"],
                "Donatur": st.session_state['scen_b']["Total Donatur"],
                "ROAS (x)": st.session_state['scen_b']["Overall ROAS"]
            }
        ])
        
        c_chart, c_table = st.columns([3, 2])
        
        with c_chart:
            df_melted = df_ab.melt(id_vars=["Skenario"], value_vars=["Biaya Total (Rp)", "Dana Terhimpun (Rp)"], var_name="Indikator", value_name="Nilai")
            fig_ab = px.bar(df_melted, x="Skenario", y="Nilai", color="Indikator", barmode="group", title="Perbandingan Biaya vs Dana Terhimpun")
            st.plotly_chart(fig_ab, use_container_width=True)
            
        with c_table:
            st.markdown("**Rincian Parameter Skenario**")
            st.dataframe(df_ab.set_index("Skenario").style.format({
                "Biaya Total (Rp)": "Rp {:,.0f}",
                "Dana Terhimpun (Rp)": "Rp {:,.0f}",
                "Donatur": "{:,.1f}",
                "ROAS (x)": "{:,.2f}"
            }), use_container_width=True)
            
    else:
        st.info("Simpan Skenario A dan Skenario B untuk melihat komparasi metrik secara detail.")
