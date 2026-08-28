import os
import duckdb

def check_fact():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "indohotel", "dev.duckdb")
    conn = duckdb.connect(db_path, read_only=True)
    conn.execute("SET search_path = 'main';")
    
    # ดูรายชื่อคอลัมน์ทั้งหมดใน fact_hotel_bookings
    cols = conn.execute("DESCRIBE main.fact_hotel_bookings").df()
    print("Columns in fact_hotel_bookings:")
    print(cols[['column_name', 'column_type']])
    
    conn.close()

if __name__ == "__main__":
    check_fact()