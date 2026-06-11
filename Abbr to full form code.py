# expand_plan_abbrevs.py
import re
from sqlalchemy import create_engine, text
import pandas as pd

# ----------------- SETTINGS -----------------
DB_URL = "postgresql+psycopg2://postgres:Siri2000@localhost:5432/MedicalPricing"
TABLE  = "public.medical_charges_cpt"
COL    = "plan_name"

# After expanding to full forms, collapse spaces?
REMOVE_SPACES_AFTER_EXPANSION = False   # set True if you want UNITED HEALTHCARE -> UNITEDHEALTHCARE

# Abbreviation -> full form (edit/extend freely)
ABBR = {
    "HMO":  "HEALTH MAINTENANCE ORGANIZATION",
    "PPO":  "PREFERRED PROVIDER ORGANIZATION",
    "EPO":  "EXCLUSIVE PROVIDER ORGANIZATION",
    "POS":  "POINT OF SERVICE",
    "EPN":  "EMPLOYEE PROVIDER NETWORK",          # safer generic
    "PPG":  "PARTICIPATING PHYSICIAN GROUP",
    "IFP":  "INDIVIDUAL AND FAMILY PLAN",
    "UHC":  "UNITEDHEALTHCARE",
    "UMR":  "UNITEDHEALTHCARE (UMR TPA)",
    "UFCW": "UNITED FOOD AND COMMERCIAL WORKERS",
    "GEHA": "GOVERNMENT EMPLOYEES HEALTH ASSOCIATION",
    "BCBS": "BLUE CROSS BLUE SHIELD",
    "WC":   "WORKERS' COMPENSATION",
    "BCEDP":"BREAST AND CERVICAL EARLY DETECTION PROGRAM",
    "AARP": "UNITEDHEALTHCARE"
}


# Build compiled regexes with safe token boundaries:
# (?<![A-Z0-9])ABC(?![A-Z0-9])   → match ABC not inside a bigger token
PATTERNS = [(re.compile(rf"(?<![A-Z0-9]){re.escape(k)}(?![A-Z0-9])", re.I), v) for k, v in ABBR.items()]

def expand_abbrevs(name: str) -> str:
    if not isinstance(name, str):
        return name
    s = name.upper()
    for pat, repl in PATTERNS:
        s = pat.sub(repl.upper(), s)
    if REMOVE_SPACES_AFTER_EXPANSION:
        s = s.replace(" ", "")
    # squeeze accidental double spaces if you keep spaces
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s

# ----------------- RUN -----------------
engine = create_engine(DB_URL)

# pull distinct values to build a mapping
df = pd.read_sql(f"SELECT DISTINCT {COL} FROM {TABLE} WHERE {COL} IS NOT NULL", engine)
df["new"] = df[COL].map(expand_abbrevs)
changes = df[df["new"] != df[COL]]

print(f"Found {len(changes)} distinct values to update (out of {len(df)}).")
print(changes.head(15))

if not changes.empty:
    # create VALUES list for a single set-based UPDATE
    values_sql = ",\n".join(
        engine.raw_connection().cursor().mogrify("(%s,%s)", (old, new)).decode()
        for old, new in changes[[COL, "new"]].itertuples(index=False, name=None)
    )

    with engine.begin() as con:
        # optional: keep a one-time backup column
        con.execute(text(f"""
            ALTER TABLE {TABLE}
            ADD COLUMN IF NOT EXISTS {COL}_orig TEXT;
        """))
        con.execute(text(f"""
            UPDATE {TABLE}
            SET {COL}_orig = {COL}
            WHERE {COL}_orig IS NULL;
        """))

        update_sql = f"""
        WITH map(old_val, new_val) AS (VALUES {values_sql})
        UPDATE {TABLE} t
        SET {COL} = map.new_val
        FROM map
        WHERE t.{COL} = map.old_val;
        """
        con.execute(text(update_sql))

    print("plan_name expanded and updated.")
else:
    print("No changes needed.")
