import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="ZIS Digital Strategy Engine", layout="wide")

# ================= HELPER FUNCTIONS =================
def safe_div(numerator, denominator, default=0.0):
    return numerator / denominator if denominator > 0 else default

def format_cpa(cpa_value, donatur_count):
    if donatur_count > 0:
        return f"Rp {cpa_value:,.0f}"
    return "N/A"

# ================= SESSION STATE INIT =================
# Menyimpan list data per kanal untuk append log
if 'log_ads' not in st.session_state: st.session_state['log_ads'] = []
if 'log_org' not in st.session_state: st.session_state['log_org'] = []
if 'log_wa' not in st.session_state: st.session_state['log_wa'] = []
if 'log_em' not in st.session_state: st.session_state['log_em'] = []

if 'scen_a' not in st.session_state: st.session_state['scen_a'] = None
if 'scen_b' not in st.session_state: st.session_state['scen_b'] = None

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
    st.header("⚙️ 1. Auto-Fill Data Default")
    uploaded_file = st.file_uploader("Upload CSV Performa", type=['csv'])
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            for key, default_val in default_params.items():
                if key in df_upload.columns:
                    val = df_upload[key].iloc[0]
                    st.session_state[key] = int(val) if isinstance(default_val, int) else float(val)
            st.success("Data berhasil dimuat ke input default!")
        except Exception as e:
            st.error(f"Gagal membaca file CSV: {e}")
    
    st.divider()
    
    st.header("⚠️ 2. What-If Analysis (Risiko)")
    risk_cpm = st.slider("Kenaikan Harga Iklan (CPM) %", 0, 100, 0) / 100
    risk_cr = st.slider("Penurunan Conversion Rate %", 0, 50, 0) / 100

# ================= TAB NAVIGATION =================
tab_ads, tab_org, tab_wa, tab_email, tab_sum, tab_goal, tab_ab = st.tabs([
    "📢 Paid Ads", "📱 Organik", "💬 WA Blast", "✉️ Email", "📈 Ekspor & Total", "🎯 Goal-Seek", "⚖️ A/B Skenario"
])

# ================= TAB: PAID ADS =================
with tab_ads:
    st.header("Kanal Paid Ads")
    with st.form("form_ads"):
        nama_campaign = st.text_input("Nama Campaign", value=f"Campaign Ads #{len(st.session_state['log_ads']) + 1}")
        c1, c2 = st.columns(2)
        budget_ads = c1.number_input("Budget Iklan (Rp)", min_value=0, value=int(st.session_state['budget_ads']), step=500000)
        base_cpm = c1.number_input("Target CPM (Rp)", min_value=0, value=int(st.session_state['base_cpm']), step=1000)
        freq_ads = c1.number_input("Target Frequency", min_value=0.0, value=float(st.session_state['freq_ads']), step=0.1, format="%g")
        ctr_ads = c1.number_input("Target CTR (%)", min_value=0.0, value=float(st.session_state['ctr_ads']), step=0.1, format="%g")
        
        lp_rate_ads = c2.number_input("Target LP View Rate (%)", min_value=0.0, value=float(st.session_state['lp_rate_ads']), step=1.0, format="%g")
        base_cr_ads = c2.number_input("Target CR Ads (%)", min_value=0.0, value=float(st.session_state['base_cr_ads']), step=0.1, format="%g")
        avg_don_ads = c2.number_input("Rata-rata Donasi Ads (Rp)", min_value=0, value=int(st.session_state['avg_don_ads']), step=10000)

        submit_ads = st.form_submit_button("➕ Tambahkan Kalkulasi Campaign")
        
        if submit_ads:
            actual_cpm = base_cpm * (1 + risk_cpm)
            actual_cr = (base_cr_ads / 100) * (1 - risk_cr)
            imp = safe_div(budget_ads, actual_cpm) * 1000
            reach = safe_div(imp, freq_ads)
            clicks = imp * (ctr_ads / 100)
            lp_views = clicks * (lp_rate_ads / 100)
            donatur = lp_views * actual_cr
            dana = donatur * avg_don_ads
            roas = safe_div(dana, budget_ads)
            
            st.session_state['log_ads'].append({
                "Nama Campaign": nama_campaign,
                "Budget (Rp)": budget_ads, "CPM (Rp)": base_cpm, "Freq": freq_ads, 
                "CTR (%)": ctr_ads, "LP View (%)": lp_rate_ads, "CR (%)": base_cr_ads, 
                "Avg Donasi (Rp)": avg_don_ads,
                "_Imp": imp, "_Reach": reach, "_Clicks": clicks, "_LPViews": lp_views, 
                "_Donatur": donatur, "_Dana": dana
            })

    if st.session_state['log_ads']:
        st.divider()
        st.subheader("Tabel Log Campaign - Paid Ads")
        df_ads = pd.DataFrame(st.session_state['log_ads'])
        
        # Display table formatted
        display_df = df_ads[["Nama Campaign", "Budget (Rp)", "CPM (Rp)", "Freq", "CTR (%)", "LP View (%)", "CR (%)", "Avg Donasi (Rp)"]].copy()
        display_df["Reach"] = df_ads["_Reach"].map("{:,.0f}".format)
        display_df["Klik"] = df_ads["_Clicks"].map("{:,.0f}".format)
        display_df["Donatur"] = df_ads["_Donatur"].map("{:,.1f}".format)
        display_df["Dana Terhimpun (Rp)"] = df_ads["_Dana"].map("Rp {:,.0f}".format)
        display_df["ROAS"] = (df_ads["_Dana"] / df_ads["Budget (Rp)"]).fillna(0).map("{:.2f} x".format)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Hapus Semua Data Ads"):
            st.session_state['log_ads'] = []
            st.rerun()

        # Aggregate Calcs
        tot_budget_ads = df_ads["Budget (Rp)"].sum()
        tot_imp_ads = df_ads["_Imp"].sum()
        tot_reach_ads = df_ads["_Reach"].sum()
        tot_clicks_ads = df_ads["_Clicks"].sum()
        tot_lp_ads = df_ads["_LPViews"].sum()
        tot_donatur_ads = df_ads["_Donatur"].sum()
        tot_dana_ads = df_ads["_Dana"].sum()
        
        tot_cpc_ads = safe_div(tot_budget_ads, tot_clicks_ads)
        tot_cpa_ads = safe_div(tot_budget_ads, tot_donatur_ads)
        tot_roas_ads = safe_div(tot_dana_ads, tot_budget_ads)

        st.subheader("Agregat Total Paid Ads")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Estimasi Reach", f"{tot_reach_ads:,.0f}")
        m2.metric("Total Estimasi Klik", f"{tot_clicks_ads:,.0f}")
        m3.metric("Total Proyeksi Donatur", f"{tot_donatur_ads:,.1f}")
        m4.metric("Total Dana Terhimpun", f"Rp {tot_dana_ads:,.0f}")

        m5, m6, m7 = st.columns(3)
        m5.metric("Average CPC", f"Rp {tot_cpc_ads:,.0f}")
        m6.metric("Average CPA (Cost/Donor)", format_cpa(tot_cpa_ads, tot_donatur_ads))
        m7.metric("Overall ROAS Ads", f"{tot_roas_ads:.2f} x")
        
        with st.expander("📊 Lihat Visualisasi Corong Konversi (Agregat) Paid Ads"):
            fig = go.Figure(go.Funnel(
                y = ["Impressions", "Ad Clicks", "LP Views", "Donatur Berhasil"],
                x = [tot_imp_ads, tot_clicks_ads, tot_lp_ads, tot_donatur_ads],
                textinfo = "value+percent initial",
                marker = {"color": ["#4C78A8", "#72B7B2", "#F58518", "#E45756"]}
            ))
            fig.update_layout(margin=dict(t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        tot_budget_ads = tot_dana_ads = tot_donatur_ads = tot_roas_ads = 0
        st.info("Belum ada campaign Paid Ads yang dikalkulasi.")

# ================= TAB: ORGANIK =================
with tab_org:
    st.header("Kanal Organic Content")
    with st.form("form_org"):
        nama_campaign_org = st.text_input("Nama Campaign", value=f"Campaign Organik #{len(st.session_state['log_org']) + 1}")
        c1, c2 = st.columns(2)
        reach_org_in = c1.number_input("Estimasi Reach Organik", min_value=0, value=int(st.session_state['reach_org']), step=5000)
        interactions_org = c1.number_input("Total Interactions", min_value=0, value=int(st.session_state['interactions_org']), step=500)
        pv_org = c1.number_input("Profile Visits", min_value=0, value=int(st.session_state['pv_org']), step=100)
        
        lc_org = c2.number_input("Link in Bio Clicks", min_value=0, value=int(st.session_state['lc_org']), step=50)
        base_cr_org = c2.number_input("Target CR Organik (%)", min_value=0.0, value=float(st.session_state['base_cr_org']), step=0.5, format="%g")
        avg_don_org = c2.number_input("Rata-rata Donasi Organik (Rp)", min_value=0, value=int(st.session_state['avg_don_org']), step=25000)

        if st.form_submit_button("➕ Tambahkan Kalkulasi Organik"):
            actual_cr = (base_cr_org / 100) * (1 - risk_cr)
            donatur = lc_org * actual_cr
            dana = donatur * avg_don_org
            
            st.session_state['log_org'].append({
                "Nama Campaign": nama_campaign_org,
                "Reach": reach_org_in, "Interactions": interactions_org, "Profile Visits": pv_org, 
                "Link Clicks": lc_org, "CR (%)": base_cr_org, "Avg Donasi (Rp)": avg_don_org,
                "_Donatur": donatur, "_Dana": dana
            })

    if st.session_state['log_org']:
        st.divider()
        df_org = pd.DataFrame(st.session_state['log_org'])
        display_df_org = df_org.copy().drop(columns=["_Donatur", "_Dana"])
        display_df_org["Donatur"] = df_org["_Donatur"].map("{:,.1f}".format)
        display_df_org["Dana Terhimpun (Rp)"] = df_org["_Dana"].map("Rp {:,.0f}".format)
        st.dataframe(display_df_org, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Hapus Semua Data Organik"):
            st.session_state['log_org'] = []
            st.rerun()

        tot_reach_org = df_org["Reach"].sum()
        tot_pv_org = df_org["Profile Visits"].sum()
        tot_lc_org = df_org["Link Clicks"].sum()
        tot_donatur_org = df_org["_Donatur"].sum()
        tot_dana_org = df_org["_Dana"].sum()

        st.subheader("Agregat Total Organik")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Link Clicks", f"{tot_lc_org:,.0f}")
        m2.metric("Avg CTR Total", f"{(safe_div(tot_lc_org, tot_pv_org)*100):.2f}%")
        m3.metric("Total Estimasi Donatur", f"{tot_donatur_org:,.1f}")
        m4.metric("Total Dana Terhimpun", f"Rp {tot_dana_org:,.0f}")
        
        with st.expander("📊 Lihat Visualisasi Corong Konversi (Agregat) Organik"):
            fig = go.Figure(go.Funnel(
                y = ["Reach", "Profile Visits", "Link Clicks", "Donatur Berhasil"],
                x = [tot_reach_org, tot_pv_org, tot_lc_org, tot_donatur_org],
                textinfo = "value+percent initial",
                marker = {"color": ["#4C78A8", "#72B7B2", "#F58518", "#E45756"]}
            ))
            fig.update_layout(margin=dict(t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        tot_dana_org = tot_donatur_org = 0
        st.info("Belum ada data Organik yang dikalkulasi.")

# ================= TAB: WA BLAST =================
with tab_wa:
    st.header("Kanal WA Blast")
    with st.form("form_wa"):
        nama_campaign_wa = st.text_input("Nama Campaign", value=f"WA Blast #{len(st.session_state['log_wa']) + 1}")
        c1, c2 = st.columns(2)
        db_wa_in = c1.number_input("Total Database WA", min_value=0, value=int(st.session_state['db_wa']), step=1000)
        cpc_wa = c1.number_input("Biaya per Chat (Rp)", min_value=0, value=int(st.session_state['cpc_wa']), step=50)
        del_wa = c1.number_input("Target Delivered WA (%)", min_value=0.0, value=float(st.session_state['del_wa']), step=1.0, format="%g")
        read_wa = c1.number_input("Target Read Rate (%)", min_value=0.0, value=float(st.session_state['read_wa']), step=1.0, format="%g")
        
        ctr_wa = c2.number_input("Target CTR Link WA (%)", min_value=0.0, value=float(st.session_state['ctr_wa']), step=1.0, format="%g")
        base_cr_wa = c2.number_input("Target CR WA (%)", min_value=0.0, value=float(st.session_state['base_cr_wa']), step=1.0, format="%g")
        avg_don_wa = c2.number_input("Rata-rata Donasi WA (Rp)", min_value=0, value=int(st.session_state['avg_don_wa']), step=25000)

        if st.form_submit_button("➕ Tambahkan Kalkulasi WA"):
            actual_cr = (base_cr_wa / 100) * (1 - risk_cr)
            biaya = db_wa_in * cpc_wa
            msg_del = db_wa_in * (del_wa / 100)
            msg_read = msg_del * (read_wa / 100)
            clicks = msg_read * (ctr_wa / 100)
            donatur = clicks * actual_cr
            dana = donatur * avg_don_wa
            
            st.session_state['log_wa'].append({
                "Nama Campaign": nama_campaign_wa,
                "Database": db_wa_in, "Cost/Chat (Rp)": cpc_wa, "Delivered (%)": del_wa, 
                "Read (%)": read_wa, "CTR (%)": ctr_wa, "CR (%)": base_cr_wa, "Avg Donasi (Rp)": avg_don_wa,
                "_Biaya": biaya, "_Delivered": msg_del, "_Read": msg_read, "_Clicks": clicks, 
                "_Donatur": donatur, "_Dana": dana
            })

    if st.session_state['log_wa']:
        st.divider()
        df_wa = pd.DataFrame(st.session_state['log_wa'])
        display_df_wa = df_wa[["Nama Campaign", "Database", "Cost/Chat (Rp)", "Delivered (%)", "Read (%)", "CTR (%)", "CR (%)", "Avg Donasi (Rp)"]].copy()
        display_df_wa["Biaya Blast (Rp)"] = df_wa["_Biaya"].map("Rp {:,.0f}".format)
        display_df_wa["Pesan Dibaca"] = df_wa["_Read"].map("{:,.0f}".format)
        display_df_wa["Donatur"] = df_wa["_Donatur"].map("{:,.1f}".format)
        display_df_wa["Dana Terhimpun (Rp)"] = df_wa["_Dana"].map("Rp {:,.0f}".format)
        display_df_wa["ROAS"] = (df_wa["_Dana"] / df_wa["_Biaya"]).fillna(0).map("{:.2f} x".format)
        
        st.dataframe(display_df_wa, use_container_width=True, hide_index=True)
        if st.button("🗑️ Hapus Semua Data WA"):
            st.session_state['log_wa'] = []
            st.rerun()

        tot_biaya_wa = df_wa["_Biaya"].sum()
        tot_db_wa = df_wa["Database"].sum()
        tot_del_wa = df_wa["_Delivered"].sum()
        tot_read_wa = df_wa["_Read"].sum()
        tot_clicks_wa = df_wa["_Clicks"].sum()
        tot_donatur_wa = df_wa["_Donatur"].sum()
        tot_dana_wa = df_wa["_Dana"].sum()
        tot_roas_wa = safe_div(tot_dana_wa, tot_biaya_wa)

        st.subheader("Agregat Total WA Blast")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Biaya Blast", f"Rp {tot_biaya_wa:,.0f}")
        m2.metric("Total Pesan Dibaca", f"{tot_read_wa:,.0f}")
        m3.metric("Total Donatur", f"{tot_donatur_wa:,.1f}")
        m4.metric("Total Dana Terhimpun", f"Rp {tot_dana_wa:,.0f}")
        st.metric("Overall ROAS WA Blast", f"{tot_roas_wa:.2f} x")
        
        with st.expander("📊 Lihat Visualisasi Corong Konversi (Agregat) WA"):
            fig = go.Figure(go.Funnel(
                y = ["Database", "Delivered", "Read", "Clicks", "Donatur"],
                x = [tot_db_wa, tot_del_wa, tot_read_wa, tot_clicks_wa, tot_donatur_wa],
                textinfo = "value+percent initial",
                marker = {"color": ["#4C78A8", "#54A24B", "#72B7B2", "#F58518", "#E45756"]}
            ))
            fig.update_layout(margin=dict(t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        tot_biaya_wa = tot_dana_wa = tot_donatur_wa = tot_roas_wa = tot_db_wa = 0
        st.info("Belum ada data WA Blast yang dikalkulasi.")

# ================= TAB: EMAIL MARKETING =================
with tab_email:
    st.header("Kanal Email Marketing")
    with st.form("form_em"):
        nama_campaign_em = st.text_input("Nama Campaign", value=f"Email Campaign #{len(st.session_state['log_em']) + 1}")
        c1, c2 = st.columns(2)
        db_em_in = c1.number_input("Total Database Email", min_value=0, value=int(st.session_state['db_em']), step=5000)
        del_em = c1.number_input("Target Delivery Email (%)", min_value=0.0, value=float(st.session_state['del_em']), step=1.0, format="%g")
        open_em = c1.number_input("Target Open Rate (%)", min_value=0.0, value=float(st.session_state['open_em']), step=1.0, format="%g")
        ctr_em = c1.number_input("Target CTR Email (%)", min_value=0.0, value=float(st.session_state['ctr_em']), step=0.5, format="%g")
        
        base_cr_em = c2.number_input("Target CR Email (%)", min_value=0.0, value=float(st.session_state['base_cr_em']), step=1.0, format="%g")
        avg_don_em = c2.number_input("Rata-rata Donasi Email (Rp)", min_value=0, value=int(st.session_state['avg_don_em']), step=50000)
        cost_em_in = c2.number_input("Biaya Campaign Email (Rp)", min_value=0, value=int(st.session_state['cost_em']), step=50000)

        if st.form_submit_button("➕ Tambahkan Kalkulasi Email"):
            actual_cr = (base_cr_em / 100) * (1 - risk_cr)
            msg_del = db_em_in * (del_em / 100)
            msg_open = msg_del * (open_em / 100)
            clicks = msg_open * (ctr_em / 100)
            donatur = clicks * actual_cr
            dana = donatur * avg_don_em
            
            st.session_state['log_em'].append({
                "Nama Campaign": nama_campaign_em,
                "Database": db_em_in, "Biaya Campaign (Rp)": cost_em_in, "Delivery (%)": del_em, 
                "Open (%)": open_em, "CTR (%)": ctr_em, "CR (%)": base_cr_em, "Avg Donasi (Rp)": avg_don_em,
                "_Delivered": msg_del, "_Open": msg_open, "_Clicks": clicks, "_Donatur": donatur, "_Dana": dana
            })

    if st.session_state['log_em']:
        st.divider()
        df_em = pd.DataFrame(st.session_state['log_em'])
        display_df_em = df_em[["Nama Campaign", "Database", "Biaya Campaign (Rp)", "Delivery (%)", "Open (%)", "CTR (%)", "CR (%)", "Avg Donasi (Rp)"]].copy()
        display_df_em["Email Dibuka"] = df_em["_Open"].map("{:,.0f}".format)
        display_df_em["Donatur"] = df_em["_Donatur"].map("{:,.1f}".format)
        display_df_em["Dana Terhimpun (Rp)"] = df_em["_Dana"].map("Rp {:,.0f}".format)
        display_df_em["ROAS"] = (df_em["_Dana"] / df_em["Biaya Campaign (Rp)"]).fillna(0).map("{:.2f} x".format)
        
        st.dataframe(display_df_em, use_container_width=True, hide_index=True)
        if st.button("🗑️ Hapus Semua Data Email"):
            st.session_state['log_em'] = []
            st.rerun()

        tot_biaya_em = df_em["Biaya Campaign (Rp)"].sum()
        tot_db_em = df_em["Database"].sum()
        tot_del_em = df_em["_Delivered"].sum()
        tot_open_em = df_em["_Open"].sum()
        tot_clicks_em = df_em["_Clicks"].sum()
        tot_donatur_em = df_em["_Donatur"].sum()
        tot_dana_em = df_em["_Dana"].sum()
        tot_roas_em = safe_div(tot_dana_em, tot_biaya_em)

        st.subheader("Agregat Total Email Marketing")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Email Dibuka", f"{tot_open_em:,.0f}")
        m2.metric("Total Klik", f"{tot_clicks_em:,.0f}")
        m3.metric("Total Donatur", f"{tot_donatur_em:,.1f}")
        m4.metric("Total Dana Terhimpun", f"Rp {tot_dana_em:,.0f}")
        st.metric("Overall ROAS Email", f"{tot_roas_em:.2f} x")
        
        with st.expander("📊 Lihat Visualisasi Corong Konversi (Agregat) Email"):
            fig = go.Figure(go.Funnel(
                y = ["Database", "Terkirim", "Dibuka", "Klik Link", "Donatur"],
                x = [tot_db_em, tot_del_em, tot_open_em, tot_clicks_em, tot_donatur_em],
                textinfo = "value+percent initial",
                marker = {"color": ["#4C78A8", "#54A24B", "#72B7B2", "#F58518", "#E45756"]}
            ))
            fig.update_layout(margin=dict(t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        tot_biaya_em = tot_dana_em = tot_donatur_em = tot_roas_em = 0
        st.info("Belum ada data Email yang dikalkulasi.")


# ================= PERHITUNGAN TOTAL METRICS (GLOBAL) =================
# Pastikan nilai ini memiliki referensi default jika tabel kosong
total_biaya_global = tot_budget_ads + tot_biaya_wa + tot_biaya_em
total_dana_global = tot_dana_ads + tot_dana_org + tot_dana_wa + tot_dana_em
total_donatur_global = tot_donatur_ads + tot_donatur_org + tot_donatur_wa + tot_donatur_em
overall_roas_global = safe_div(total_dana_global, total_biaya_global)

current_metrics = {
    "Biaya Total": total_biaya_global,
    "Dana Terhimpun": total_dana_global,
    "Total Donatur": total_donatur_global,
    "Overall ROAS": overall_roas_global
}

# ================= TAB: EKSPOR & SUMMARY =================
with tab_sum:
    st.header("📈 Ringkasan Agregat & Ekspor Data")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Biaya Investasi", f"Rp {total_biaya_global:,.0f}")
    c2.metric("Total Donatur", f"{total_donatur_global:,.1f}")
    c3.metric("Dana Terhimpun", f"Rp {total_dana_global:,.0f}")
    c4.metric("Overall ROAS (Semua Kanal)", f"{overall_roas_global:.2f} x")

    df_summary = pd.DataFrame({
        "Kanal Digital": ["Paid Ads", "Organic Content", "WA Blast", "Email Marketing"],
        "Jumlah Campaign": [len(st.session_state['log_ads']), len(st.session_state['log_org']), len(st.session_state['log_wa']), len(st.session_state['log_em'])],
        "Biaya Total (Rp)": [tot_budget_ads, 0, tot_biaya_wa, tot_biaya_em],
        "Proyeksi Donatur": [tot_donatur_ads, tot_donatur_org, tot_donatur_wa, tot_donatur_em],
        "Total Dana Terhimpun (Rp)": [tot_dana_ads, tot_dana_org, tot_dana_wa, tot_dana_em],
        "ROAS Agregat (x)": [tot_roas_ads, 0, tot_roas_wa, tot_roas_em]
    })
    
    st.dataframe(df_summary.style.format({
        "Biaya Total (Rp)": "Rp {:,.0f}",
        "Proyeksi Donatur": "{:,.1f}",
        "Total Dana Terhimpun (Rp)": "Rp {:,.0f}",
        "ROAS Agregat (x)": "{:,.2f}"
    }), use_container_width=True, hide_index=True)

    col_dl1, col_dl2 = st.columns(2)
    csv_data = df_summary.to_csv(index=False).encode('utf-8')
    col_dl1.download_button("📥 Unduh CSV Agregat", data=csv_data, file_name='proyeksi_zis_agregat.csv', mime='text/csv', use_container_width=True)

# ================= TAB: GOAL SEEK =================
with tab_goal:
    st.header("🎯 Kalkulator Mundur (Goal-Seek)")
    st.write("Sistem mendistribusikan kebutuhan modal dari sisa target menggunakan rasio ROAS Agregat pada sesi saat ini.")
    
    target_dana = st.number_input("Target Total Penghimpunan (Rp)", min_value=0, value=1000000000, step=100000000)
    
    sisa_target_berbayar = max(0.0, target_dana - tot_dana_org)
    st.info(f"💡 Target total: Rp {target_dana:,.0f} | Proyeksi Organik Terkumpul: Rp {tot_dana_org:,.0f}")
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
        if pct_ads > 0 and tot_roas_ads <= 0: warnings.append("Paid Ads memiliki porsi tetapi ROAS Agregat 0 (Masukkan data di Tab Ads).")
        if pct_wa > 0 and tot_roas_wa <= 0: warnings.append("WA Blast memiliki porsi tetapi ROAS Agregat 0 (Masukkan data di Tab WA).")
        if pct_em > 0 and tot_roas_em <= 0: warnings.append("Email memiliki porsi tetapi ROAS Agregat 0 (Masukkan data di Tab Email).")
        
        if warnings:
            for w in warnings:
                st.warning(f"⚠️ {w}")
        else:
            req_budget_ads = safe_div(sisa_target_berbayar * pct_ads, tot_roas_ads)
            req_cost_wa = safe_div(sisa_target_berbayar * pct_wa, tot_roas_wa)
            cpc_wa_avg = safe_div(tot_biaya_wa, tot_db_wa) if tot_db_wa > 0 else (st.session_state.get('cpc_wa') or 450)
            req_db_wa = safe_div(req_cost_wa, cpc_wa_avg)
            req_cost_em = safe_div(sisa_target_berbayar * pct_em, tot_roas_em)
            
            st.success("✅ Rekomendasi Alokasi Tambahan Berdasarkan ROAS Saat Ini:")
            m1, m2, m3 = st.columns(3)
            m1.metric("Kebutuhan Budget Ads", f"Rp {req_budget_ads:,.0f}")
            m2.metric("Kebutuhan Database WA", f"{req_db_wa:,.0f} Kontak")
            m3.metric("Kebutuhan Budget Email", f"Rp {req_cost_em:,.0f}")

# ================= TAB: A/B SKENARIO =================
with tab_ab:
    st.header("⚖️ Bandingkan Skenario A vs B")
    st.caption("Menyimpan agregat global dari seluruh kampanye yang ada di tabel saat ini.")
    
    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("💾 Simpan Semua Data Saat Ini sbg Skenario A", use_container_width=True):
        st.session_state['scen_a'] = current_metrics.copy()
        st.success("Skenario A tersimpan.")
        
    if col_btn2.button("💾 Simpan Semua Data Saat Ini sbg Skenario B", use_container_width=True):
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
            fig_ab = px.bar(df_melted, x="Skenario", y="Nilai", color="Indikator", barmode="group", title="Perbandingan Biaya vs Dana Terhimpun (Agregat Global)")
            st.plotly_chart(fig_ab, use_container_width=True)
            
        with c_table:
            st.markdown("**Rincian Agregat Global**")
            st.dataframe(df_ab.set_index("Skenario").style.format({
                "Biaya Total (Rp)": "Rp {:,.0f}",
                "Dana Terhimpun (Rp)": "Rp {:,.0f}",
                "Donatur": "{:,.1f}",
                "ROAS (x)": "{:,.2f}"
            }), use_container_width=True)
    else:
        st.info("Simpan Skenario A dan Skenario B untuk melihat komparasi metrik secara detail.")
