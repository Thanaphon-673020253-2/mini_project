import os
import duckdb

base_dir = os.path.dirname(os.path.abspath(__file__))
possible_paths = [
    os.path.join(base_dir, "indohotel", "dev.duckdb"),
    os.path.join(base_dir, "dev.duckdb")
]
db_path = next((p for p in possible_paths if os.path.exists(p)), None)

if db_path:
    conn = duckdb.connect(db_path, read_only=True)
    
    print("📌 1. ตรวจสอบค่าที่เป็นไปได้ทั้งหมดใน stg_bookings.status (สำหรับ Q12):")
    print(conn.execute("""
        SELECT status, COUNT(*) AS count 
        FROM main.stg_bookings 
        GROUP BY status;
    """).df().to_string(index=False))
    
    print("\n" + "="*50 + "\n")
    
    print("📌 2. ตรวจสอบข้อมูลพื้นที่ใน dim_venue (สำหรับ Q15):")
    print(conn.execute("""
        SELECT venue_key, venue_name, venue_type, area_sqm, max_capacity 
        FROM main.dim_venue;
    """).df().to_string(index=False))
    
    conn.close()