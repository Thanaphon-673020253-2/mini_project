import os
import duckdb

# 1. กำหนดพาธไฟล์ฐานข้อมูล
db_path = "indohotel/dev.duckdb"

# 2. เช็กว่าไฟล์มีอยู่จริงหรือไม่ก่อนเชื่อมต่อ
if not os.path.exists(db_path):
    print(f"❌ หาไฟล์ไม่พบที่: {os.path.abspath(db_path)}")
    print("กรุณาตรวจสอบว่าไฟล์ dev.duckdb อยู่ในโฟลเดอร์ indohotel")

else:
    # 3. เชื่อมต่อฐานข้อมูล
    conn = duckdb.connect(db_path)

    # 4. ดึงรายชื่อ Table ใน schema 'main'
    tables = conn.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
        ORDER BY table_name
    """).fetchall()

    print("Tables in dev.duckdb:")

    if not tables:
        print("  (ไม่พบข้อมูล Table ใน schema 'main')")
    else:
        for table in tables:
            print(f"  - {table[0]}")

    print("\n" + "=" * 80)

    # 5. Query ข้อมูล Spa Booking + Guest
    try:
        df2 = conn.execute("""
            SELECT
                COUNT(*) AS total_spa_bookings
            FROM main.stg_spa_bookings s
            LEFT JOIN main.stg_guests g
                ON s.guest_id = g.guest_id
            WHERE g.nationality IS NOT NULL
                AND UPPER(TRIM(g.nationality)) == 'INDONESIA'

        """).df()

        print("\nจำนวนการจอง Spa แยกตามสัญชาติ:")
        print(df2)

        print("\nColumns:")
        print(df2.columns)

        # ถ้าต้องการบันทึกเป็น CSV
        # df2.to_csv("spa_booking_by_nationality.csv", index=False)

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดขณะ Query: {e}")

    # 6. ปิดการเชื่อมต่อ
    conn.close()