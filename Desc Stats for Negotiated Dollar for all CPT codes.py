import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

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
# 🧮 QUERY: SAMPLE DATA
# ==============================
query = """
SELECT  "standard_charge|negotiated_dollar" AS negotiated_dollar
FROM medical_charges_cpt AS m
JOIN "CPT_Codes" AS c
  ON m.cpt_code = c.cpt_codes
ORDER BY negotiated_dollar DESC;

"""

df = pd.read_sql(query, conn)
conn.close()

# Convert to numeric just in case, also filled with mean, median, mode are not giving better result.
# So we drop the NA column, which is about 3% of the entire data
print(df["negotiated_dollar"])
df["negotiated_dollar"] = pd.to_numeric(df["negotiated_dollar"], errors="coerce")
df = df.dropna()

mean_val = df["negotiated_dollar"].mean()
median_val = df["negotiated_dollar"].median()
std_val = df["negotiated_dollar"].std()
skew_val = stats.skew(df["negotiated_dollar"])
kurt_val = stats.kurtosis(df["negotiated_dollar"])

# REMOVE outlier
Q1 = df["negotiated_dollar"].quantile(0.25)
Q3 = df["negotiated_dollar"].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print("\n--- IQR Outlier Detection ---")
print(f"Q1: {Q1:,.2f}")
print(f"Q3: {Q3:,.2f}")
print(f"IQR: {IQR:,.2f}")
print(f"Lower Bound: {lower_bound:,.2f}")
print(f"Upper Bound: {upper_bound:,.2f}")

# Identify outliers
outliers = df[(df["negotiated_dollar"] < lower_bound) | (df["negotiated_dollar"] > upper_bound)]

print(f"\nNumber of outliers detected: {len(outliers):,}")
print(f"Percentage of dataset: {100 * len(outliers) / len(df):.2f}%")


# ==============================
# 📊 BASIC STATISTICS
# ==============================
print("AFTER OUTLIER ------------------------\n")
mean_val = df["negotiated_dollar"].mean()
median_val = df["negotiated_dollar"].median()
std_val = df["negotiated_dollar"].std()
skew_val = stats.skew(df["negotiated_dollar"])
kurt_val = stats.kurtosis(df["negotiated_dollar"])

print("\n--- Negotiated Dollar Summary ---")
print(f"Mean:   ${mean_val:,.2f}")
print(f"Median: ${median_val:,.2f}")
print(f"Std:    ${std_val:,.2f}")
print(f"Skewness: {skew_val:.2f}")
print(f"Kurtosis: {kurt_val:.2f}")

# ==============================
# 📈 VISUALIZATION
# ==============================
# Sort values to create a smooth line plot
sorted_vals = df["negotiated_dollar"].sort_values().reset_index(drop=True)

plt.figure(figsize=(14, 8))
plt.plot(sorted_vals)
plt.title("Line Chart of Negotiated Dollar Values (Sorted)")
plt.xlabel("Record Index (sorted by value)")
plt.ylabel("Negotiated Dollar ($)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()