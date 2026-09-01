import os
import duckdb

# 1. กำหนดพาธไฟล์ฐานข้อมูล
db_path = "indohotel/dev.duckdb"

# 2. เช็กว่าไฟล์มีอยู่จริงหรือไม่ก่อนเชื่อมต่อ
if not os.path.exists(db_path):
    print(f"❌ หาไฟล์ไม่พบที่: {os.path.abspath(db_path)}")
    print("กรุณาตรวจสอบว่าอยู่ในโฟลเดอร์ W:\\Learn_Program\\mini_project และมีไฟล์ indohotel/dev.duckdb อยู่จริง")
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
        df_date = conn.execute("SELECT * FROM main.dim_date ").df()
        df_employee = conn.execute("SELECT * FROM main.dim_employee ").df()
        df_fnb_outlet = conn.execute("SELECT * FROM main.dim_fnb_outlet ").df()
        df_guest = conn.execute("SELECT * FROM main.dim_guest ").df()
        df_property = conn.execute("SELECT * FROM main.dim_property ").df()
        df_room = conn.execute("SELECT * FROM main.dim_room ").df()
        df_venue = conn.execute("SELECT * FROM main.dim_venue ").df()
        df_f_ancillary_services = conn.execute("SELECT * FROM main.fact_ancillary_services ").df()
        df_f_fnb_operations = conn.execute("SELECT * FROM main.fact_fnb_operations ").df()
        df_f_hotel_bookings = conn.execute("SELECT * FROM main.fact_hotel_bookings ").df()
        df_f_hotel_operations_hr = conn.execute("SELECT * FROM main.fact_hotel_operations_hr ").df()
        df_event_type = conn.execute("SELECT * FROM main.dim_event_type ").df()

        print("DataFrames loaded successfully:")
        print("===================== date =====================")
        print(df_date)
        print("===================== employee =====================")
        print(df_employee)
        print("===================== fnb_outlet =====================")
        print(df_fnb_outlet)
        print("===================== guest =====================")
        print(df_guest)
        print("===================== property =====================")
        print(df_property)
        print("===================== room =====================")
        print(df_room)
        print("===================== venue =====================")
        print(df_venue)
        print("===================== ancillary_services =====================")
        print(df_f_ancillary_services)
        print("===================== fnb_operations =====================")
        print(df_f_fnb_operations)
        print("===================== hotel_bookings =====================")
        print(df_f_hotel_bookings)
        print("===================== hotel_operations_hr =====================")
        print(df_f_hotel_operations_hr)
        print("===================== event_type =====================")
        print(df_event_type)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดขณะ Query: {e}")

    conn.close()