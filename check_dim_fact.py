import os
import duckdb

db_path = "indohotel/dev.duckdb"

if not os.path.exists(db_path):
    print(f"❌ หาไฟล์ไม่พบที่: {os.path.abspath(db_path)}")
else:
    conn = duckdb.connect(db_path, read_only=True)
    
    # ดึงข้อมูลคอลัมน์ของทุกตารางใน schema 'main'
    query = """
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'main' 
        ORDER BY table_name, ordinal_position;
    """
    
    columns_df = conn.execute(query).df()

    print("=" * 70)
    print(" TABLE COLUMNS STRUCTURE IN DEV.DUCKDB (SCHEMA: MAIN)")
    print("=" * 70)

    current_table = ""
    for _, row in columns_df.iterrows():
        if row["table_name"] != current_table:
            current_table = row["table_name"]
            print(f"\n📂 TABLE: {current_table}")
            print("-" * 50)
        print(f"  - {row['column_name']:<25} : {row['data_type']}")

    print("\n" + "=" * 70)
    print("🎉 ตรวจสอบโครงสร้างคอลัมน์ครบทุกตารางเสร็จสิ้น!")
    print("=" * 70)

    conn.close()