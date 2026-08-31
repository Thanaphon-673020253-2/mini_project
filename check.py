import os
import duckdb

base_dir = os.path.dirname(os.path.abspath(__file__))
possible_paths = [
    os.path.join(base_dir, "indohotel", "dev.duckdb"),
    os.path.join(base_dir, "dev.duckdb")
]
db_path = next((p for p in possible_paths if os.path.exists(p)), None)

if not db_path:
    print("❌ หาไฟล์ฐานข้อมูล dev.duckdb ไม่พบ")
    exit()

conn = duckdb.connect(db_path, read_only=True)
conn.execute("SET search_path = 'main';")

print("============================================================")
print("🔍 1. ตรวจสอบข้อมูลในตาราง Fact โดยตรง (ไม่ผ่านการ JOIN)")
print("============================================================")

print("\n📌 [A] ตาราง fact_fnb_operations:")
print(conn.execute("""
    SELECT 
        COUNT(*) AS total_rows, 
        SUM(sales_amount) AS total_sales, 
        COUNT(DISTINCT guest_key) AS unique_guests
    FROM fact_fnb_operations;
""").df().to_string(index=False))

print("\n📌 [B] ตาราง fact_ancillary_services:")
print(conn.execute("""
    SELECT 
        COUNT(*) AS total_rows, 
        SUM(spa_revenue) AS total_spa_revenue, 
        SUM(event_revenue) AS total_event_revenue,
        COUNT(DISTINCT guest_key) AS unique_guests
    FROM fact_ancillary_services;
""").df().to_string(index=False))

print("\n============================================================")
print("🔍 2. ทดสอบ JOIN กับ fact_hotel_bookings (เช็กว่าหลุดตอน JOIN หรือไม่)")
print("============================================================")

print("\n📌 [A] การ JOIN ของ F&B (ตาม guest_key และ date_key):")
print(conn.execute("""
    SELECT 
        COUNT(*) AS matched_rows,
        SUM(f.sales_amount) AS matched_fnb_revenue
    FROM fact_hotel_bookings b
    JOIN fact_fnb_operations f 
      ON b.guest_key = f.guest_key AND b.date_key = f.date_key;
""").df().to_string(index=False))

print("\n📌 [B] การ JOIN ของ Spa & Event (ตาม guest_key และ date_key):")
print(conn.execute("""
    SELECT 
        COUNT(*) AS matched_rows,
        SUM(a.spa_revenue) AS matched_spa_revenue,
        SUM(a.event_revenue) AS matched_event_revenue
    FROM fact_hotel_bookings b
    JOIN fact_ancillary_services a 
      ON b.guest_key = a.guest_key AND b.date_key = a.date_key;
""").df().to_string(index=False))

print("\n📌 [C] การ JOIN ของ Spa & Event (ดึงตรงโดยไม่ผ่าน fact_hotel_bookings):")
print(conn.execute("""
    SELECT 
        SUM(spa_revenue) AS total_spa,
        SUM(event_revenue) AS total_event
    FROM fact_ancillary_services;
""").df().to_string(index=False))

conn.close()