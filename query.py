import os
import duckdb

# 1. กำหนดพาธไฟล์ฐานข้อมูล
db_path = "indohotel/dev.duckdb"

# 2. เช็กว่าไฟล์มีอยู่จริงหรือไม่ก่อนเชื่อมต่อ
if not os.path.exists(db_path):
    print(f"❌ หาไฟล์ไม่พบที่: {os.path.abspath(db_path)}")
    print(
        "กรุณาตรวจสอบว่าอยู่ในโฟลเดอร์ "
        "W:\\Learn_Program\\mini_project "
        "และมีไฟล์ indohotel/dev.duckdb อยู่จริง"
    )
else:
    # 3. เชื่อมต่อฐานข้อมูล
    conn = duckdb.connect(db_path)

    # 4. ดึงรายชื่อ Table ใน schema 'main'
    tables = conn.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
    """).fetchall()

    print("Tables in dev.duckdb:")

    if not tables:
        print("  (ไม่พบข้อมูล Table ใน schema 'main')")
    else:
        for table in tables:
            print(f"  - {table[0]}")

    print("\n" + "=" * 80)

    # 5. Query ข้อ 8
    # เปรียบเทียบจำนวนครั้งการใช้บริการ
    # Food และ Spa ระหว่างลูกค้าในประเทศและต่างชาติ
    try:
        q8_query = """
            SELECT
                service_type,
                guest_type,
                service_count
            FROM (
                -- =========================
                -- Food & Beverage
                -- =========================
                SELECT
                    'Food' AS service_type,
                    CASE
                        WHEN g.is_domestic = TRUE
                            THEN 'ในประเทศ (Domestic)'
                        ELSE 'ต่างชาติ (International)'
                    END AS guest_type,
                    COUNT(*) AS service_count,
                    2 AS sort_order
                FROM main.fact_fnb_operations f
                JOIN main.dim_guest g
                    ON f.guest_key = g.guest_key
                JOIN main.dim_date d
                    ON f.date_key = d.date_key
                JOIN main.dim_property p
                    ON f.property_key = p.property_key
                WHERE f.sales_amount > 0
                GROUP BY
                    service_type,
                    guest_type

                UNION ALL

                -- =========================
                -- Spa & Wellness
                -- =========================
                SELECT
                    'Spa' AS service_type,
                    CASE
                        WHEN g.is_domestic = TRUE
                            THEN 'ในประเทศ (Domestic)'
                        ELSE 'ต่างชาติ (International)'
                    END AS guest_type,
                    COUNT(*) AS service_count,
                    1 AS sort_order
                FROM main.fact_ancillary_services a
                JOIN main.dim_guest g
                    ON a.guest_key = g.guest_key
                JOIN main.dim_date d
                    ON a.date_key = d.date_key
                JOIN main.dim_property p
                    ON a.property_key = p.property_key
                WHERE a.spa_revenue > 0
                GROUP BY
                    service_type,
                    guest_type
            ) q
            ORDER BY
                sort_order,
                guest_type
        """

        df2 = conn.execute(q8_query).df()

        print("ข้อ 8: จำนวนครั้งการใช้บริการ Food และ Spa")
        print("ระหว่างลูกค้าในประเทศและต่างชาติ")
        print("=" * 80)

        print(df2.to_string(index=False))

        print("\nColumns:")
        print(df2.columns.tolist())

    except Exception as e:
        print(f"เกิดข้อผิดพลาดขณะ Query: {e}")

    # ตรวจสอบค่า is_domestic ใน dim_guest
    try:
        check_query = """
            SELECT
                g.is_domestic,
                COUNT(*) AS guest_count
            FROM main.dim_guest g
            GROUP BY g.is_domestic
            ORDER BY g.is_domestic
        """

        check_df = conn.execute(check_query).df()

        print("ตรวจสอบค่า is_domestic ใน dim_guest")
        print("=" * 80)
        print(check_df.to_string(index=False))

    except Exception as e:
        print(f"เกิดข้อผิดพลาดขณะตรวจสอบ is_domestic: {e}")

    try:
        check_query = """
            SELECT
                nationality,
                COUNT(*) AS guest_count
            FROM main.stg_guests
            GROUP BY nationality
            ORDER BY guest_count DESC
        """

        check_df = conn.execute(check_query).df()

        print("Nationality ใน stg_guests")
        print("=" * 80)
        print(check_df.to_string(index=False))

    except Exception as e:
        print(f"เกิดข้อผิดพลาดขณะ Query: {e}")
    conn.close()