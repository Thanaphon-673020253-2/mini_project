import os
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Helper Functions
# ---------------------------------------------------------
st.set_page_config(
    page_title="IndoHotel Executive Analytics",
    page_icon="🏨",
    layout="wide"
)

def clean_chart(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=False, title=""),
        margin=dict(t=35, b=10, l=10, r=10)
    )
    return fig

@st.cache_resource
def get_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, "indohotel", "dev.duckdb"),
        os.path.join(base_dir, "dev.duckdb")
    ]
    db_path = next((p for p in possible_paths if os.path.exists(p)), None)
    
    if not db_path:
        st.error("❌ หาไฟล์ฐานข้อมูล dev.duckdb ไม่พบ")
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
    
    years_df = conn.execute("SELECT DISTINCT year FROM main.dim_date WHERE year BETWEEN 2023 AND 2026 ORDER BY 1 DESC").df()
    selected_year = st.selectbox("📅 เลือกปี", ["ทั้งหมด"] + [str(int(y)) for y in years_df['year']])

    properties_df = conn.execute("SELECT DISTINCT property_name FROM main.dim_property ORDER BY 1").df()
    selected_property = st.selectbox("🏨 เลือกสาขา", ["ทั้งหมด"] + list(properties_df['property_name']))
    
    seasons_df = conn.execute("SELECT DISTINCT season FROM main.dim_date WHERE season IS NOT NULL ORDER BY 1").df()
    selected_season = st.selectbox("🌤️ เลือกฤดูกาล", ["ทั้งหมด"] + list(seasons_df['season']))

# Build SQL WHERE clause
where_clauses = []
if selected_year != "ทั้งหมด":
    where_clauses.append(f"d.year = {selected_year}")
else:
    where_clauses.append("d.year BETWEEN 2023 AND 2026")

if selected_property != "ทั้งหมด":
    where_clauses.append(f"p.property_name = '{selected_property}'")

if selected_season != "ทั้งหมด":
    where_clauses.append(f"d.season = '{selected_season}'")

where_stmt = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

# ---------------------------------------------------------
# Main Title & Navigation
# ---------------------------------------------------------
st.title("🏨 IndoHotel 360 Analytics Dashboard")
st.caption("ระบบวิเคราะห์ข้อมูลเชิงยุทธศาสตร์ ครอบคลุมคำถามการดำเนินงาน 15 ข้อหลัก")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 1. รายได้และผลประกอบการ (Q1-Q4)", 
    "👥 2. ลูกค้าและพฤติกรรม (Q5, Q6, Q8, Q11)", 
    "🛏️ 3. ห้องพักและการจอง (Q9, Q10, Q12)", 
    "📅 4. มิติเวลาและสถานที่ (Q13-Q14)",
    "⚙️ 5. ปฏิบัติการและสถานที่ (Q7, Q15)"
])

# =========================================================
# TAB 1: Revenue & Performance (ข้อ 1 - 4)
# =========================================================
with tab1:
    st.header("1. ด้านรายได้และผลประกอบการ (Revenue & Performance)")
    
    # Q1 Metrics
    q1_df = conn.execute(f"""
        SELECT 
            SUM(b.total_revenue) as total_rev,
            SUM(b.nights) as total_nights
        FROM main.fact_hotel_bookings b
        JOIN main.dim_date d ON b.date_key = d.date_key
        JOIN main.dim_property p ON b.property_key = p.property_key
        {where_stmt}
    """).df()
    
    c1, c2 = st.columns(2)
    c1.metric("ข้อ 1: ยอดขายรวม (Total Revenue)", f"Rp {q1_df['total_rev'][0]:,.0f}" if not q1_df.empty and pd.notna(q1_df['total_rev'][0]) else "Rp 0")
    c2.metric("ข้อ 1: จำนวนคืนที่จอง (Nights)", f"{q1_df['total_nights'][0]:,.0f} คืน" if not q1_df.empty and pd.notna(q1_df['total_nights'][0]) else "0 คืน")
    
    st.markdown("---")
    
    # Q3 Breakdown
    st.markdown("**ข้อ 3: สัดส่วนรายได้และผู้ใช้บริการเสริม แยกตามประเภทบริการ**")
    q3_df = conn.execute(f"""
        SELECT 
            'Food & Beverage' AS service_type,
            COALESCE(SUM(f.sales_amount), 0) AS revenue,
            COUNT(DISTINCT f.guest_key) AS guest_count
        FROM main.fact_fnb_operations f
        JOIN main.dim_date d ON f.date_key = d.date_key
        JOIN main.dim_property p ON f.property_key = p.property_key
        {where_stmt}
        
        UNION ALL
        
        SELECT 
            'Spa & Wellness' AS service_type,
            COALESCE(SUM(a.spa_revenue), 0) AS revenue,
            COUNT(DISTINCT CASE WHEN a.spa_revenue > 0 THEN a.guest_key END) AS guest_count
        FROM main.fact_ancillary_services a
        JOIN main.dim_date d ON a.date_key = d.date_key
        JOIN main.dim_property p ON a.property_key = p.property_key
        {where_stmt}
        
        UNION ALL
        
        SELECT 
            'Event & Venue' AS service_type,
            COALESCE(SUM(a.event_revenue), 0) AS revenue,
            COUNT(CASE WHEN a.event_revenue > 0 THEN 1 END) AS guest_count
        FROM main.fact_ancillary_services a
        JOIN main.dim_date d ON a.date_key = d.date_key
        JOIN main.dim_property p ON a.property_key = p.property_key
        {where_stmt}
        ORDER BY revenue DESC
    """).df()

    if not q3_df.empty:
        m1, m2, m3 = st.columns(3)
        for idx, row in q3_df.iterrows():
            target_col = [m1, m2, m3][idx]
            rev_billions = row['revenue'] / 1e9
            unit_label = "รายการจัดงาน" if row['service_type'] == 'Event & Venue' else "ผู้ใช้บริการ"
            target_col.metric(
                label=f"บริการ {row['service_type']}",
                value=f"Rp {rev_billions:,.2f}B",
                delta=f"{row['guest_count']:,} {unit_label}"
            )
        
        q3_df['revenue_b'] = q3_df['revenue'] / 1e9
        fig_q3 = px.bar(
            q3_df, 
            x='service_type', 
            y='revenue_b', 
            text='revenue_b',
            color='service_type',
            labels={'service_type': 'ประเภทบริการเสริม', 'revenue_b': 'รายได้ (พันล้านรูเปียห์)'}
        )
        fig_q3.update_traces(texttemplate='Rp %{y:.2f}B')
        st.plotly_chart(clean_chart(fig_q3), use_container_width=True)
    else:
        st.info("ไม่พบข้อมูลบริการเสริมตามเงื่อนไขที่เลือก")

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**ข้อ 2: อัตราการเข้าพักเฉลี่ย (Occupancy Rate) แยกตามสาขา**")
        q2_df = conn.execute(f"""
            SELECT p.property_name, AVG(o.occupancy_rate) * 100 as avg_occ
            FROM main.stg_daily_occupancy o
            JOIN main.dim_property p ON o.property_id = p.property_id
            GROUP BY 1 ORDER BY avg_occ DESC
        """).df()
        if not q2_df.empty:
            fig_q2 = px.bar(
                q2_df, 
                x='property_name', 
                y='avg_occ', 
                text='avg_occ', 
                color='property_name',
                range_y=[0, 100]
            )
            fig_q2.update_traces(texttemplate='%{text:.1f}%')
            st.plotly_chart(clean_chart(fig_q2), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูล Occupancy Rate")

# =========================================================
# TAB 2: Customer Analysis (ข้อ 5, 6, 8, 11)
# =========================================================
with tab2:
    st.header("2. ด้านลูกค้าและพฤติกรรม (Customer Analysis)")
    
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("**ข้อ 5: มูลค่าลูกค้า (LTV) และความถี่การเข้าพักซ้ำ ตามระดับสมาชิก (Loyalty Tier)**")
        q5_df = conn.execute(f"""
            SELECT 
                COALESCE(g.loyalty_tier, 'Non-Member') as loyalty_tier,
                SUM(b.total_revenue) / 1e9 as ltv_billions,
                COUNT(b.booking_id) * 1.0 / NULLIF(COUNT(DISTINCT g.guest_key), 0) as repeat_rate
            FROM main.fact_hotel_bookings b
            LEFT JOIN main.dim_guest g ON b.guest_key = g.guest_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
            GROUP BY 1 ORDER BY ltv_billions DESC
        """).df()
        if not q5_df.empty:
            fig_q5 = px.bar(q5_df, x='loyalty_tier', y='ltv_billions', text='repeat_rate', color='loyalty_tier')
            fig_q5.update_traces(texttemplate='พักซ้ำเฉลี่ย %{text:.1f} ครั้ง')
            st.plotly_chart(clean_chart(fig_q5), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูล Loyalty Tier")
        
    with col_d:
        st.markdown("**ข้อ 6: สัญชาติลูกค้าที่มียอดจองสูงสุด Top 5**")
        nat_where = where_stmt + (" AND " if where_stmt else "WHERE ") + "g.nationality IS NOT NULL AND g.nationality != 'Others'"
        q6_df = conn.execute(f"""
            SELECT g.nationality, COUNT(b.booking_id) as bookings
            FROM main.fact_hotel_bookings b
            JOIN main.dim_guest g ON b.guest_key = g.guest_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {nat_where}
            GROUP BY g.nationality ORDER BY bookings DESC LIMIT 5
        """).df()
        if not q6_df.empty:
            fig_q6 = px.bar(q6_df, x='bookings', y='nationality', orientation='h', text='bookings')
            fig_q6.update_traces(texttemplate='%{text:,.0f} รายการ', marker_color='#ff7f0e')
            st.plotly_chart(clean_chart(fig_q6), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลสัญชาติลูกค้า")
        
    st.markdown("---")
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown(
            "**ข้อ 8: เปรียบเทียบจำนวนครั้งการใช้บริการ Food และ Spa "
            "ระหว่างลูกค้าในประเทศและต่างชาติ**"
        )

        q8_df = conn.execute(f"""
            SELECT
                'Food' AS service_type,
                CASE
                    WHEN g.is_domestic = TRUE THEN 'ในประเทศ (Domestic)'
                    ELSE 'ต่างชาติ (International)'
                END AS guest_type,
                COUNT(*) AS service_count
            FROM main.fact_fnb_operations f
            JOIN main.dim_guest g ON f.guest_key = g.guest_key
            JOIN main.dim_date d ON f.date_key = d.date_key
            JOIN main.dim_property p ON f.property_key = p.property_key
            {where_stmt}
                AND f.sales_amount > 0
            GROUP BY 1, 2

            UNION ALL

            SELECT
                'Spa' AS service_type,
                CASE
                    WHEN g.is_domestic = TRUE THEN 'ในประเทศ (Domestic)'
                    ELSE 'ต่างชาติ (International)'
                END AS guest_type,
                COUNT(*) AS service_count
            FROM main.fact_ancillary_services a
            JOIN main.dim_guest g ON a.guest_key = g.guest_key
            JOIN main.dim_date d ON a.date_key = d.date_key
            JOIN main.dim_property p ON a.property_key = p.property_key
            {where_stmt}
                AND a.spa_revenue > 0
            GROUP BY 1, 2
        """).df()

        if not q8_df.empty:
            q8_df["service_type"] = pd.Categorical(
                q8_df["service_type"],
                categories=["Spa", "Food"],
                ordered=True
            )
            q8_df["guest_type"] = pd.Categorical(
                q8_df["guest_type"],
                categories=[
                    "ในประเทศ (Domestic)",
                    "ต่างชาติ (International)"
                ],
                ordered=True
            )
            q8_df = q8_df.sort_values(["service_type", "guest_type"])

            fig_q8 = px.bar(
                q8_df,
                x="service_type",
                y="service_count",
                color="guest_type",
                barmode="group",
                text="service_count",
                category_orders={
                    "service_type": ["Spa", "Food"],
                    "guest_type": [
                        "ในประเทศ (Domestic)",
                        "ต่างชาติ (International)"
                    ]
                },
                labels={
                    "service_type": "ประเภทบริการ",
                    "service_count": "จำนวนครั้งการใช้บริการ",
                    "guest_type": "ประเภทลูกค้า"
                },
                color_discrete_map={
                    "ในประเทศ (Domestic)": "#87CEEB",
                    "ต่างชาติ (International)": "#FFF2B2"
                }
            )

            fig_q8.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside"
            )
            fig_q8.update_layout(
                xaxis_title="ประเภทบริการ",
                yaxis_title="จำนวนครั้งการใช้บริการ",
                legend_title="",
                bargap=0.25,
                yaxis=dict(showgrid=False)
            )

            st.plotly_chart(clean_chart(fig_q8), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลการใช้บริการ Spa และ Food ตามเงื่อนไขที่เลือก")

    with col_f:
        st.markdown("**ข้อ 11: ระยะเวลาเข้าพักเฉลี่ย (Nights Stayed) ตามสาขาโรงแรม**")

        q11_df = conn.execute(f"""
            SELECT 
                p.property_name,
                AVG(b.nights) AS avg_nights
            FROM main.fact_hotel_bookings b
            LEFT JOIN main.dim_guest g ON b.guest_key = g.guest_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
            GROUP BY p.property_name
            ORDER BY avg_nights DESC
        """).df()

        if not q11_df.empty:
            fig_q11 = px.bar(
                q11_df,
                x='property_name',
                y='avg_nights',
                text='avg_nights'
            )
            fig_q11.update_traces(
                texttemplate='%{text:.1f} คืน',
                textposition='outside',
                marker_color='#9467bd'
            )
            fig_q11.update_layout(
                xaxis_title='สาขาโรงแรม',
                yaxis_title='ระยะเวลาเข้าพักเฉลี่ย (คืน)'
            )
            st.plotly_chart(clean_chart(fig_q11), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลระยะเวลาเข้าพักเฉลี่ย")

# =========================================================
# TAB 3: Room & Booking Patterns (ข้อ 9, 10, 12)
# =========================================================
with tab3:
    st.header("3. ด้านประเภทห้องพักและการจอง (Room & Booking Patterns)")
    
    q10_df = conn.execute(f"""
        SELECT AVG(b.lead_time_days) as avg_lead
        FROM main.fact_hotel_bookings b
        JOIN main.dim_property p ON b.property_key = p.property_key
        JOIN main.dim_date d ON b.date_key = d.date_key
        {where_stmt}
    """).df()
    
    lead_val = q10_df['avg_lead'][0] if not q10_df.empty and pd.notna(q10_df['avg_lead'][0]) else 0
    st.metric("ข้อ 10: ระยะเวลาการจองล่วงหน้าเฉลี่ย (Lead Time)", f"{lead_val:,.1f} วัน")
    
    st.markdown("---")
    col_g, col_h = st.columns(2)
    
    with col_g:
        st.markdown("**ข้อ 9: ประเภทห้องพักที่สร้างรายได้หลักและมียอดจองสูงสุด**")
        q9_df = conn.execute(f"""
            SELECT 
                s.room_type, 
                COUNT(b.booking_id) as bookings, 
                SUM(b.total_revenue) / 1e9 as revenue_b
            FROM main.fact_hotel_bookings b
            JOIN main.stg_bookings s ON b.booking_id = s.booking_id
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
            GROUP BY 1 
            ORDER BY revenue_b DESC
        """).df()
        
        if not q9_df.empty and q9_df['revenue_b'].notna().any():
            fig_q9 = px.bar(q9_df, x='room_type', y='revenue_b', text='bookings', color='room_type')
            fig_q9.update_traces(texttemplate='Rp %{y:.1f}B (%{text:,} จอง)')
            st.plotly_chart(clean_chart(fig_q9), use_container_width=True)
        else:
            st.warning("⚠️ ไม่พบข้อมูลประเภทห้องพักตามเงื่อนไขที่เลือก")
        
    with col_h:
        st.markdown("**ข้อ 12: อัตราการยกเลิกการจอง (%) แยกตามประเภทห้องพัก**")
        q12_df = conn.execute(f"""
            SELECT 
                s.room_type,
                AVG(CASE WHEN LOWER(s.status) = 'cancelled' THEN 1.0 ELSE 0.0 END) * 100 as cancel_rate
            FROM main.fact_hotel_bookings b
            JOIN main.stg_bookings s ON b.booking_id = s.booking_id
            JOIN main.dim_property p ON b.property_key = p.property_key
            JOIN main.dim_date d ON b.date_key = d.date_key
            {where_stmt}
            GROUP BY 1 
            ORDER BY cancel_rate DESC
        """).df()
        
        if not q12_df.empty and q12_df['cancel_rate'].notna().any():
            fig_q12 = px.bar(q12_df, x='room_type', y='cancel_rate', text='cancel_rate', color='room_type')
            fig_q12.update_traces(texttemplate='%{text:.1f}%')
            st.plotly_chart(clean_chart(fig_q12), use_container_width=True)
        else:
            st.warning("⚠️ ไม่พบข้อมูลอัตราการยกเลิกตามเงื่อนไขที่เลือก")

# =========================================================
# TAB 4: Time & Location Trends (ข้อ 13 - 14)
# =========================================================
with tab4:
    st.header("4. ด้านมิติเวลาและสถานที่ (Time & Location Trends)")
    
    col_i, col_j = st.columns([2, 1])
    with col_i:
        st.markdown("**ข้อ 13: แนวโน้มรายได้ตามช่วงเดือน / ฤดูกาล (เรียงต่อกันตามลำดับเวลา)**")
        q13_df = conn.execute(f"""
            SELECT 
                CAST(d.year AS VARCHAR) || ' ' || d.month_name AS year_month,
                MIN(d.date_key) as sort_key,
                SUM(b.total_revenue) / 1e9 as revenue_b
            FROM main.fact_hotel_bookings b
            JOIN main.dim_date d ON b.date_key = d.date_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            {where_stmt}
            GROUP BY d.year, d.month_name ORDER BY sort_key
        """).df()
        
        if not q13_df.empty:
            fig_q13 = px.line(
                q13_df, 
                x='year_month', 
                y='revenue_b', 
                markers=True,
                labels={'year_month': 'ช่วงเวลา (ปี เดือน)', 'revenue_b': 'รายได้ (พันล้านรูเปียห์)'}
            )
            fig_q13.update_traces(line_color='#1f77b4', line_width=3)
            fig_q13.update_xaxes(type='category', tickangle=-45)
            st.plotly_chart(clean_chart(fig_q13), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลแนวโน้มรายได้")
        
    with col_j:
        st.markdown("**ข้อ 14: ยอดขาย วันธรรมดา vs วันหยุดสุดสัปดาห์**")
        q14_df = conn.execute(f"""
            SELECT 
                CASE WHEN d.is_weekend THEN 'Weekend' ELSE 'Weekday' END as day_type,
                SUM(b.total_revenue) as revenue
            FROM main.fact_hotel_bookings b
            JOIN main.dim_date d ON b.date_key = d.date_key
            JOIN main.dim_property p ON b.property_key = p.property_key
            {where_stmt}
            GROUP BY 1
        """).df()
        if not q14_df.empty:
            fig_q14 = px.pie(q14_df, values='revenue', names='day_type', hole=0.4)
            fig_q14.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_q14, use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลสัดส่วนวันธรรมดา/วันหยุด")

# =========================================================
# TAB 5: Operations & Venues (ข้อ 7, 15 และการจัดงาน Event)
# =========================================================
with tab5:
    st.header("5. ด้านปฏิบัติการและสถานที่จัดงาน (Operations & Venues)")
    st.markdown("**ข้อ 15: ประเภทสถานที่จัดงาน (Venue Type) ที่มีการจองมากที่สุด**")
    q15_df = conn.execute(f"""
            SELECT 
                v.venue_type,
                COUNT(CASE WHEN a.event_revenue > 0 THEN 1 END) as booking_count,
                SUM(a.event_revenue) / 1e9 as rev_billions
            FROM main.fact_ancillary_services a
            JOIN main.dim_venue v ON a.venue_key = v.venue_key
            JOIN main.dim_property p ON a.property_key = p.property_key
            JOIN main.dim_date d ON a.date_key = d.date_key
            {where_stmt}
            GROUP BY v.venue_type 
            ORDER BY booking_count DESC
        """).df()
        
    if not q15_df.empty and q15_df['booking_count'].notna().any():
            fig_q15 = px.bar(
                q15_df, 
                x='venue_type', 
                y='booking_count', 
                text='booking_count', 
                color='venue_type',
                labels={'venue_type': 'ประเภทสถานที่', 'booking_count': 'จำนวนการจอง (ครั้ง)'}
            )
            fig_q15.update_traces(texttemplate='%{text:,} ครั้ง') 
            st.plotly_chart(clean_chart(fig_q15), use_container_width=True)
    else:
            st.info("ไม่พบข้อมูล Venue Performance")

    st.markdown("---")
    st.markdown("**📌 รายละเอียดประเภทกิจกรรมจัดงาน (Event Type Breakdown)**")
    
    # Query สรุปจำนวนครั้งและรายได้ตามประเภท Event จาก stg_event_bookings
    q_event_type = conn.execute("""
        SELECT 
            TRIM(event_type) AS event_type,
            COUNT(*) AS total_bookings,
            SUM(total_revenue) / 1e9 AS rev_billions
        FROM main.stg_event_bookings
        WHERE event_type IS NOT NULL 
          AND TRIM(event_type) != ''
        GROUP BY 1 
        ORDER BY total_bookings DESC
    """).df()
    
    if not q_event_type.empty:
        col_m, col_n = st.columns(2)
        with col_m:
            fig_evt_count = px.bar(
                q_event_type, 
                x='event_type', 
                y='total_bookings', 
                text='total_bookings',
                color='event_type',
                labels={'event_type': 'ประเภท Event', 'total_bookings': 'จำนวนครั้งที่จัด (ครั้ง)'},
                title="จำนวนครั้งที่จัดแยกตามประเภท Event"
            )
            fig_evt_count.update_traces(texttemplate='%{text:,} ครั้ง')
            st.plotly_chart(clean_chart(fig_evt_count), use_container_width=True)
            
        with col_n:
            fig_evt_rev = px.bar(
                q_event_type, 
                x='event_type', 
                y='rev_billions', 
                text='rev_billions',
                color='event_type',
                labels={'event_type': 'ประเภท Event', 'rev_billions': 'รายได้ (พันล้านรูเปียห์)'},
                title="รายได้รวมแยกตามประเภท Event"
            )
            fig_evt_rev.update_traces(texttemplate='Rp %{y:.2f}B')
            st.plotly_chart(clean_chart(fig_evt_rev), use_container_width=True)
    else:
        st.info("ไม่พบข้อมูลประเภทกิจกรรมจัดงาน (stg_event_bookings)")