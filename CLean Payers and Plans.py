import psycopg2
import re

DB_USER = "postgres"
DB_PASS = "Siri2000"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "MedicalPricing"
TABLE_NAME = "medical_charges_cpt"

select_query = f"""
    SELECT payer_name, plan_name, ctid
    FROM {TABLE_NAME}
    WHERE payer_name IS NOT NULL OR plan_name IS NOT NULL;
"""

update_query = f"""
    UPDATE {TABLE_NAME}
    SET payer_name = %s,
        plan_name  = %s
    WHERE ctid = %s;
"""

# Regex to remove numbers or bracketed numbers from payer/plan names
def clean_name(name):
    if not name:
        return None
    name = name.strip()
    # Remove bracketed numbers like [1234] or (1140)
    name = re.sub(r"\[\s*\d+\s*\]", "", name)
    name = re.sub(r"\(\s*\d+\s*\)", "", name)
    # Remove leading/trailing numbers or symbols
    name = re.sub(r"^[\W\d_]+|[\W\d_]+$", "", name)
    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name)
    return name.strip()

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

    with conn.cursor() as cur:
        print("🔄 Fetching rows to clean...")
        cur.execute(select_query)
        rows = cur.fetchall()

        total_updated = 0
        for payer, plan, ctid in rows:
            payer_clean = clean_name(payer)
            plan_clean = clean_name(plan)

            if (payer_clean != payer) or (plan_clean != plan):
                cur.execute(update_query, (payer_clean, plan_clean, ctid))
                total_updated += 1

        conn.commit()
        print(f"Successfully standardized {total_updated} rows.")

except Exception as e:
    print("Error while cleaning data:", e)
    conn.rollback()

finally:
    if conn:
        conn.close()
        print("Connection closed.")

