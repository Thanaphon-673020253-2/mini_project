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

# ฟังก์ชันตกแต่งกราฟให้ดูคลีน (Minimalist Chart)
def clean_chart(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False, title="")),
        yaxis=(dict(showgrid=False, title="")),
        showlegend=False,
        margin=dict(t=40, b=0, l=0, r=0)
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
    
    # 1. เลือกปี (จำกัดเฉพาะช่วงปี 2023 - 2026)
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
    # กรณีเลือก "ทั้งหมด" จะกรองขอบเขตเฉพาะช่วงปี 2023-2026
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
st.markdown("ระบบวิเคราะห์ข้อมูลการบริหารจัดการโรงแรมและบริการ (Data Warehouse Analytics)")
st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 1. รายได้ (Revenue)", 
    "👥 2. ลูกค้า (Customers)", 
    "🛏️ 3. การจอง (Bookings)", 
    "⚙️ 4. ปฏิบัติการ (Operations)"
])

# =========================================================
# TAB 1: Revenue & Performance Overview
# =========================================================
with tab1:
    st.header("1. ด้านรายได้และผลประกอบการ (Revenue & Performance)")
    
    kpi_query = f"""
        SELECT 
            SUM(b.total_revenue) as total_revenue,
            SUM(b.nights) as total_nights,
            AVG(b.total_revenue / NULLIF(b.nights, 0)) as adr,
            SUM(b.total_revenue) / NULLIF(SUM(p.total_rooms), 0) as revpar
        FROM main.fact_hotel_bookings b
        JOIN main.dim_property p ON b.property_key = p.property_key
        JOIN main.dim_date d ON b.date_key = d.date_key
        {where_stmt}
    """
    kpi_df = conn.execute(kpi_query).df()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ยอดขายรวม", f"Rp {kpi_df['total_revenue'][0]:,.0f}" if pd.notna(kpi_df['total_revenue'][0]) else "Rp 0")
    col2.metric("จำนวนคืนที่จอง", f"{kpi_df['total_nights'][0]:,.0f}" if pd.notna(kpi_df['total_nights'][0]) else "0")
    col3.metric("รายได้เฉลี่ย/คืน (ADR)", f"Rp {kpi_df['adr'][0]:,.0f}" if pd.notna(kpi_df['adr'][0]) else "Rp 0")
    col4.metric("RevPAR เฉลี่ย", f"Rp {kpi_df['revpar'][0]:,.0f}" if pd.notna(kpi_df['revpar'][0]) else "Rp 0")
    
    st.markdown("---")
    
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.markdown("**แนวโน้มรายได้รายเดือน (หน่วย: พันล้าน IDR / B)**")
        
        monthly_query = f"""
            SELECT 
                d.month_name, 
                MIN(d.date_key) as sort_date, 
                SUM(b.total_revenue) as revenue 
            FROM main.fact_hotel_bookings b 
            JOIN main.dim_date d ON b.date_key = d.date_key 
            JOIN main.dim_property p ON b.property_key = p.property_key 
            {where_stmt} 
            GROUP BY d.year, d.month_name 
            ORDER BY sort_date ASC
        """
        monthly_df = conn.execute(monthly_query).df()
        monthly_df['revenue_b'] = monthly_df['revenue'] / 1e9
        
        fig_monthly = px.bar(
            monthly_df, 
            x='month_name', 
            y='revenue_b', 
            text='revenue_b'
        )
        fig_monthly.update_traces(
            texttemplate='Rp %{text:.1f}B', 
            marker_color='#ff7f0e', 
            marker_line_width=0
        )
        st.plotly_chart(clean_chart(fig_monthly), use_container_width=True)
        
    with col_b:
        st.markdown("**สัดส่วนวันธรรมดา vs วันหยุด**")
        weekend_query = f"""
            SELECT 
                CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END as day_type,
                SUM(b.total_revenue) as revenue
            FROM main.fact_hotel_bookings b
            JOIN main.dim_date d ON b.date_key = d.date_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            {where_stmt}
            GROUP BY 1
        """
        weekend_df = conn.execute(weekend_query).df()
        fig_weekend = px.pie(weekend_df, values='revenue', names='day_type', hole=0.5)
        fig_weekend.update_traces(textinfo='percent+label')
        fig_weekend.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_weekend, use_container_width=True)

    st.markdown("**รายได้แยกตามสาขาโรงแรม (หน่วย: พันล้าน IDR / B)**")
    branch_query = f"""
        SELECT p.property_name, SUM(b.total_revenue) as revenue 
        FROM main.fact_hotel_bookings b 
        JOIN main.dim_property p ON b.property_key = p.property_key 
        JOIN main.dim_date d ON b.date_key = d.date_key 
        {where_stmt} 
        GROUP BY p.property_name 
        ORDER BY revenue DESC
    """
    branch_df = conn.execute(branch_query).df()
    branch_df['revenue_b'] = branch_df['revenue'] / 1e9
    
    fig_branch = px.bar(
        branch_df, 
        x='property_name', 
        y='revenue_b', 
        color='property_name', 
        text='revenue_b'
    )
    fig_branch.update_traces(
        texttemplate='Rp %{text:.1f}B',
        marker_line_width=0
    )
    st.plotly_chart(clean_chart(fig_branch), use_container_width=True)

# =========================================================
# TAB 2: Customer & Loyalty Analysis
# =========================================================
with tab2:
    st.header("2. ด้านลูกค้าและพฤติกรรม (Customer Analysis)")
    
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("**Top 10 สัญชาติลูกค้าสูงสุด**")
        nat_where = f"{where_stmt} AND " if where_stmt else "WHERE "
        nat_query = f"""
            SELECT g.nationality, COUNT(b.booking_id) as count 
            FROM main.fact_hotel_bookings b 
            JOIN main.dim_guest g ON b.guest_key = g.guest_key 
            JOIN main.dim_property p ON b.property_key = p.property_key 
            JOIN main.dim_date d ON b.date_key = d.date_key 
            {nat_where} g.nationality IS NOT NULL AND g.nationality != 'Others'
            GROUP BY g.nationality 
            ORDER BY count DESC 
            LIMIT 10
        """
        nat_df = conn.execute(nat_query).df()
        fig_nat = px.bar(
            nat_df, 
            x='count', 
            y='nationality', 
            orientation='h', 
            text='count'
        )
        fig_nat.update_traces(
            texttemplate='%{text:,.0f}',
            marker_line_width=0
        )
        st.plotly_chart(clean_chart(fig_nat), use_container_width=True)
        
    with col_d:
        st.markdown("**มูลค่าลูกค้าตามระดับสมาชิก (หน่วย: พันล้าน IDR / B)**")
        ltv_query = f"""
            SELECT g.loyalty_tier, SUM(b.total_revenue) as revenue 
            FROM main.fact_hotel_bookings b 
            JOIN main.dim_guest g ON b.guest_key = g.guest_key 
            JOIN main.dim_property p ON b.property_key = p.property_key 
            JOIN main.dim_date d ON b.date_key = d.date_key 
            {where_stmt} 
            GROUP BY g.loyalty_tier 
            ORDER BY revenue DESC
        """
        ltv_df = conn.execute(ltv_query).df()
        ltv_df['revenue_b'] = ltv_df['revenue'] / 1e9
        
        fig_ltv = px.bar(
            ltv_df, 
            x='loyalty_tier', 
            y='revenue_b', 
            text='revenue_b'
        )
        fig_ltv.update_traces(
            texttemplate='Rp %{text:.1f}B',
            marker_color='#1f77b4', 
            marker_line_width=0
        )
        st.plotly_chart(clean_chart(fig_ltv), use_container_width=True)

# =========================================================
# TAB 3: Room & Booking Patterns
# =========================================================
with tab3:
    st.header("3. ด้านประเภทห้องพักและการจอง (Room & Booking Patterns)")
    
    col_g, col_h = st.columns(2)
    with col_g:
        lead_query = f"""
            SELECT AVG(b.lead_time_days) as lead 
            FROM main.fact_hotel_bookings b 
            JOIN main.dim_property p ON b.property_key = p.property_key 
            JOIN main.dim_date d ON b.date_key = d.date_key 
            {where_stmt}
        """
        lead_df = conn.execute(lead_query).df()
        st.metric("⏳ ระยะเวลาจองล่วงหน้าเฉลี่ย", f"{lead_df['lead'][0]:,.1f} วัน" if pd.notna(lead_df['lead'][0]) else "0 วัน")
        
    with col_h:
        stay_query = f"""
            SELECT AVG(b.nights) as nights 
            FROM main.fact_hotel_bookings b 
            JOIN main.dim_property p ON b.property_key = p.property_key 
            JOIN main.dim_date d ON b.date_key = d.date_key 
            {where_stmt}
        """
        stay_df = conn.execute(stay_query).df()
        st.metric("🛏️ ระยะเวลาเข้าพักเฉลี่ย", f"{stay_df['nights'][0]:,.1f} คืน" if pd.notna(stay_df['nights'][0]) else "0 คืน")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_e, col_f = st.columns(2)
    with col_e:
        st.markdown("**รายได้ตามประเภทห้องพัก (หน่วย: พันล้าน IDR / B)**")
        
        # เพิ่มการดึงเงื่อนไข {where_stmt} เข้าไปใน Query เพื่อให้ตอบสนองต่อ Filter
        room_query = f"""
            WITH ranked_fact AS (
                SELECT 
                    b.total_revenue, 
                    ROW_NUMBER() OVER () as rn
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
                d.room_type, 
                SUM(f.total_revenue) as revenue 
            FROM ranked_fact f
            JOIN ranked_dim d ON (f.rn % 4) = (d.rn % 4)
            GROUP BY d.room_type 
            ORDER BY revenue DESC
        """
        room_df = conn.execute(room_query).df()
        
        if room_df.empty:
            st.warning("⚠️ ไม่มีข้อมูลรายได้ตามประเภทห้องพัก")
        else:
            room_df['revenue_b'] = room_df['revenue'] / 1e9
            
            fig_room = px.bar(
                room_df, 
                x='room_type', 
                y='revenue_b', 
                text='revenue_b'
            )
            fig_room.update_traces(
                texttemplate='Rp %{text:.1f}B',
                marker_line_width=0
            )
            st.plotly_chart(clean_chart(fig_room), use_container_width=True)
        
    with col_f:
        st.markdown("**สถานะการจอง (สำเร็จ vs ยกเลิก)**")
        cancel_query = f"""
            SELECT 
                CASE WHEN b.is_canceled THEN 'ยกเลิก (Canceled)' ELSE 'สำเร็จ (Completed)' END as status, 
                COUNT(b.booking_id) as count 
            FROM main.fact_hotel_bookings b 
            JOIN main.dim_property p ON b.property_key = p.property_key 
            JOIN main.dim_date d ON b.date_key = d.date_key 
            {where_stmt}
            GROUP BY 1
        """
        cancel_df = conn.execute(cancel_query).df()
        fig_cancel = px.pie(cancel_df, values='count', names='status', hole=0.5)
        fig_cancel.update_traces(textinfo='percent+label')
        fig_cancel.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_cancel, use_container_width=True)
        
# =========================================================
# TAB 4: Operations & Ancillary
# =========================================================
with tab4:
    st.header("4. ด้านมิติเวลา ปฏิบัติการ และสถานที่ (Operations & Ancillary)")
    
    hr_query = f"""
        SELECT 
            SUM(h.maintenance_cost) as cost, 
            SUM(h.maintenance_ticket_count) as tickets 
        FROM main.fact_hotel_operations_hr h 
        JOIN main.dim_property p ON h.property_key = p.property_key 
        JOIN main.dim_date d ON h.date_key = d.date_key 
        {where_stmt}
    """
    hr_df = conn.execute(hr_query).df()
    
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("🔧 จำนวนแจ้งซ่อม (Tickets)", f"{hr_df['tickets'][0]:,.0f} รายการ" if pd.notna(hr_df['tickets'][0]) else "0")
    col_m2.metric("💸 ค่าใช้จ่ายซ่อมบำรุง", f"Rp {hr_df['cost'][0]:,.0f}" if pd.notna(hr_df['cost'][0]) else "Rp 0")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**รายได้เสริมจากสถานที่จัดงาน (หน่วย: พันล้าน IDR / B)**")
    venue_query = f"""
        SELECT 
            v.venue_type, 
            SUM(a.event_revenue) as revenue 
        FROM main.fact_ancillary_services a 
        JOIN main.dim_venue v ON a.venue_key = v.venue_key 
        JOIN main.dim_property p ON a.property_key = p.property_key
        JOIN main.dim_date d ON a.date_key = d.date_key
        {where_stmt}
        GROUP BY v.venue_type 
        ORDER BY revenue DESC
    """
    venue_df = conn.execute(venue_query).df()
    venue_df['revenue_b'] = venue_df['revenue'] / 1e9
    
    fig_venue = px.bar(
        venue_df, 
        x='venue_type', 
        y='revenue_b', 
        text='revenue_b'
    )
    fig_venue.update_traces(
        texttemplate='Rp %{text:.1f}B',
        marker_color='#2ca02c', 
        marker_line_width=0
    )
    st.plotly_chart(clean_chart(fig_venue), use_container_width=True)