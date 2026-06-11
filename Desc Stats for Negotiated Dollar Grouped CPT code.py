import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# ==============================
# 📁 LOAD CPT GROUP FILES
# ==============================
ct_codes = pd.read_csv("CT_code.csv")["cpt_code"].astype(str).str.strip().tolist()
xray_codes = pd.read_csv("XRay_code.csv")["cpt_code"].astype(str).str.strip().tolist()
mri_codes = pd.read_csv("MRI_code.csv")["cpt_code"].astype(str).str.strip().tolist()

# ==============================
# 🔧 DATABASE CONNECTION
# ==============================
conn = psycopg2.connect(
    dbname="MedicalPricing",
    user="postgres",
    password="Siri2000",
    host="localhost"
)

# ==============================
# 🧮 QUERY ALL NEEDED CPT DATA
# ==============================
query = """
SELECT m.cpt_code, "standard_charge|negotiated_dollar" AS negotiated_dollar
FROM medical_charges_cpt AS m
JOIN "CPT_Codes" AS c
  ON m.cpt_code = c.cpt_codes
ORDER BY negotiated_dollar DESC;

"""

df = pd.read_sql(query, conn)
conn.close()

df["cpt_code"] = df["cpt_code"].astype(str).str.strip()
df["negotiated_dollar"] = pd.to_numeric(df["negotiated_dollar"], errors="coerce")
df = df.dropna()

# ==============================
# 🎯 GROUP INTO CT / XRAY / MRI
# ==============================
df["group"] = "OTHER"  # default
df.loc[df["cpt_code"].isin(ct_codes), "group"] = "CT"
df.loc[df["cpt_code"].isin(xray_codes), "group"] = "XRAY"
df.loc[df["cpt_code"].isin(mri_codes), "group"] = "MRI"

# Filter only the three groups
df = df[df["group"].isin(["CT", "XRAY", "MRI"])]

# ==============================
# FUNCTION: COMPUTE STATS
# ==============================
def compute_stats(sub):
    mean_val = sub.mean()
    median_val = sub.median()
    std_val = sub.std()
    skew_val = stats.skew(sub)
    kurt_val = stats.kurtosis(sub)
    return mean_val, median_val, std_val, skew_val, kurt_val

# ==============================
# 📊 PRINT STATISTICS PER GROUP
# ==============================
for grp in ["CT", "XRAY", "MRI"]:
    sub = df[df["group"] == grp]["negotiated_dollar"]

    mean_val, median_val, std_val, skew_val, kurt_val = compute_stats(sub)

    print(f"\n======= {grp} GROUP STATISTICS =======")
    print(f"Count: {len(sub):,}")
    print(f"Mean: ${mean_val:,.2f}")
    print(f"Median: ${median_val:,.2f}")
    print(f"Std Dev: ${std_val:,.2f}")
    print(f"Skewness: {skew_val:.2f}")
    print(f"Kurtosis: {kurt_val:.2f}")

# ==============================
# 📈 LINE CHARTS (3 SEPARATE PLOTS)
# ==============================
for grp in ["CT", "XRAY", "MRI"]:
    sub = df[df["group"] == grp]["negotiated_dollar"].sort_values().reset_index(drop=True)

    plt.figure(figsize=(12, 7))
    plt.plot(sub)
    plt.title(f"{grp} Negotiated Dollar Trend (Sorted)")
    plt.xlabel("Record Index")
    plt.ylabel("Negotiated Dollar ($)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()
