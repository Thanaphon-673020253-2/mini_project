import os
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# Page Configuration (ตั้งค่าหน้าเว็บกว้างขึ้น)
# ---------------------------------------------------------
st.set_page_config(page_title="IndoHotel Analytics", page_icon="🏨", layout="wide")

# ฟังก์ชันตกแต่งกราฟให้ดูคลีน (Minimalist Chart)
def clean_chart(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", # พื้นหลังโปร่งใส
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False, title="")), # ซ่อนเส้นกริดและชื่อแกน X
        yaxis=(dict(showgrid=False, title="")), # ซ่อนเส้นกริดและชื่อแกน Y
        showlegend=False, # ซ่อนกล่องสี (Legend) ถ้าระบุสีที่แท่งกราฟแล้ว
        margin=dict(t=40, b=0, l=0, r=0)
    )
    return fig

# ---------------------------------------------------------
# Database Connection
# ---------------------------------------------------------
@st.cache_resource
def get_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "indohotel", "dev.duckdb")
    if not os.path.exists(db_path):
        st.error(f"❌ หาไฟล์ฐานข้อมูลไม่พบ: {db_path}")
        st.stop()
    conn = duckdb.connect(db_path, read_only=True)
    conn.execute("SET search_path = 'main';")
    return conn

conn = get_connection()

# ---------------------------------------------------------
# Sidebar (ตัวกรองข้อมูล)
# ---------------------------------------------------------
with st.sidebar:
    st.title("🎛️ ตัวกรองข้อมูล")
    st.markdown("---")
    
    properties_df = conn.execute("SELECT DISTINCT property_name FROM main.dim_property ORDER BY 1").df()
    selected_property = st.selectbox("🏨 เลือกสาขา", ["ทั้งหมด"] + list(properties_df['property_name']))
    
    seasons_df = conn.execute("SELECT DISTINCT season FROM main.dim_date WHERE season IS NOT NULL ORDER BY 1").df()
    selected_season = st.selectbox("🌤️ เลือกฤดูกาล", ["ทั้งหมด"] + list(seasons_df['season']))

# สร้างเงื่อนไข SQL จากตัวกรอง
where_clauses = []
if selected_property != "ทั้งหมด":
    where_clauses.append(f"p.property_name = '{selected_property}'")
if selected_season != "ทั้งหมด":
    where_clauses.append(f"d.season = '{selected_season}'")
where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title("🏨 IndoHotel Analytics")
st.markdown("แดชบอร์ดสรุปผลประกอบการและพฤติกรรมลูกค้า")
st.markdown("---")

# แบ่งหน้าจอ (Tabs) ให้กระชับขึ้น
tab1, tab2, tab3, tab4 = st.tabs(["💰 รายได้ (Revenue)", "👥 ลูกค้า (Customers)", "🛏️ การจอง (Bookings)", "⚙️ ปฏิบัติการ (Operations)"])

# =========================================================
# TAB 1: รายได้ (Revenue)
# =========================================================
with tab1:
    # ดึงข้อมูล KPI
    kpi_query = f"""
        SELECT 
            SUM(b.total_revenue) as total_revenue,
            SUM(b.nights) as total_nights,
            AVG(b.total_revenue / NULLIF(b.nights, 0)) as adr,
            SUM(b.total_revenue) / NULLIF(SUM(p.total_rooms), 0) as revpar
        FROM main.fact_hotel_bookings b
        JOIN main.dim_property p ON b.property_key = p.property_key
        JOIN main.dim_date d ON b.date_key = d.date_key
        {where_sql}
    """
    kpi_df = conn.execute(kpi_query).df()
    
    # สรุปตัวเลข (KPI Scorecards)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ยอดขายรวม", f"${kpi_df['total_revenue'][0]:,.0f}" if pd.notna(kpi_df['total_revenue'][0]) else "$0")
    col2.metric("จำนวนคืนที่จอง", f"{kpi_df['total_nights'][0]:,.0f}" if pd.notna(kpi_df['total_nights'][0]) else "0")
    col3.metric("รายได้เฉลี่ย/คืน (ADR)", f"${kpi_df['adr'][0]:,.0f}" if pd.notna(kpi_df['adr'][0]) else "$0")
    col4.metric("รายได้ต่อห้อง (RevPAR)", f"${kpi_df['revpar'][0]:,.0f}" if pd.notna(kpi_df['revpar'][0]) else "$0")
    
    st.markdown("<br>", unsafe_allow_html=True) # เว้นบรรทัดให้โปร่งขึ้น
    
    col_a, col_b = st.columns([2, 1]) # ให้กราฟซ้ายใหญ่กว่ากราฟขวา
    
    with col_a:
        st.markdown("**แนวโน้มรายได้รายเดือน**")
        
        monthly_query = f"""
            SELECT 
                d.month_name, 
                MIN(d.date_key) as sort_date, 
                SUM(b.total_revenue) as revenue 
            FROM main.fact_hotel_bookings b 
            JOIN main.dim_date d ON b.date_key = d.date_key 
            JOIN main.dim_property p ON b.property_key = p.property_key 
            {where_sql} 
            GROUP BY d.year, d.month_name 
            ORDER BY sort_date ASC
        """
        monthly_df = conn.execute(monthly_query).df()
        
        # สร้างกราฟแท่ง
        fig_monthly = px.bar(
            monthly_df, 
            x='month_name', 
            y='revenue', 
            text_auto='.2s'
        )
        
        # บังคับซ่อนเส้นขอบและเส้นตารางภายในแท่งกราฟทั้งหมด
        fig_monthly.update_traces(
            marker_color='#ff7f0e',          # สีส้มของแท่ง
            marker_line_color='#ff7f0e',     # ปรับสีเส้นขอบให้เป็นสีเดียวกับแท่ง (เส้นจะกลืนหายไป)
            marker_line_width=1              # กำหนดความหนาเส้นขอบ
        )
        
        st.plotly_chart(clean_chart(fig_monthly), use_container_width=True)
    with col_b:
        st.markdown("**สัดส่วนวันธรรมดา vs วันหยุด**")
        weekend_df = conn.execute(f"SELECT CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END as day_type, SUM(b.total_revenue) as revenue FROM main.fact_hotel_bookings b JOIN main.dim_date d ON b.date_key = d.date_key JOIN main.dim_property p ON b.property_key = p.property_key {where_sql} GROUP BY 1").df()
        fig_weekend = px.pie(weekend_df, values='revenue', names='day_type', hole=0.5)
        fig_weekend.update_traces(textinfo='percent+label') # โชว์แค่ % กับป้าย
        fig_weekend.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_weekend, use_container_width=True)

    st.markdown("**รายได้แยกตามสาขา**")
    branch_df = conn.execute(f"SELECT p.property_name, SUM(b.total_revenue) as revenue FROM main.fact_hotel_bookings b JOIN main.dim_property p ON b.property_key = p.property_key JOIN main.dim_date d ON b.date_key = d.date_key {where_sql} GROUP BY p.property_name ORDER BY revenue DESC").df()
    fig_branch = px.bar(branch_df, x='property_name', y='revenue', color='property_name', text_auto='.2s')
    st.plotly_chart(clean_chart(fig_branch), use_container_width=True)

# =========================================================
# TAB 2: ลูกค้า (Customers)
# =========================================================
with tab2:
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("**Top 5 สัญชาติลูกค้า (ตามยอดจอง)**")
        nat_df = conn.execute(f"SELECT g.nationality, COUNT(b.booking_id) as count FROM main.fact_hotel_bookings b JOIN main.dim_guest g ON b.guest_key = g.guest_key JOIN main.dim_property p ON b.property_key = p.property_key JOIN main.dim_date d ON b.date_key = d.date_key {where_sql} GROUP BY g.nationality ORDER BY count DESC LIMIT 5").df()
        fig_nat = px.bar(nat_df, x='count', y='nationality', orientation='h', text_auto=True) # ปรับเป็นแนวนอนให้อ่านง่าย
        st.plotly_chart(clean_chart(fig_nat), use_container_width=True)
        
    with col_d:
        st.markdown("**มูลค่าลูกค้าตามระดับสมาชิก (LTV)**")
        ltv_df = conn.execute(f"SELECT g.loyalty_tier, SUM(b.total_revenue) as revenue FROM main.fact_hotel_bookings b JOIN main.dim_guest g ON b.guest_key = g.guest_key JOIN main.dim_property p ON b.property_key = p.property_key JOIN main.dim_date d ON b.date_key = d.date_key {where_sql} GROUP BY g.loyalty_tier ORDER BY revenue DESC").df()
        fig_ltv = px.bar(ltv_df, x='loyalty_tier', y='revenue', text_auto='.2s')
        fig_ltv.update_traces(marker_color='#1f77b4') # ใช้สีเดียวล้วนๆ ให้ดูมินิมอล
        st.plotly_chart(clean_chart(fig_ltv), use_container_width=True)

# =========================================================
# TAB 3: การจอง (Bookings)
# =========================================================
with tab3:
    col_g, col_h = st.columns(2)
    with col_g:
        lead_df = conn.execute(f"SELECT AVG(b.lead_time_days) as lead FROM main.fact_hotel_bookings b JOIN main.dim_property p ON b.property_key = p.property_key JOIN main.dim_date d ON b.date_key = d.date_key {where_sql}").df()
        st.metric("⏳ ระยะเวลาจองล่วงหน้าเฉลี่ย", f"{lead_df['lead'][0]:,.1f} วัน" if pd.notna(lead_df['lead'][0]) else "0 วัน")
    with col_h:
        stay_df = conn.execute(f"SELECT AVG(b.nights) as nights FROM main.fact_hotel_bookings b JOIN main.dim_property p ON b.property_key = p.property_key JOIN main.dim_date d ON b.date_key = d.date_key {where_sql}").df()
        st.metric("🛏️ ระยะเวลาเข้าพักเฉลี่ย", f"{stay_df['nights'][0]:,.1f} คืน" if pd.notna(stay_df['nights'][0]) else "0 คืน")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_e, col_f = st.columns(2)
    with col_e:
        st.markdown("**รายได้ตามประเภทห้องพัก**")
        room_df = conn.execute(f"SELECT r.room_type, SUM(b.total_revenue) as revenue FROM main.fact_hotel_bookings b JOIN main.dim_room r ON b.room_key = r.room_key JOIN main.dim_property p ON b.property_key = p.property_key JOIN main.dim_date d ON b.date_key = d.date_key {where_sql} GROUP BY r.room_type ORDER BY revenue DESC").df()
        fig_room = px.bar(room_df, x='room_type', y='revenue', text_auto='.2s')
        st.plotly_chart(clean_chart(fig_room), use_container_width=True)
        
    with col_f:
        st.markdown("**สถานะการจอง (สำเร็จ vs ยกเลิก)**")
        cancel_df = conn.execute(f"SELECT CASE WHEN b.is_canceled THEN 'ยกเลิก (Canceled)' ELSE 'สำเร็จ (Completed)' END as status, COUNT(b.booking_id) as count FROM main.fact_hotel_bookings b JOIN main.dim_property p ON b.property_key = p.property_key JOIN main.dim_date d ON b.date_key = d.date_key {where_sql} GROUP BY 1").df()
        fig_cancel = px.pie(cancel_df, values='count', names='status', hole=0.5)
        fig_cancel.update_traces(textinfo='percent+label')
        fig_cancel.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_cancel, use_container_width=True)

# =========================================================
# TAB 4: ปฏิบัติการ (Operations)
# =========================================================
with tab4:
    hr_df = conn.execute(f"SELECT SUM(h.maintenance_cost) as cost, SUM(h.maintenance_ticket_count) as tickets FROM main.fact_hotel_operations_hr h JOIN main.dim_property p ON h.property_key = p.property_key JOIN main.dim_date d ON h.date_key = d.date_key {where_sql}").df()
    
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("🔧 จำนวนแจ้งซ่อม (Tickets)", f"{hr_df['tickets'][0]:,.0f} รายการ" if pd.notna(hr_df['tickets'][0]) else "0")
    col_m2.metric("💸 ค่าใช้จ่ายซ่อมบำรุง", f"${hr_df['cost'][0]:,.0f}" if pd.notna(hr_df['cost'][0]) else "$0")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**รายได้เสริมจากสถานที่จัดงาน (Venue Revenue)**")
    venue_df = conn.execute("SELECT v.venue_type, SUM(a.event_revenue) as revenue FROM main.fact_ancillary_services a JOIN main.dim_venue v ON a.venue_key = v.venue_key GROUP BY v.venue_type ORDER BY revenue DESC").df()
    fig_venue = px.bar(venue_df, x='venue_type', y='revenue', text_auto='.2s')
    fig_venue.update_traces(marker_color='#2ca02c') # ใช้โทนสีเขียว
    st.plotly_chart(clean_chart(fig_venue), use_container_width=True)