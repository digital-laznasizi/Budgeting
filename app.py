import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Simulator Budgeting Digital ZIS", layout="wide")

st.title("📊 Simulator Budgeting Digital Fundraising ZIS")
st.caption("Masukan angka parameter kustom Anda di setiap kanal untuk melihat proyeksi penghimpunan dana.")

# Tab navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📢 Paid Ads", 
    "📱 Organic Content", 
    "💬 WA Blast", 
    "✉️ Email Marketing",
    "📈 Ringkasan & Total"
])

# ---------------- TAB 1: PAID ADS ----------------
with tab1:
    st.header("1. Digital Paid Ads (Meta, Google, TikTok)")
    col1, col2 = st.columns(2)
    with col1:
        budget_ads = st.number_input("Budget Iklan (Rp)", value=5000000, step=500000, key="b_ads")
        cpm_ads = st.number_input("Target CPM (Rp)", value=30000, step=1000, key="cpm_ads")
        freq_ads = st.number_input("Target Frequency", value=1.8, step=0.1, key="freq_ads")
        ctr_ads = st.number_input("Target CTR (%)", value=3.0, step=0.1, key="ctr_ads") / 100
    with col2:
        lp_rate_ads = st.number_input("Target LP View Rate (%)", value=75.0, step=1.0, key="lp_ads") / 100
        cr_ads = st.number_input("Target Conversion Rate (%)", value=2.0, step=0.1, key="cr_ads") / 100
        avg_don_ads = st.number_input("Rata-rata Donasi / Average Donation (Rp)", value=100000, step=10000, key="avg_ads")

    imp_ads = (budget_ads / cpm_ads) * 1000 if cpm_ads > 0 else 0
    reach_ads = imp_ads / freq_ads if freq_ads > 0 else 0
    clicks_ads = imp_ads * ctr_ads
    cpc_ads = budget_ads / clicks_ads if clicks_ads > 0 else 0
    lp_views_ads = clicks_ads * lp_rate_ads
    donatur_ads = lp_views_ads * cr_ads
    dana_ads = donatur_ads * avg_don_ads
    cpa_ads = budget_ads / donatur_ads if donatur_ads > 0 else 0
    roas_ads = dana_ads / budget_ads if budget_ads > 0 else 0

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

# ---------------- TAB 2: ORGANIC CONTENT ----------------
with tab2:
    st.header("2. Organic Content (Social Media & Web)")
    col1, col2 = st.columns(2)
    with col1:
        reach_org = st.number_input("Estimasi Reach Organik", value=100000, step=5000, key="r_org")
        interactions_org = st.number_input("Total Interactions", value=5000, step=500, key="i_org")
        profile_visits_org = st.number_input("Profile Visits", value=1000, step=100, key="pv_org")
    with col2:
        link_clicks_org = st.number_input("Link in Bio Clicks", value=300, step=50, key="lc_org")
        cr_org = st.number_input("Target Conversion Rate (%)", value=5.0, step=0.5, key="cr_org") / 100
        avg_don_org = st.number_input("Rata-rata Donasi (Rp)", value=200000, step=25000, key="avg_org")

    er_org = (interactions_org / reach_org) if reach_org > 0 else 0
    ctr_org = (link_clicks_org / profile_visits_org) if profile_visits_org > 0 else 0
    donatur_org = link_clicks_org * cr_org
    dana_org = donatur_org * avg_don_org

    st.subheader("Proyeksi Hasil Organik")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Engagement Rate (ER)", f"{er_org*100:.2f}%")
    m2.metric("Click-Through Rate (CTR)", f"{ctr_org*100:.2f}%")
    m3.metric("Estimasi Donatur", f"{donatur_org:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_org:,.0f}")

# ---------------- TAB 3: WA BLAST ----------------
with tab3:
    st.header("3. WA Blast / WABA")
    col1, col2 = st.columns(2)
    with col1:
        db_wa = st.number_input("Total Database Nomor", value=10000, step=1000, key="db_wa")
        cost_per_chat_wa = st.number_input("Biaya per Chat (Rp)", value=450, step=50, key="cpc_wa")
        deliv_rate_wa = st.number_input("Target Delivered Rate (%)", value=95.0, step=1.0, key="del_wa") / 100
        read_rate_wa = st.number_input("Target Read Rate (%)", value=70.0, step=1.0, key="read_wa") / 100
    with col2:
        ctr_wa = st.number_input("Target CTR Link (%)", value=15.0, step=1.0, key="ctr_wa") / 100
        cr_wa = st.number_input("Target Conversion Rate (%)", value=20.0, step=1.0, key="cr_wa") / 100
        avg_don_wa = st.number_input("Rata-rata Donasi (Rp)", value=350000, step=25000, key="avg_wa")

    total_cost_wa = db_wa * cost_per_chat_wa
    read_msgs_wa = db_wa * deliv_rate_wa * read_rate_wa
    clicks_wa = read_msgs_wa * ctr_wa
    donatur_wa = clicks_wa * cr_wa
    dana_wa = donatur_wa * avg_don_wa
    roas_wa = dana_wa / total_cost_wa if total_cost_wa > 0 else 0

    st.subheader("Proyeksi Hasil WA Blast")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Biaya Blast", f"Rp {total_cost_wa:,.0f}")
    m2.metric("Pesan Dibaca", f"{read_msgs_wa:,.0f}")
    m3.metric("Estimasi Donatur", f"{donatur_wa:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_wa:,.0f}")
    st.metric("Proyeksi ROAS WA Blast", f"{roas_wa:.2f} x")

# ---------------- TAB 4: EMAIL BLAST ----------------
with tab4:
    st.header("4. Email Marketing")
    col1, col2 = st.columns(2)
    with col1:
        db_email = st.number_input("Total Database Email", value=40000, step=5000, key="db_em")
        deliv_rate_em = st.number_input("Target Delivery Rate (%)", value=98.0, step=1.0, key="del_em") / 100
        open_rate_em = st.number_input("Target Open Rate (%)", value=22.0, step=1.0, key="open_em") / 100
        ctr_em = st.number_input("Target CTR (%)", value=4.0, step=0.5, key="ctr_em") / 100
    with col2:
        cr_em = st.number_input("Target Conversion Rate (%)", value=8.0, step=1.0, key="cr_em") / 100
        avg_don_em = st.number_input("Rata-rata Donasi (Rp)", value=450000, step=50000, key="avg_em")
        cost_em = st.number_input("Estimasi Biaya Campaign (Rp)", value=200000, step=50000, key="cost_em")

    open_emails_em = db_email * deliv_rate_em * open_rate_em
    clicks_em = open_emails_em * ctr_em
    donatur_em = clicks_em * cr_em
    dana_em = donatur_em * avg_don_em
    roas_em = dana_em / cost_em if cost_em > 0 else 0

    st.subheader("Proyeksi Hasil Email Marketing")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Email Dibuka", f"{open_emails_em:,.0f}")
    m2.metric("Estimasi Klik", f"{clicks_em:,.0f}")
    m3.metric("Estimasi Donatur", f"{donatur_em:,.1f}")
    m4.metric("Total Dana Terhimpun", f"Rp {dana_em:,.0f}")
    st.metric("Proyeksi ROAS Email", f"{roas_em:.2f} x")

# ---------------- TAB 5: SUMMARY & TOTAL ----------------
with tab5:
    st.header("5. Ringkasan Total Digital Fundraising")
    
    total_biaya = budget_ads + total_cost_wa + cost_em
    total_dana = dana_ads + dana_org + dana_wa + dana_em
    total_donatur = donatur_ads + donatur_org + donatur_wa + donatur_em
    overall_roas = total_dana / total_biaya if total_biaya > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Biaya Investasi", f"Rp {total_biaya:,.0f}")
    c2.metric("Total Proyeksi Donatur", f"{total_donatur:,.1f}")
    c3.metric("Total Dana Terhimpun", f"Rp {total_dana:,.0f}")
    c4.metric("Overall ROAS Combined", f"{overall_roas:.2f} x")

    df_summary = pd.DataFrame({
        "Kanal": ["Paid Ads", "Organic Content", "WA Blast", "Email Marketing"],
        "Biaya (Rp)": [budget_ads, 0, total_cost_wa, cost_em],
        "Dana Terhimpun (Rp)": [dana_ads, dana_org, dana_wa, dana_em],
        "Estimasi Donatur": [donatur_ads, donatur_org, donatur_wa, donatur_em]
    })

    st.subheader("Perbandingan Hasil per Kanal")
    st.dataframe(df_summary.style.format({
        "Biaya (Rp)": "Rp {:,.0f}",
        "Dana Terhimpun (Rp)": "Rp {:,.0f}",
        "Estimasi Donatur": "{:,.1f}"
    }), use_container_width=True)

    fig = px.bar(
        df_summary, 
        x="Kanal", 
        y="Dana Terhimpun (Rp)", 
        color="Kanal",
        title="Proyeksi Penghimpunan Dana ZIS per Kanal Digital"
    )
    st.plotly_chart(fig, use_container_width=True)
