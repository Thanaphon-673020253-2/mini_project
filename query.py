import os
import duckdb
import matplotlib.pyplot as plt

# 1. เชื่อมต่อฐานข้อมูล DuckDB
db_path = "indohotel/dev.duckdb"

if os.path.exists(db_path):
    conn = duckdb.connect(db_path)
    try:
        # Query ดึงข้อมูลการจัดงานและรายได้แยกตามประเภท Event ทั้งหมด
        query_events = """
            SELECT 
                TRIM(event_type) AS event_type,
                COUNT(*) AS total_bookings,
                SUM(total_revenue) AS total_revenue
            FROM main.stg_event_bookings
            WHERE event_type IS NOT NULL 
              AND TRIM(event_type) != ''
            GROUP BY TRIM(event_type)
            ORDER BY total_bookings DESC;
        """
        
        df = conn.execute(query_events).df()
        
        if not df.empty:
            # กำหนด Font สำหรับแสดงภาษาไทยบน Windows (เช่น Tahoma หรือ Microsoft Sans Serif)
            plt.rcParams['font.family'] = 'Tahoma'
            plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

            # สร้าง Subplots แบบ 2 กราฟคู่กัน (1 แถว 2 คอลัมน์)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # -------------------------------------------------------------
            # กราฟที่ 1: เปรียบเทียบจำนวนครั้งที่จัด (Bookings Count)
            # -------------------------------------------------------------
            bars1 = ax1.barh(df['event_type'], df['total_bookings'], color='#2b5c8f')
            ax1.set_title('เปรียบเทียบจำนวนครั้งที่จัด (Total Bookings)', fontsize=13, fontweight='bold', pad=12)
            ax1.set_xlabel('จำนวนครั้ง (ครั้ง)')
            ax1.invert_yaxis()  # ให้ประเภทที่จัดเยอะที่สุดอยู่ด้านบนสุด
            ax1.bar_label(bars1, fmt='%,d', padding=5, fontsize=10) # แสดงตัวเลขกำกับปลายแท่ง

            # -------------------------------------------------------------
            # กราฟที่ 2: เปรียบเทียบรายได้รวม (Total Revenue)
            # -------------------------------------------------------------
            bars2 = ax2.barh(df['event_type'], df['total_revenue'], color='#2e8b57')
            ax2.set_title('เปรียบเทียบรายได้รวม (Total Revenue)', fontsize=13, fontweight='bold', pad=12)
            ax2.set_xlabel('รายได้รวม (บาท)')
            ax2.invert_yaxis()
            # แสดงตัวเลขกำกับปลายแท่งแบบใส่จุลภาคคั่นพัน
            ax2.bar_label(bars2, labels=[f'{x:,.0f}' for x in df['total_revenue']], padding=5, fontsize=10)

            # จัดระเบียบพื้นที่แสดงผล
            plt.tight_layout()
            
            # บันทึกรูปภาพไว้ในโฟลเดอร์ปัจจุบัน
            plt.savefig('event_comparison_chart.png', dpi=300, bbox_inches='tight')
            print("📸 บันทึกรูปภาพกราฟไว้ที่ 'event_comparison_chart.png' เรียบร้อยแล้ว")

            # แสดงผลหน้าต่างกราฟ
            plt.show()

        else:
            print("ไม่พบข้อมูล Event สำหรับสร้างกราฟ")
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาดขณะสร้างกราฟ: {e}")
    finally:
        conn.close()
else:
    print(f"❌ หาไฟล์ไม่พบที่: {os.path.abspath(db_path)}")