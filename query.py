import os
import duckdb

# 1. กำหนดพาธไฟล์ฐานข้อมูล
db_path = "indohotel/dev.duckdb"

# 2. เช็กว่าไฟล์มีอยู่จริงหรือไม่ก่อนเชื่อมต่อ
if not os.path.exists(db_path):
    print(f"❌ หาไฟล์ไม่พบที่: {os.path.abspath(db_path)}")
    print("กรุณาตรวจสอบว่าอยู่ในโฟลเดอร์ W:\\Learn_Program\\mini_project และมีไฟล์ indohotel/indohotel.duckdb อยู่จริง")
else:
    # 3. เชื่อมต่อฐานข้อมูล
    conn = duckdb.connect(db_path)

    # 4. ดึงรายชื่อ Table ใน schema 'main'
    tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()

    print("Tables in dev.duckdb:")
    if not tables:
        print("  (ไม่พบข้อมูล Table ใน schema 'main')")
    else:
        for table in tables:
            print(f"  - {table[0]}")

    print("\n" + "=" * 80)

    # 5. ดึงข้อมูล 20 แถวแรกแปลงเป็น DataFrame โดยตรง
    try:
        df2 = conn.execute("SELECT status, COUNT(*) AS total_bookings FROM main.stg_bookings GROUP BY status").df()
        print(df2)
        #df2.to_csv("output.csv", index=False)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดขณะ Query: {e}")

    conn.close()