import os
import duckdb

# =========================================================
# หา dev.duckdb
# =========================================================
base_dir = os.path.dirname(os.path.abspath(__file__))

possible_paths = [
    os.path.join(base_dir, "indohotel", "dev.duckdb"),
    os.path.join(base_dir, "dev.duckdb")
]

db_path = next(
    (p for p in possible_paths if os.path.exists(p)),
    None
)

if not db_path:
    print("❌ ไม่พบไฟล์ dev.duckdb")
    print("ตรวจสอบ path แล้ว:")
    for p in possible_paths:
        print(" -", p)
    raise SystemExit

print("=" * 70)
print("DATABASE FOUND")
print("=" * 70)
print(db_path)


# =========================================================
# Connect
# =========================================================
conn = duckdb.connect(
    db_path,
    read_only=True
)

conn.execute("SET search_path = 'main';")


# =========================================================
# 1. รายชื่อตารางทั้งหมด
# =========================================================
print("\n")
print("=" * 70)
print("1. ALL TABLES")
print("=" * 70)

tables_df = conn.execute("""
    SHOW TABLES
""").df()

print(tables_df.to_string(index=False))


# =========================================================
# 2. รายละเอียดทุกตาราง
# =========================================================
print("\n")
print("=" * 70)
print("2. TABLE STRUCTURE")
print("=" * 70)

for table in tables_df["name"]:

    print("\n")
    print("-" * 70)
    print(f"TABLE: {table}")
    print("-" * 70)

    try:

        columns_df = conn.execute(
            f'DESCRIBE main."{table}"'
        ).df()

        print(
            columns_df[
                ["column_name", "column_type"]
            ].to_string(index=False)
        )

    except Exception as e:

        print("❌ ไม่สามารถอ่านตาราง:", e)


# =========================================================
# 3. ค้นหาตารางที่เกี่ยวข้องกับ Ingredient / Price
# =========================================================
print("\n")
print("=" * 70)
print("3. TABLES RELATED TO INGREDIENT / PRICE")
print("=" * 70)

keywords = [
    "ingredient",
    "price",
    "cost",
    "material",
    "inventory",
    "fnb",
    "food"
]

matched_tables = []

for table in tables_df["name"]:

    table_lower = table.lower()

    if any(
        keyword in table_lower
        for keyword in keywords
    ):
        matched_tables.append(table)


if matched_tables:

    for table in matched_tables:
        print("✓", table)

else:

    print("❌ ไม่พบตารางที่ชื่อเกี่ยวข้องโดยตรง")


# =========================================================
# 4. ค้นหา Column ที่เกี่ยวข้องกับ Ingredient / Price
# =========================================================
print("\n")
print("=" * 70)
print("4. COLUMNS RELATED TO INGREDIENT / PRICE")
print("=" * 70)

matched_columns = []

for table in tables_df["name"]:

    try:

        columns_df = conn.execute(
            f'DESCRIBE main."{table}"'
        ).df()

        for _, row in columns_df.iterrows():

            column = str(row["column_name"])
            column_lower = column.lower()

            if any(
                keyword in column_lower
                for keyword in keywords
            ):

                matched_columns.append({
                    "table": table,
                    "column": column,
                    "type": row["column_type"]
                })

    except Exception:
        pass


if matched_columns:

    for item in matched_columns:

        print(
            f"✓ {item['table']}"
            f" → {item['column']}"
            f" ({item['type']})"
        )

else:

    print(
        "❌ ไม่พบ Column ที่ชื่อเกี่ยวข้องโดยตรง"
    )


# =========================================================
# 5. ตรวจสอบตาราง Fact / Dimension โดยเฉพาะ
# =========================================================
print("\n")
print("=" * 70)
print("5. FACT / DIM TABLES")
print("=" * 70)

for table in tables_df["name"]:

    if (
        table.lower().startswith("fact_")
        or table.lower().startswith("dim_")
        or table.lower().startswith("stg_")
    ):

        print(table)


# =========================================================
# 6. ตัวอย่างข้อมูลของตารางที่เกี่ยวข้อง
# =========================================================
print("\n")
print("=" * 70)
print("6. SAMPLE DATA FROM RELATED TABLES")
print("=" * 70)

for table in matched_tables:

    print("\n")
    print("-" * 70)
    print(f"SAMPLE: {table}")
    print("-" * 70)

    try:

        sample_df = conn.execute(
            f'''
            SELECT *
            FROM main."{table}"
            LIMIT 5
            '''
        ).df()

        print(sample_df.to_string(index=False))

    except Exception as e:

        print("❌ Error:", e)


# =========================================================
# DONE
# =========================================================
print("\n")
print("=" * 70)
print("ตรวจสอบ Database เสร็จแล้ว")
print("=" * 70)

conn.close()