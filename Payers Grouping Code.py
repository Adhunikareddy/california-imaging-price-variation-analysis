# map_payers_from_csv.py
import pandas as pd
from sqlalchemy import create_engine, text

CSV_PATH = r"C:\Users\sp599936\Downloads\Payer Names_grouped.csv"
DB_URL   = "postgresql+psycopg2://postgres:Siri2000@localhost:5432/MedicalPricing"
TABLE    = "public.medical_charges_cpt"
COL      = "payer_name"
# ------------------
# 1) read mapping and normalize
map_df = pd.read_csv(CSV_PATH, dtype=str).rename(
    columns=lambda c: c.strip().replace(" ", "_")
)

src_col = [c for c in map_df.columns if c.lower() == "payer_names"][0]
dst_col = [c for c in map_df.columns if c.lower() == "payer_family"][0]

map_df = map_df[[src_col, dst_col]].dropna()
map_df[src_col] = map_df[src_col].astype(str).str.strip().str.upper()
map_df[dst_col] = map_df[dst_col].astype(str).str.strip().str.upper()

# drop duplicates keeping first mapping
map_df = map_df.drop_duplicates(subset=[src_col])

# 2) pull distinct payer_name from DB
engine = create_engine(DB_URL)
db_df = pd.read_sql(
    f"SELECT DISTINCT {COL} FROM {TABLE} WHERE {COL} IS NOT NULL", engine
)
db_df[COL] = db_df[COL].astype(str).str.strip().str.upper()

# 3) join to find matches / misses
joined = db_df.merge(map_df, left_on=COL, right_on=src_col, how="left")
to_update = joined.dropna(subset=[dst_col]).copy()
unmatched = joined[joined[dst_col].isna()][COL].sort_values().unique().tolist()

print(f"Will update {len(to_update)} distinct payer names.")
if unmatched:
    print(f"{len(unmatched)} payer_name values had NO mapping in the CSV (showing up to 25):")
    for v in unmatched[:25]:
        print("  -", v)

# 4) set-based UPDATE (overwrite payer_name with Payer_family)
if len(to_update) > 0:
    # make VALUES list
    conn = engine.raw_connection()
    cur = conn.cursor()
    values = ",\n".join(
        cur.mogrify("(%s,%s)", (old, new)).decode()
        for old, new in to_update[[COL, dst_col]].itertuples(index=False, name=None)
    )
    conn.close()

    with engine.begin() as con:
        # one-time backup of originals
        con.execute(text(f"""
            ALTER TABLE {TABLE}
            ADD COLUMN IF NOT EXISTS {COL}_orig TEXT;
        """))
        con.execute(text(f"""
            UPDATE {TABLE}
            SET {COL}_orig = {COL}
            WHERE {COL}_orig IS NULL;
        """))

        # perform update
        sql = f"""
        WITH m(old_name, fam) AS (VALUES {values})
        UPDATE {TABLE} t
        SET {COL} = m.fam
        FROM m
        WHERE t.{COL} = m.old_name;
        """
        con.execute(text(sql))

    print("payer_name overwritten with Payer_family for all mapped values.")
else:
    print("No updates to apply (no matches found).")
