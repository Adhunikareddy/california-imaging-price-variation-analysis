# using COPY instead of INSERT for faster bulk insert
import os
import io
import pandas as pd
import psycopg2

# Connect to DB
conn = psycopg2.connect(
    dbname="MedicalPricing",
    user="postgres",
    password="Siri2000",
    host="localhost"
)
cur = conn.cursor()                                              

folder_path = r"C:\Users\sp599936\Downloads\new tall files"

schema_cols = [                                           
    "hospital_name",
    "hospital_location",
    "hospital_address",
    "description",
    "code|1",
    "code|1|type",
    "code|2",
    "code|2|type",
    "code|3",
    "code|3|type",
    "code|4",
    "code|4|type",
    "setting",
    "standard_charge|gross",
    "standard_charge|discounted_cash",
    "payer_name",
    "plan_name",
    "standard_charge|negotiated_dollar",
    "standard_charge|negotiated_percentage",
    "standard_charge|negotiated_algorithm",
    "estimated_amount",
    "standard_charge|min",
    "standard_charge|max",
    "standard_charge|methodology"
]

# Quote column names that contain pipes
quoted_cols = ', '.join([f'"{c}"' for c in schema_cols])

for file in os.listdir(folder_path):
    if not file.endswith(".csv"):
        continue

    file_path = os.path.join(folder_path, file)
    print(f"Importing (COPY) {file}")

    try:
        # --- Hospital metadata (row 2 = index 1) ---
        try:
            meta = pd.read_csv(file_path, header=None, skiprows=1, nrows=1, encoding="utf-8")
        except UnicodeDecodeError:
            meta = pd.read_csv(file_path, header=None, skiprows=1, nrows=1, encoding="latin1")

        hospital_name = meta.iloc[0, 0]
        hospital_location = meta.iloc[0, 3]
        hospital_address = meta.iloc[0, 4]

        # --- Charges: row 3 is header (index 2) ---
        try:
            df = pd.read_csv(file_path, header=2, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, header=2, encoding="latin1")

        # keep only needed columns & match order
        # if a column is missing, create it with None
        for col in schema_cols[3:]:
            if col not in df.columns:
                df[col] = None

        # prepend the 3 metadata columns
        df_out = pd.DataFrame({
            "hospital_name": hospital_name,
            "hospital_location": hospital_location,
            "hospital_address": hospital_address
        }, index=df.index)

        df_out = pd.concat([df_out, df[schema_cols[3:]]], axis=1)

        # Normalize NaN -> empty (COPY with NULL '')
        df_out = df_out.where(pd.notnull(df_out), '')

        # (Optional) Clean numeric-like strings (remove $ and commas)
        num_cols = [
            "standard_charge|gross",
            "standard_charge|discounted_cash",
            "standard_charge|negotiated_dollar",
            "standard_charge|negotiated_percentage",
            "estimated_amount",
            "standard_charge|min",
            "standard_charge|max",
        ]
        for c in num_cols:
            if c in df_out.columns:
                df_out[c] = (
                    df_out[c]
                    .astype(str)
                    .str.replace(r'[\$,]', '', regex=True)
                    .replace({'': None})
                )

        # Send to PostgreSQL via COPY FROM STDIN
        buf = io.StringIO()
        df_out.to_csv(buf, index=False, header=False)  # no header
        buf.seek(0)

        cur.execute("SET LOCAL synchronous_commit TO OFF;")
        copy_sql = f"""
            COPY medical_charges ({quoted_cols})
            FROM STDIN WITH (FORMAT CSV, NULL '', QUOTE '"', ESCAPE '"');
        """
        cur.copy_expert(copy_sql, buf)
        conn.commit()
        print(f"Finished (COPY) {file}: {len(df_out)} rows")

    except Exception as e:
        conn.rollback()
        print(f"Error importing {file}: {e}")

cur.close()
conn.close()