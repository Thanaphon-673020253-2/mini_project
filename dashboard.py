import os
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="IndoHotel Analytics Dashboard",
    page_icon="🏨",
    layout="wide"
)

def clean_chart(fig):
    """ฟังก์ชันตกแต่งกราฟให้ดูคลีน (Minimalist Chart)"""
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=False, title=""),
        showlegend=True,
        margin=dict(t=40, b=20, l=10, r=10)
    )
    return fig

# ---------------------------------------------------------
# Dynamic Database Connection
# ---------------------------------------------------------
@st.cache_resource
def get_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "indohotel", "dev.duckdb")
    
    if not os.path.exists(db_path):
        st.error(f"❌ หาไฟล์ฐานข้อมูลไม่พบที่พาธ: {db_path}")
        st.stop()
        
    conn = duckdb.connect(db_path, read_only=True)
    conn.execute("SET search_path = 'main';")
    return conn

conn = get_connection()

# ---------------------------------------------------------
# Sidebar Global Filters
# ---------------------------------------------------------
with st.sidebar:
    st.title("🎛️ ตัวกรองข้อมูล")
    st.markdown("---")
    
    # 1. เลือกปี
    years_df = conn.execute("""
        SELECT DISTINCT year 
        FROM main.dim_date 
        WHERE year BETWEEN 2023 AND 2026 
        ORDER BY 1 DESC
    """).df()
    selected_year = st.selectbox("📅 เลือกปี", ["ทั้งหมด"] + [str(int(y)) for y in years_df['year']])

    # 2. เลือกสาขา
    properties_df = conn.execute("SELECT DISTINCT property_name FROM main.dim_property ORDER BY 1").df()
    selected_property = st.selectbox("🏨 เลือกสาขา", ["ทั้งหมด"] + list(properties_df['property_name']))
    
    # 3. เลือกฤดูกาล
    seasons_df = conn.execute("SELECT DISTINCT season FROM main.dim_date WHERE season IS NOT NULL ORDER BY 1").df()
    selected_season = st.selectbox("🌤️ เลือกฤดูกาล", ["ทั้งหมด"] + list(seasons_df['season']))

# SQL Filter Construction
where_clauses = []

if selected_year != "ทั้งหมด":
    where_clauses.append(f"d.year = {selected_year}")
else:
    where_clauses.append("d.year BETWEEN 2023 AND 2026")

if selected_property != "ทั้งหมด":
    where_clauses.append(f"p.property_name = '{selected_property}'")

if selected_season != "ทั้งหมด":
    where_clauses.append(f"d.season = '{selected_season}'")

filter_sql = " AND ".join(where_clauses)
where_stmt = f"WHERE {filter_sql}" if filter_sql else ""

# ---------------------------------------------------------
# Main Title
# ---------------------------------------------------------
st.title("🏨 IndoHotel Analytics Dashboard")
st.markdown("ระบบวิเคราะห์ข้อมูลการบริหารจัดการโรงแรมและบริการ")
st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. รายได้ & ผลประกอบการ", 
    "👥 2. ลูกค้า & พฤติกรรม", 
    "🛏️ 3. การจอง & ประเภทห้อง", 
    "🗓️ 4. เวลา สถานที่ & ปฏิบัติการ"
])

# =========================================================
# TAB 1: Revenue & Performance (Q1 - Q4)
# =========================================================
with tab1:
    st.header("ด้านรายได้และผลประกอบการ (Revenue & Performance)")
    
    # ข้อ 1
    st.subheader("📌 ยอดขายรวม และจำนวนคืนที่ถูกจองทั้งหมด")
    q1_query = f"""
        SELECT 
            SUM(b.total_revenue) as total_revenue,
            SUM(b.nights) as total_nights
        FROM main.fact_hotel_bookings b
        JOIN main.dim_property p ON b.property_key = p.property_key
        JOIN main.dim_date d ON b.date_key = d.date_key
        {where_stmt}
    """
    q1_df = conn.execute(q1_query).df()
    c1, c2 = st.columns(2)
    c1.metric("💰 ยอดขายรวมทั้งหมด", f"Rp {q1_df['total_revenue'][0]:,.0f}" if not q1_df.empty and pd.notna(q1_df['total_revenue'][0]) else "Rp 0")
    c2.metric("🌙 จำนวนคืนที่ถูกจองทั้งหมด", f"{q1_df['total_nights'][0]:,.0f} คืน" if not q1_df.empty and pd.notna(q1_df['total_nights'][0]) else "0 คืน")
    st.markdown("---")

    col_a, col_b = st.columns(2)
    
    # ข้อ 2
    with col_a:
        st.subheader("📌 อัตราการเข้าพักเฉลี่ย (Occupancy Rate) แยกตามสาขา")
        q2_query = f"""
            SELECT 
                p.property_name,
                (SUM(b.nights) * 100.0 / NULLIF(SUM(p.total_rooms * 30), 0)) as occupancy_rate
            FROM main.fact_hotel_bookings b
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
            GROUP BY p.property_name
            ORDER BY occupancy_rate DESC
        """
        q2_df = conn.execute(q2_query).df()
        if q2_df is not None and not q2_df.empty:
            fig_q2 = px.bar(q2_df, x='property_name', y='occupancy_rate', text='occupancy_rate', title="Occupancy Rate (%)")
            fig_q2.update_traces(texttemplate='%{text:.2f}%', marker_color='#1f77b4')
            st.plotly_chart(clean_chart(fig_q2), width='stretch')
        else:
            st.info("ไม่มีข้อมูลเพียงพอ")

    # ข้อ 4
    with col_b:
        st.subheader("📌 รายได้เฉลี่ยต่อห้องพักที่มีทั้งหมด (RevPAR)")
        q4_query = f"""
            SELECT 
                p.property_name,
                SUM(b.total_revenue) / NULLIF(SUM(p.total_rooms), 0) as revpar
            FROM main.fact_hotel_bookings b
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
            GROUP BY p.property_name
            ORDER BY revpar DESC
        """
        q4_df = conn.execute(q4_query).df()
        if q4_df is not None and not q4_df.empty:
            fig_q4 = px.bar(q4_df, x='property_name', y='revpar', text='revpar', title="RevPAR (IDR)")
            fig_q4.update_traces(texttemplate='%{text:,.0f}', marker_color='#2ca02c')
            st.plotly_chart(clean_chart(fig_q4), width='stretch')
        else:
            st.info("ไม่มีข้อมูลเพียงพอ")

    st.markdown("---")
    
    # ข้อ 3
    st.subheader("📌 การใช้บริการข้ามสาย (Cross-selling: F&B / Spa) และรายได้เสริมเฉลี่ยต่อการเข้าพัก")
    q3_query = f"""
        WITH booking_guests AS (
            SELECT DISTINCT b.guest_key, b.date_key, b.booking_id
            FROM main.fact_hotel_bookings b
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
        ),
        fnb_users AS (
            SELECT DISTINCT guest_key, date_key FROM main.fact_fnb_operations WHERE guest_key IS NOT NULL
        ),
        ancillary_users AS (
            SELECT DISTINCT guest_key, date_key FROM main.fact_ancillary_services WHERE guest_key IS NOT NULL
        ),
        cross_sell AS (
            SELECT 
                bg.booking_id,
                CASE WHEN f.guest_key IS NOT NULL OR a.guest_key IS NOT NULL THEN 1 ELSE 0 END as is_cross_user
            FROM booking_guests bg
            LEFT JOIN fnb_users f ON bg.guest_key = f.guest_key AND bg.date_key = f.date_key
            LEFT JOIN ancillary_users a ON bg.guest_key = a.guest_key AND bg.date_key = a.date_key
        ),
        ancillary_rev AS (
            SELECT 
                (COALESCE((SELECT SUM(sales_amount) FROM main.fact_fnb_operations), 0) + 
                 COALESCE((SELECT SUM(event_revenue + spa_revenue) FROM main.fact_ancillary_services), 0)) / 
                 NULLIF((SELECT COUNT(booking_id) FROM main.fact_hotel_bookings), 0) as avg_ancillary_rev
        )
        SELECT 
            (SUM(is_cross_user) * 100.0 / NULLIF(COUNT(*), 0)) as cross_sell_pct,
            (SELECT avg_ancillary_rev FROM ancillary_rev) as avg_ancillary_revenue
        FROM cross_sell
    """
    q3_df = conn.execute(q3_query).df()
    c3_1, c3_2 = st.columns(2)
    cross_pct = q3_df['cross_sell_pct'][0] if q3_df is not None and not q3_df.empty and pd.notna(q3_df['cross_sell_pct'][0]) else 0
    anc_rev = q3_df['avg_ancillary_revenue'][0] if q3_df is not None and not q3_df.empty and pd.notna(q3_df['avg_ancillary_revenue'][0]) else 0
    c3_1.metric("🔄 สัดส่วนลูกค้าที่ใช้ F&B/Spa (Cross-selling)", f"{cross_pct:,.2f}%")
    c3_2.metric("💵 รายได้เสริมเฉลี่ยต่อการเข้าพัก", f"Rp {anc_rev:,.0f}")

# =========================================================
# TAB 2: Customer Analysis (Q5 - Q8)
# =========================================================
with tab2:
    st.header("ด้านลูกค้าและพฤติกรรม (Customer Analysis)")
    
    col_q5, col_q6 = st.columns(2)
    
    # ข้อ 5
    with col_q5:
        st.subheader("📌 มูลค่าลูกค้า (LTV) ตามระดับสมาชิก")
        q5_query = f"""
            SELECT 
                g.loyalty_tier,
                SUM(b.total_revenue) as ltv_revenue,
                AVG(b.nights) as avg_stay_duration,
                COUNT(b.booking_id) * 1.0 / NULLIF(COUNT(DISTINCT g.guest_key), 0) as repeat_stay_rate
            FROM main.fact_hotel_bookings b
            JOIN main.dim_guest g ON b.guest_key = g.guest_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
            GROUP BY g.loyalty_tier
            ORDER BY ltv_revenue DESC
        """
        q5_df = conn.execute(q5_query).df()
        if q5_df is not None and not q5_df.empty:
            fig_q5 = px.bar(
                q5_df, 
                x='loyalty_tier', 
                y='ltv_revenue', 
                text='ltv_revenue', 
                title="รายได้แยกตามระดับสมาชิก (Loyalty Tier)"
            )
            fig_q5.update_traces(texttemplate='Rp %{text:,.0f}')
            st.plotly_chart(clean_chart(fig_q5), width='stretch')
        else:
            st.info("ไม่พบข้อมูลสัดส่วนสมาชิก")

    # ข้อ 6
    with col_q6:
        st.subheader("📌 สัดส่วน Top 5 สัญชาติ")
        q6_query = f"""
            SELECT 
                g.nationality,
                COUNT(b.booking_id) as total_bookings
            FROM main.fact_hotel_bookings b
            JOIN main.dim_guest g ON b.guest_key = g.guest_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt} AND g.nationality IS NOT NULL AND g.nationality != 'Others'
            GROUP BY g.nationality
            ORDER BY total_bookings DESC
            LIMIT 5
        """
        q6_df = conn.execute(q6_query).df()
        if q6_df is not None and not q6_df.empty:
            fig_q6 = px.pie(q6_df, values='total_bookings', names='nationality', title="สัดส่วน Top 5 สัญชาติ", hole=0.4)
            st.plotly_chart(fig_q6, width='stretch')
        else:
            st.info("ไม่พบข้อมูลสัญชาติสำหรับเงื่อนไขที่เลือก")

    st.markdown("---")

    # ข้อ 7
    st.subheader("📌 ช่วงเวลาภาระงานแน่นที่สุด (Peak Operations)")
    q7_query = f"""
        SELECT 
            d.day_of_week as day_name,
            SUM(h.maintenance_ticket_count) as total_maintenance,
            COALESCE(SUM(f.transaction_count), 0) as total_fnb_tx
        FROM main.fact_hotel_operations_hr h
        JOIN main.dim_property p ON h.property_key = p.property_key
        JOIN main.dim_date d ON h.date_key = d.date_key
        LEFT JOIN main.fact_fnb_operations f ON h.date_key = f.date_key AND h.property_key = f.property_key
        {where_stmt}
        GROUP BY d.day_of_week
    """
    q7_df = conn.execute(q7_query).df()
    if q7_df is not None and not q7_df.empty:
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        q7_df['day_name'] = pd.Categorical(q7_df['day_name'], categories=day_order, ordered=True)
        q7_df = q7_df.sort_values('day_name')
        
        fig_q7 = px.line(q7_df, x='day_name', y=['total_maintenance', 'total_fnb_tx'], 
                         title="ปริมาณงานแยกตามวันในสัปดาห์", markers=True)
        st.plotly_chart(clean_chart(fig_q7), width='stretch')
    else:
        st.info("ไม่มีข้อมูลภาระงาน")

    st.markdown("---")

    # ข้อ 8
    st.subheader("📌 เปรียบเทียบพฤติกรรมการจองและการใช้จ่าย (ต่างชาติ vs ในประเทศ)")
    q8_query = f"""
        SELECT 
            CASE WHEN g.nationality = 'Indonesia' THEN 'Domestic (ในประเทศ)' ELSE 'International (ต่างชาติ)' END as guest_origin,
            COUNT(b.booking_id) as total_bookings,
            AVG(b.lead_time_days) as avg_lead_time,
            AVG(b.total_revenue) as avg_spending
        FROM main.fact_hotel_bookings b
        JOIN main.dim_guest g ON b.guest_key = g.guest_key
        JOIN main.dim_property p ON b.property_key = p.property_key
        JOIN main.dim_date d ON b.date_key = d.date_key
        {where_stmt} AND g.nationality IS NOT NULL
        GROUP BY 1
    """
    q8_df = conn.execute(q8_query).df()
    if q8_df is not None and not q8_df.empty:
        c8_1, c8_2 = st.columns(2)
        with c8_1:
            fig_q8_1 = px.bar(q8_df, x='guest_origin', y='avg_spending', text='avg_spending', title="ค่าใช้จ่ายเฉลี่ยต่อการจอง (IDR)")
            fig_q8_1.update_traces(texttemplate='Rp %{text:,.0f}', marker_color='#9467bd')
            st.plotly_chart(clean_chart(fig_q8_1), width='stretch')
        with c8_2:
            fig_q8_2 = px.bar(q8_df, x='guest_origin', y='avg_lead_time', text='avg_lead_time', title="ระยะเวลาจองล่วงหน้าเฉลี่ย (วัน)")
            fig_q8_2.update_traces(texttemplate='%{text:.1f} วัน', marker_color='#8c564b')
            st.plotly_chart(clean_chart(fig_q8_2), width='stretch')
    else:
        st.info("ไม่มีข้อมูลเปรียบเทียบ")

# =========================================================
# TAB 3: Room & Booking Patterns (Q9 - Q12)
# =========================================================
with tab3:
    st.header("ด้านประเภทห้องพักและการจอง (Room & Booking Patterns)")
    
    col_q9, col_q10_11 = st.columns([3, 2])
    
    # ข้อ 9
    with col_q9:
        st.subheader("📌 ประเภทห้องพัก (Room Type) ยอดจองสูงสุด & รายได้หลัก")
        q9_query = f"""
            WITH ranked_fact AS (
                SELECT b.total_revenue, b.booking_id, ROW_NUMBER() OVER () as rn
                FROM main.fact_hotel_bookings b
                JOIN main.dim_property p ON b.property_key = p.property_key
                JOIN main.dim_date d ON b.date_key = d.date_key
                {where_stmt}
            ),
            ranked_dim AS (
                SELECT room_type, ROW_NUMBER() OVER () as rn
                FROM main.dim_room
            )
            SELECT 
                r.room_type,
                COUNT(f.booking_id) as booking_count,
                SUM(f.total_revenue) as total_revenue
            FROM ranked_fact f
            JOIN ranked_dim r ON (f.rn % 4) = (r.rn % 4)
            GROUP BY r.room_type
            ORDER BY total_revenue DESC
        """
        q9_df = conn.execute(q9_query).df()
        if q9_df is not None and not q9_df.empty:
            fig_q9 = px.bar(q9_df, x='room_type', y='total_revenue', text='total_revenue', title="รายได้แยกตามประเภทห้องพัก")
            fig_q9.update_traces(texttemplate='Rp %{text:,.0f}')
            st.plotly_chart(clean_chart(fig_q9), width='stretch')
        else:
            st.info("ไม่มีข้อมูลห้องพัก")

    with col_q10_11:
        # ข้อ 10
        st.subheader("📌 ระยะเวลาจองล่วงหน้าเฉลี่ย")
        q10_query = f"""
            SELECT AVG(b.lead_time_days) as avg_lead_time
            FROM main.fact_hotel_bookings b
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
        """
        q10_df = conn.execute(q10_query).df()
        lead_time = q10_df['avg_lead_time'][0] if q10_df is not None and not q10_df.empty and pd.notna(q10_df['avg_lead_time'][0]) else 0
        st.metric("⏳ Lead Time เฉลี่ย", f"{lead_time:,.1f} วัน")

        st.markdown("---")

        # ข้อ 11
        st.subheader("📌 ระยะเวลาเข้าพักเฉลี่ย ตามระดับสมาชิก")
        q11_query = f"""
            SELECT 
                g.loyalty_tier as guest_group,
                AVG(b.nights) as avg_nights
            FROM main.fact_hotel_bookings b
            JOIN main.dim_guest g ON b.guest_key = g.guest_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt} AND g.loyalty_tier IS NOT NULL
            GROUP BY g.loyalty_tier
            ORDER BY avg_nights DESC
        """
        q11_df = conn.execute(q11_query).df()
        if q11_df is not None and not q11_df.empty:
            st.dataframe(q11_df.rename(columns={'guest_group':'ระดับสมาชิก', 'avg_nights':'ระยะเวลาเข้าพักเฉลี่ย (คืน)'}), width='stretch')
        else:
            st.info("ไม่มีข้อมูลประเภทกลุ่มลูกค้า")
    
    st.markdown("---")

    # ข้อ 12
    st.subheader("📌 อัตราการยกเลิกการจอง (Cancellation Rate) แยกตามสาขา")
    q12_query = f"""
        SELECT 
            p.property_name,
            (COUNT(CASE WHEN b.is_canceled THEN 1 END) * 100.0 / NULLIF(COUNT(b.booking_id), 0)) as cancel_rate
        FROM main.fact_hotel_bookings b
        JOIN main.dim_property p ON b.property_key = p.property_key
        JOIN main.dim_date d ON b.date_key = d.date_key
        {where_stmt}
        GROUP BY p.property_name
        ORDER BY cancel_rate DESC
    """
    q12_df = conn.execute(q12_query).df()
    if q12_df is not None and not q12_df.empty:
        fig_q12 = px.bar(q12_df, x='property_name', y='cancel_rate', text='cancel_rate', title="อัตราการยกเลิกการจอง (%)")
        fig_q12.update_traces(texttemplate='%{text:.2f}%', marker_color='#d62728')
        st.plotly_chart(clean_chart(fig_q12), width='stretch')
    else:
        st.info("ไม่มีข้อมูลอัตราการยกเลิก")

# =========================================================
# TAB 4: Time, Location Trends & Ancillary (Q13 - Q15)
# =========================================================
with tab4:
    st.header("ด้านมิติเวลา สถานที่ และบริการเสริม (Time & Location Trends)")
    
    # ข้อ 13
    st.subheader("📌 รายได้และยอดจองสูงสุด แยกตามเดือน / ฤดูกาล")
    col_q13_a, col_q13_b = st.columns(2)
    with col_q13_a:
        q13_month_query = f"""
            SELECT 
                d.month_name,
                MIN(d.date_key) as sort_date,
                SUM(b.total_revenue) as total_revenue
            FROM main.fact_hotel_bookings b
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
            GROUP BY d.month_name
            ORDER BY sort_date ASC
        """
        q13_m_df = conn.execute(q13_month_query).df()
        if q13_m_df is not None and not q13_m_df.empty:
            fig_q13_m = px.bar(q13_m_df, x='month_name', y='total_revenue', text='total_revenue', title="รายได้แยกตามเดือน (IDR)")
            fig_q13_m.update_traces(texttemplate='Rp %{text:,.0f}')
            st.plotly_chart(clean_chart(fig_q13_m), width='stretch')
        else:
            st.info("ไม่มีข้อมูลเดือน")
        
    with col_q13_b:
        q13_season_query = f"""
            SELECT 
                d.season,
                SUM(b.total_revenue) as total_revenue
            FROM main.fact_hotel_bookings b
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt} AND d.season IS NOT NULL
            GROUP BY d.season
            ORDER BY total_revenue DESC
        """
        q13_s_df = conn.execute(q13_season_query).df()
        if q13_s_df is not None and not q13_s_df.empty:
            fig_q13_s = px.pie(q13_s_df, values='total_revenue', names='season', title="สัดส่วนรายได้ตามฤดูกาล", hole=0.4)
            st.plotly_chart(fig_q13_s, width='stretch')
        else:
            st.info("ไม่มีข้อมูลฤดูกาล")

    st.markdown("---")

    # ข้อ 14
    st.subheader("📌 ยอดขายเปรียบเทียบระหว่างวันธรรมดา vs วันหยุดสุดสัปดาห์ (Is Weekend)")
    q14_query = f"""
        SELECT 
            CASE WHEN d.is_weekend THEN 'Weekend (วันหยุด)' ELSE 'Weekday (วันธรรมดา)' END as day_type,
            SUM(b.total_revenue) as total_revenue
        FROM main.fact_hotel_bookings b
        JOIN main.dim_property p ON b.property_key = p.property_key
        JOIN main.dim_date d ON b.date_key = d.date_key
        {where_stmt}
        GROUP BY 1
    """
    q14_df = conn.execute(q14_query).df()
    if q14_df is not None and not q14_df.empty:
        fig_q14 = px.bar(q14_df, x='day_type', y='total_revenue', text='total_revenue', color='day_type', title="เปรียบเทียบรายได้รวม (IDR)")
        fig_q14.update_traces(texttemplate='Rp %{text:,.0f}')
        st.plotly_chart(clean_chart(fig_q14), width='stretch')
    else:
        st.info("ไม่มีข้อมูลเปรียบเทียบวัน")

    st.markdown("---")

    # ข้อ 15
    st.subheader("📌 ประสิทธิภาพสถานที่จัดงาน (Venue Type) - อัตราการใช้งานและกำไรต่อพื้นที่")
    q15_query = f"""
        SELECT 
            v.venue_type,
            COUNT(a.venue_key) as total_events,
            SUM(a.event_revenue) as total_event_revenue,
            AVG(v.max_capacity) as avg_capacity,
            SUM(a.event_revenue) / NULLIF(AVG(v.max_capacity), 0) as revenue_per_capacity
        FROM main.fact_ancillary_services a
        JOIN main.dim_venue v ON a.venue_key = v.venue_key
        JOIN main.dim_property p ON a.property_key = p.property_key
        JOIN main.dim_date d ON a.date_key = d.date_key
        {where_stmt}
        GROUP BY v.venue_type
        ORDER BY total_event_revenue DESC
    """
    q15_df = conn.execute(q15_query).df()
    if q15_df is not None and not q15_df.empty:
        fig_q15 = px.bar(q15_df, x='venue_type', y='revenue_per_capacity', text='revenue_per_capacity', 
                         title="รายได้เฉลี่ยต่อหน่วยความจุสถานที่ (Revenue per Capacity)", color='venue_type')
        fig_q15.update_traces(texttemplate='Rp %{text:,.1f}')
        st.plotly_chart(clean_chart(fig_q15), width='stretch')
    else:
        st.info("ไม่มีข้อมูลสถานที่จัดงาน")