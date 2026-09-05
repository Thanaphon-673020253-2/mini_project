import os
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="IndoHotel Executive Analytics",
    page_icon="🏨",
    layout="wide"
)


# =========================================================
# CUSTOM CSS & ADAPTIVE THEME STYLING
# =========================================================

st.markdown(
    """
    <style>
        /* Main container spacing */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
        }

        /* Adaptive Metric Card for Light & Dark Mode */
        div[data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.05);
            border: 1px solid rgba(128, 128, 128, 0.15);
            padding: 18px 22px;
            border-radius: 14px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: rgba(59, 130, 246, 0.4);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: rgba(128, 128, 128, 0.08);
            padding: 8px;
            border-radius: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
        }

        /* Divider */
        hr {
            margin-top: 2.5rem;
            margin-bottom: 2.5rem;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, rgba(128,128,128,0) 0%, rgba(128,128,128,0.3) 50%, rgba(128,128,128,0) 100%);
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_chart(fig):
    """
    ปรับรูปแบบกราฟให้โปร่งใส เพื่อให้กลมกลืนไปกับทั้ง Theme ขาวและดำอัตโนมัติ
    """
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", title=""),
        margin=dict(t=40, b=20, l=20, r=20),
        font=dict(family="Inter, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
    )
    return fig


def sql_escape(value):
    return str(value).replace("'", "''")


def safe_number(value, default=0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


# =========================================================
# DATABASE CONNECTION
# =========================================================

@st.cache_resource
def get_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, "indohotel", "dev.duckdb"),
        os.path.join(base_dir, "dev.duckdb")
    ]
    db_path = next((path for path in possible_paths if os.path.exists(path)), None)

    if db_path is None:
        st.error("❌ ไม่พบไฟล์ฐานข้อมูล dev.duckdb\n\nกรุณาตรวจสอบว่าไฟล์อยู่ที่: `indohotel/dev.duckdb`")
        st.stop()

    try:
        conn = duckdb.connect(db_path, read_only=True)
        conn.execute("SET search_path = 'main';")
        return conn
    except Exception as e:
        st.error(f"❌ ไม่สามารถเชื่อมต่อ DuckDB ได้\n\n{e}")
        st.stop()


conn = get_connection()


# =========================================================
# SIDEBAR FILTERS
# =========================================================

with st.sidebar:
    st.markdown("### 🎛️ ตัวกรองข้อมูล")
    st.markdown("---")

    years_df = conn.execute("SELECT DISTINCT year FROM main.dim_date WHERE year BETWEEN 2023 AND 2026 ORDER BY year DESC").df()
    year_options = ["ทั้งหมด"] + ([str(int(y)) for y in years_df["year"]] if not years_df.empty else [])
    selected_year = st.selectbox("📅 เลือกปี", year_options)

    properties_df = conn.execute("SELECT DISTINCT property_name FROM main.dim_property WHERE property_name IS NOT NULL ORDER BY property_name").df()
    property_options = ["ทั้งหมด"] + (properties_df["property_name"].dropna().astype(str).tolist() if not properties_df.empty else [])
    selected_property = st.selectbox("🏨 เลือกสาขา", property_options)

    seasons_df = conn.execute("SELECT DISTINCT season FROM main.dim_date WHERE season IS NOT NULL ORDER BY season").df()
    season_options = ["ทั้งหมด"] + (seasons_df["season"].dropna().astype(str).tolist() if not seasons_df.empty else [])
    selected_season = st.selectbox("🌤️ เลือกฤดูกาล", season_options)


# =========================================================
# GLOBAL SQL FILTER
# =========================================================

where_clauses = []
if selected_year != "ทั้งหมด":
    where_clauses.append(f"d.year = {int(selected_year)}")
else:
    where_clauses.append("d.year BETWEEN 2023 AND 2026")

if selected_property != "ทั้งหมด":
    where_clauses.append(f"p.property_name = '{sql_escape(selected_property)}'")

if selected_season != "ทั้งหมด":
    where_clauses.append(f"d.season = '{sql_escape(selected_season)}'")

where_stmt = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""


# =========================================================
# MAIN HEADER
# =========================================================

st.title("🏨 INDONESIAN HOTEL GROUP OPERATIONS")
st.caption("ระบบวิเคราะห์ข้อมูลเชิงยุทธศาสตร์ ครอบคลุมการดำเนินงานรอบด้านระดับองค์กร")
st.markdown("---")


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 รายได้และผลประกอบการ",
    "👥 ลูกค้าและพฤติกรรม",
    "🛏️ ห้องพักและการจอง",
    "📅 ปฏิบัติการและสถานที่"
])


# =========================================================
# TAB 1: REVENUE & PERFORMANCE
# =========================================================

with tab1:
    st.markdown("### 📊 ภาพรวมรายได้และผลประกอบการ")

    q1_df = conn.execute(
        f"""
        SELECT 
            COALESCE(SUM(b.total_revenue), 0) AS total_rev,
            COALESCE(SUM(b.nights), 0) AS total_nights
        FROM main.fact_hotel_bookings b
        JOIN main.dim_date d ON b.date_key = d.date_key
        JOIN main.dim_property p ON b.property_key = p.property_key
        {where_stmt}
        """
    ).df()

    total_rev = safe_number(q1_df.loc[0, "total_rev"]) if not q1_df.empty else 0
    total_nights = safe_number(q1_df.loc[0, "total_nights"]) if not q1_df.empty else 0

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.metric("ยอดขายรวม (Total Revenue)", f"Rp {total_rev:,.0f}")
    with c2:
        st.metric("จำนวนคืนที่จอง (Nights)", f"{total_nights:,.0f} คืน")

    st.markdown("---")

    col_i, col_j = st.columns(2, gap="large")

    with col_i:
        st.markdown("**📈 แนวโน้มรายได้ตามช่วงเดือน / ฤดูกาล**")
        q13_df = conn.execute(
            f"""
            SELECT 
                CAST(d.year AS VARCHAR) || ' ' || d.month_name AS year_month,
                MIN(d.date_key) AS sort_key,
                COALESCE(SUM(b.total_revenue), 0) / 1e9 AS revenue_b
            FROM main.fact_hotel_bookings b
            JOIN main.dim_date d ON b.date_key = d.date_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            {where_stmt}
            GROUP BY d.year, d.month_name ORDER BY sort_key
            """
        ).df()

        if not q13_df.empty:
            fig_q13 = px.line(q13_df, x="year_month", y="revenue_b", markers=True)
            fig_q13.update_traces(line_width=3, marker_size=7, line_color="#3b82f6")
            fig_q13.update_xaxes(type="category", tickangle=-45)
            st.plotly_chart(clean_chart(fig_q13), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลแนวโน้มรายได้")

    with col_j:
        st.markdown("**🍩 สัดส่วนยอดขาย วันธรรมดา vs วันหยุดสุดสัปดาห์**")
        q14_df = conn.execute(
            f"""
            SELECT 
                CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END AS day_type,
                COALESCE(SUM(b.total_revenue), 0) AS revenue
            FROM main.fact_hotel_bookings b
            JOIN main.dim_date d ON b.date_key = d.date_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            {where_stmt} GROUP BY 1
            """
        ).df()

        if not q14_df.empty:
            fig_q14 = px.pie(q14_df, values="revenue", names="day_type", hole=0.5, color_discrete_sequence=["#3b82f6", "#60a5fa"])
            fig_q14.update_traces(textinfo="percent+label")
            st.plotly_chart(clean_chart(fig_q14), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลสัดส่วนวันธรรมดา/วันหยุด")

    st.markdown("---")
    st.markdown("**🛎️ สัดส่วนรายได้และผู้ใช้บริการเสริมแยกตามประเภทบริการ**")

    q3_df = conn.execute(
        f"""
        SELECT 'Food & Beverage' AS service_type, COALESCE(SUM(f.sales_amount), 0) AS revenue, COUNT(DISTINCT f.guest_key) AS guest_count
        FROM main.fact_fnb_operations f JOIN main.dim_date d ON f.date_key = d.date_key JOIN main.dim_property p ON f.property_key = p.property_key {where_stmt}
        UNION ALL
        SELECT 'Spa & Wellness' AS service_type, COALESCE(SUM(a.spa_revenue), 0) AS revenue, COUNT(DISTINCT CASE WHEN a.spa_revenue > 0 THEN a.guest_key END) AS guest_count
        FROM main.fact_ancillary_services a JOIN main.dim_date d ON a.date_key = d.date_key JOIN main.dim_property p ON a.property_key = p.property_key {where_stmt}
        UNION ALL
        SELECT 'Event & Venue' AS service_type, COALESCE(SUM(a.event_revenue), 0) AS revenue, COUNT(CASE WHEN a.event_revenue > 0 THEN 1 END) AS guest_count
        FROM main.fact_ancillary_services a JOIN main.dim_date d ON a.date_key = d.date_key JOIN main.dim_property p ON a.property_key = p.property_key {where_stmt}
        ORDER BY revenue DESC
        """
    ).df()

    if not q3_df.empty:
        m1, m2, m3 = st.columns(3, gap="medium")
        metric_cols = [m1, m2, m3]
        for idx, row in q3_df.iterrows():
            if idx >= 3:
                break
            rev_b = safe_number(row["revenue"]) / 1e9
            g_count = int(safe_number(row["guest_count"]))
            unit_label = "รายการจัดงาน" if row["service_type"] == "Event & Venue" else "ผู้ใช้บริการ"
            metric_cols[idx].metric(f"บริการ {row['service_type']}", f"Rp {rev_b:,.2f}B", f"{g_count:,} {unit_label}")

        q3_df["revenue_b"] = pd.to_numeric(q3_df["revenue"], errors="coerce").fillna(0) / 1e9
        fig_q3 = px.bar(q3_df, x="service_type", y="revenue_b", text="revenue_b", color="service_type", color_discrete_sequence=["#2563eb", "#38bdf8", "#93c5fd"])
        fig_q3.update_traces(texttemplate="Rp %{y:.2f}B", textposition="outside")
        fig_q3.update_layout(showlegend=False)
        st.plotly_chart(clean_chart(fig_q3), use_container_width=True)
    else:
        st.info("ไม่พบข้อมูลบริการเสริม")

    st.markdown("---")
    st.markdown("**🏨 อัตราการเข้าพักเฉลี่ย (Occupancy Rate) แยกตามสาขา**")

    q2_df = conn.execute(
        f"""
        SELECT p.property_name, AVG(f.occupancy_rate) * 100 AS avg_occ
        FROM main.fact_daily_occupancy f
        JOIN main.dim_property p ON f.property_key = p.property_key
        JOIN main.dim_date d ON f.date_key = d.date_key
        {where_stmt} GROUP BY p.property_name ORDER BY avg_occ DESC
        """
    ).df()

    if not q2_df.empty:
        q2_df["avg_occ"] = pd.to_numeric(q2_df["avg_occ"], errors="coerce").fillna(0)
        fig_q2 = px.bar(q2_df, x="property_name", y="avg_occ", text="avg_occ", color="avg_occ", color_continuous_scale="Blues", range_y=[0, 100])
        fig_q2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_q2.update_layout(coloraxis_showscale=False)
        st.plotly_chart(clean_chart(fig_q2), use_container_width=True)
    else:
        st.info("ไม่พบข้อมูล Occupancy Rate")


# =========================================================
# TAB 2: CUSTOMER ANALYSIS
# =========================================================

with tab2:
    st.markdown("### 👥 การวิเคราะห์ลูกค้าและพฤติกรรม")

    col_c, col_d = st.columns(2, gap="large")

    with col_c:
        st.markdown("**🥇 ค่าเฉลี่ยการเข้าพักซ้ำตามระดับ Loyalty Tier**")
        q5_df = conn.execute(
            f"""
            SELECT 
                CASE WHEN g.loyalty_tier IS NULL OR LOWER(TRIM(g.loyalty_tier)) = 'none' THEN 'Non-Member' ELSE g.loyalty_tier END AS loyalty_tier,
                COUNT(b.booking_id) * 1.0 / NULLIF(COUNT(DISTINCT g.guest_key), 0) AS repeat_rate
            FROM main.fact_hotel_bookings b
            LEFT JOIN main.dim_guest g ON b.guest_key = g.guest_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt} GROUP BY 1 ORDER BY repeat_rate DESC
            """
        ).df()

        if not q5_df.empty:
            fig_q5 = px.bar(q5_df, x="loyalty_tier", y="repeat_rate", text="repeat_rate", color="repeat_rate", color_continuous_scale="Purples")
            fig_q5.update_traces(texttemplate="%{text:.2f} ครั้ง", textposition="outside")
            fig_q5.update_layout(coloraxis_showscale=False)
            st.plotly_chart(clean_chart(fig_q5), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูล Loyalty Tier")

    with col_d:
        st.markdown("**🌍 สัญชาติลูกค้าที่มียอดจองสูงสุด Top 5**")
        q6_df = conn.execute(
            f"""
            SELECT g.nationality, COUNT(b.booking_id) AS bookings
            FROM main.fact_hotel_bookings b
            JOIN main.dim_guest g ON b.guest_key = g.guest_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
            AND g.nationality IS NOT NULL AND TRIM(g.nationality) <> '' AND LOWER(TRIM(g.nationality)) <> 'others'
            GROUP BY g.nationality ORDER BY bookings DESC LIMIT 5
            """
        ).df()

        if not q6_df.empty:
            fig_q6 = px.bar(q6_df, x="bookings", y="nationality", orientation="h", text="bookings", color="bookings", color_continuous_scale="Tealgrn")
            fig_q6.update_traces(texttemplate="%{text:,.0f} รายการ", textposition="outside")
            fig_q6.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
            st.plotly_chart(clean_chart(fig_q6), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลสัญชาติลูกค้า")

    st.markdown("---")
    col_e, col_f = st.columns(2, gap="large")

    with col_e:
        st.markdown("**🥗 เปรียบเทียบการใช้บริการ Food และ Spa (ในประเทศ vs ต่างชาติ)**")
        q8_df = conn.execute(
            f"""
            SELECT 'Food' AS service_type, CASE WHEN g.is_domestic = TRUE THEN 'ในประเทศ (Domestic)' ELSE 'ต่างชาติ (International)' END AS guest_type, COUNT(*) AS service_count
            FROM main.fact_fnb_operations f JOIN main.dim_guest g ON f.guest_key = g.guest_key JOIN main.dim_date d ON f.date_key = d.date_key JOIN main.dim_property p ON f.property_key = p.property_key {where_stmt} AND f.sales_amount > 0 GROUP BY 1, 2
            UNION ALL
            SELECT 'Spa' AS service_type, CASE WHEN g.is_domestic = TRUE THEN 'ในประเทศ (Domestic)' ELSE 'ต่างชาติ (International)' END AS guest_type, COUNT(*) AS service_count
            FROM main.fact_ancillary_services a JOIN main.dim_guest g ON a.guest_key = g.guest_key JOIN main.dim_date d ON a.date_key = d.date_key JOIN main.dim_property p ON a.property_key = p.property_key {where_stmt} AND a.spa_revenue > 0 GROUP BY 1, 2
            """
        ).df()

        if not q8_df.empty:
            fig_q8 = px.bar(q8_df, x="service_type", y="service_count", color="guest_type", barmode="group", text="service_count", color_discrete_sequence=["#38bdf8", "#fb7185"])
            fig_q8.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            st.plotly_chart(clean_chart(fig_q8), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลการใช้บริการ Spa และ Food")

    with col_f:
        st.markdown("**🛌 ระยะเวลาเข้าพักเฉลี่ย (Nights Stayed) ตามสาขาโรงแรม**")
        q11_df = conn.execute(
            f"""
            SELECT p.property_name, AVG(b.nights) AS avg_nights
            FROM main.fact_hotel_bookings b
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt} GROUP BY p.property_name ORDER BY avg_nights DESC
            """
        ).df()

        if not q11_df.empty:
            fig_q11 = px.bar(q11_df, x="property_name", y="avg_nights", text="avg_nights", color="avg_nights", color_continuous_scale="Oranges")
            fig_q11.update_traces(texttemplate="%{text:.1f} คืน", textposition="outside")
            fig_q11.update_layout(coloraxis_showscale=False)
            st.plotly_chart(clean_chart(fig_q11), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลระยะเวลาเข้าพักเฉลี่ย")


# =========================================================
# TAB 3: ROOM & BOOKING PATTERNS
# =========================================================

with tab3:
    st.markdown("### 🛏️ ประเภทห้องพักและพฤติกรรมการจอง")

    q10_df = conn.execute(
        f"""
        SELECT AVG(b.lead_time_days) AS avg_lead
        FROM main.fact_hotel_bookings b
        JOIN main.dim_property p ON b.property_key = p.property_key
        JOIN main.dim_date d ON b.date_key = d.date_key
        {where_stmt}
        """
    ).df()
    lead_val = safe_number(q10_df.loc[0, "avg_lead"]) if not q10_df.empty else 0
    st.metric("ระยะเวลาการจองล่วงหน้าเฉลี่ย (Lead Time)", f"{lead_val:,.1f} วัน")

    st.markdown("---")
    col_g, col_h = st.columns(2, gap="large")

    with col_g:
        st.markdown("**💰 ประเภทห้องพักที่สร้างรายได้หลักสูงสุด**")
        q9_df = conn.execute(
            f"""
            SELECT COALESCE(r.room_type, b.room_type, 'Unknown') AS room_type, COUNT(b.booking_id) AS bookings, COALESCE(SUM(b.total_revenue), 0) / 1e9 AS revenue_b
            FROM main.fact_hotel_bookings b
            LEFT JOIN main.dim_room r ON b.room_key = r.room_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt} GROUP BY 1 ORDER BY revenue_b DESC
            """
        ).df()

        if not q9_df.empty and q9_df["revenue_b"].notna().any():
            fig_q9 = px.bar(q9_df, x="room_type", y="revenue_b", text="bookings", color="revenue_b", color_continuous_scale="Greens")
            fig_q9.update_traces(texttemplate="Rp %{y:.2f}B (%{text:,} จอง)", textposition="outside")
            fig_q9.update_layout(coloraxis_showscale=False)
            st.plotly_chart(clean_chart(fig_q9), use_container_width=True)
        else:
            st.warning("⚠️ ไม่พบข้อมูลประเภทห้องพักตามเงื่อนไขที่เลือก")

    with col_h:
        st.markdown("**❌ อัตราการยกเลิกการจอง (%) แยกตามประเภทห้องพัก**")
        q12_df = conn.execute(
            f"""
            SELECT COALESCE(r.room_type, b.room_type, 'Unknown') AS room_type, AVG(CAST(b.is_canceled AS INTEGER)) * 100 AS cancel_rate
            FROM main.fact_hotel_bookings b
            LEFT JOIN main.dim_room r ON b.room_key = r.room_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt} GROUP BY 1 ORDER BY cancel_rate DESC
            """
        ).df()

        if not q12_df.empty and q12_df["cancel_rate"].notna().any():
            fig_q12 = px.bar(q12_df, x="room_type", y="cancel_rate", text="cancel_rate", color="cancel_rate", color_continuous_scale="Reds")
            fig_q12.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_q12.update_layout(coloraxis_showscale=False)
            st.plotly_chart(clean_chart(fig_q12), use_container_width=True)
        else:
            st.warning("⚠️ ไม่พบข้อมูลอัตราการยกเลิกตามเงื่อนไขที่เลือก")


# =========================================================
# TAB 4: OPERATIONS & VENUE
# =========================================================

with tab4:
    st.markdown("### 📅 ปฏิบัติการและสถานที่จัดงานประชุม")
    st.markdown("**🏢 ประเภทสถานที่จัดงาน (Venue Type) ที่มีการจองสูงสุด**")

    q15_df = conn.execute(
        f"""
        SELECT COALESCE(v.venue_type) AS venue_type, COUNT(CASE WHEN a.event_revenue > 0 THEN 1 END) AS booking_count, COALESCE(SUM(a.event_revenue), 0) / 1e9 AS rev_billions
        FROM main.fact_ancillary_services a
        LEFT JOIN main.dim_venue v ON a.venue_key = v.venue_key
        JOIN main.dim_property p ON a.property_key = p.property_key
        JOIN main.dim_date d ON a.date_key = d.date_key
        {where_stmt} GROUP BY 1 ORDER BY booking_count DESC
        """
    ).df()

    if not q15_df.empty and q15_df["booking_count"].notna().any():
        fig_q15 = px.bar(q15_df, x="venue_type", y="booking_count", text="booking_count", color="booking_count", color_continuous_scale="Viridis")
        fig_q15.update_traces(texttemplate="%{text:,} ครั้ง", textposition="outside")
        fig_q15.update_layout(coloraxis_showscale=False)
        st.plotly_chart(clean_chart(fig_q15), use_container_width=True)
    else:
        st.info("ไม่พบข้อมูล Venue Performance")

    st.markdown("---")
    st.markdown("**📋 รายละเอียดประเภทกิจกรรมจัดงาน (Event Type Breakdown)**")

    q_event_type = conn.execute(
        f"""
        SELECT COALESCE(e.event_type_name, 'Unknown') AS event_type, COUNT(*) AS total_bookings, COALESCE(SUM(a.event_revenue), 0) / 1e9 AS rev_billions
        FROM main.fact_ancillary_services a
        LEFT JOIN main.dim_event_type e ON a.event_type_key = e.event_type_key
        JOIN main.dim_date d ON a.date_key = d.date_key
        JOIN main.dim_property p ON a.property_key = p.property_key
        {where_stmt} AND a.event_revenue > 0 GROUP BY 1 ORDER BY total_bookings DESC
        """
    ).df()

    if not q_event_type.empty:
        col_m, col_n = st.columns(2, gap="large")

        with col_m:
            fig_evt_count = px.bar(q_event_type, x="event_type", y="total_bookings", text="total_bookings", color="total_bookings", color_continuous_scale="Blues")
            fig_evt_count.update_traces(texttemplate="%{text:,} ครั้ง", textposition="outside")
            fig_evt_count.update_layout(coloraxis_showscale=False, title="จำนวนครั้งที่จัดแยกตามประเภท Event")
            st.plotly_chart(clean_chart(fig_evt_count), use_container_width=True)

        with col_n:
            fig_evt_rev = px.bar(q_event_type, x="event_type", y="rev_billions", text="rev_billions", color="rev_billions", color_continuous_scale="YlGnBu")
            fig_evt_rev.update_traces(texttemplate="Rp %{y:.2f}B", textposition="outside")
            fig_evt_rev.update_layout(coloraxis_showscale=False, title="รายได้รวมแยกตามประเภท Event")
            st.plotly_chart(clean_chart(fig_evt_rev), use_container_width=True)
    else:
        st.info("ไม่พบข้อมูลประเภทกิจกรรมจัดงานตามเงื่อนไขที่เลือก")


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.caption("IndoHotel Executive Analytics | Powered by Streamlit + DuckDB + dbt")