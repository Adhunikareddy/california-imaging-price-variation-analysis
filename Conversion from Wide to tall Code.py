

import os
import csv
import re
import pandas as pd

# --- Schema ---
SCHEMA_COLS = [
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
    "standard_charge|methodology",
]

# --- Helper to parse payer/plan column ---
def parse_col(col):
    if col.startswith("additional_payer_notes") or col.startswith("additional_generic_notes"):
        return None

    # Bracket style
    m = re.match(r"(standard_charge|estimated_amount)\|\[payer_(.*?)\]\|\[plan_(.*?)\](?:\|(.*))?", col)
    if m:
        base, payer, plan, field = m.groups()
        payer, plan = payer.strip(), plan.strip()
        if base == "estimated_amount":
            return payer, plan, "estimated_amount"
        field = (field or "negotiated_dollar").strip().lower()
        return payer, plan, {
            "negotiated_dollar": "standard_charge|negotiated_dollar",
            "negotiated_percentage": "standard_charge|negotiated_percentage",
            "negotiated_algorithm": "standard_charge|negotiated_algorithm",
            "methodology": "standard_charge|methodology",
        }.get(field)

    # Pipe style
    m = re.match(r"(standard_charge|estimated_amount)\|([^|]+)\|([^|]+)(?:\|(.*))?", col)
    if m:
        base, payer, plan, field = m.groups()
        payer, plan = payer.strip(), plan.strip()
        if base == "estimated_amount":
            return payer, plan, "estimated_amount"
        field = (field or "negotiated_dollar").strip().lower()
        return payer, plan, {
            "negotiated_dollar": "standard_charge|negotiated_dollar",
            "negotiated_percentage": "standard_charge|negotiated_percentage",
            "negotiated_algorithm": "standard_charge|negotiated_algorithm",
            "methodology": "standard_charge|methodology",
        }.get(field)

    return None


def convert_wide_to_tall(in_file, out_file):
    print(f"📂 Converting {in_file}")

    # --- Hospital metadata (row 2 = index 1) ---
    try:
        meta = pd.read_csv(in_file, header=None, skiprows=1, nrows=1, encoding="utf-8", on_bad_lines="skip", engine="python")
    except UnicodeDecodeError:
        meta = pd.read_csv(in_file, header=None, skiprows=1, nrows=1, encoding="latin1", on_bad_lines="skip", engine="python")

    hospital_name = meta.iloc[0, 0]
    hospital_location = meta.iloc[0, 3]
    hospital_address = meta.iloc[0, 4]

    # --- Main data (header = row 3) ---
    try:
        df = pd.read_csv(in_file, header=2, encoding="utf-8", on_bad_lines="skip", engine="python")
    except UnicodeDecodeError:
        df = pd.read_csv(in_file, header=2, encoding="latin1", on_bad_lines="skip", engine="python")

    cols = list(df.columns)

    # Identify payer/plan mappings
    payerplan_map = {}
    for c in cols:
        parsed = parse_col(c)
        if parsed:
            payer, plan, dest = parsed
            payerplan_map.setdefault((payer, plan), {})[dest] = c

    print(f"🔎 Found {len(payerplan_map)} payer/plan combos")

    total_written = 0

    # Write tall CSV
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(SCHEMA_COLS)

        for idx, row in enumerate(df.to_dict(orient="records"), 1):
            base = {
                "hospital_name": hospital_name,
                "hospital_location": hospital_location,
                "hospital_address": hospital_address,
                "description": row.get("description"),
                "code|1": row.get("code|1"),
                "code|1|type": row.get("code|1|type"),
                "code|2": row.get("code|2"),
                "code|2|type": row.get("code|2|type"),
                "code|3": row.get("code|3"),
                "code|3|type": row.get("code|3|type"),
                "code|4": row.get("code|4"),
                "code|4|type": row.get("code|4|type"),
                "setting": row.get("setting"),
                "standard_charge|gross": row.get("standard_charge|gross"),
                "standard_charge|discounted_cash": row.get("standard_charge|discounted_cash"),
                "standard_charge|min": row.get("standard_charge|min"),
                "standard_charge|max": row.get("standard_charge|max"),
            }

            for (payer, plan), field_map in payerplan_map.items():
                rec = {c: "" for c in SCHEMA_COLS}
                rec.update(base)
                rec["payer_name"] = payer
                rec["plan_name"] = plan

                has_data = False
                for dest_col, src_col in field_map.items():
                    val = row.get(src_col)
                    if pd.notna(val) and str(val).strip() not in ("", "nan"):
                        rec[dest_col] = val
                        has_data = True

                if has_data:  # only write meaningful rows
                    writer.writerow([rec.get(c, "") for c in SCHEMA_COLS])
                    total_written += 1

            if idx % 1000 == 0:
                print(f"   Processed {idx} rows → wrote {total_written} tall rows so far")

    print(f"✅ Finished {in_file} → {out_file}")
    print(f"   Total tall rows written: {total_written}")


# --- Batch process ---
input_folder = "K:\\health_data_PROJ\\wideonly"
output_folder = "K:\\health_data_PROJ\\wide_converted"
os.makedirs(output_folder, exist_ok=True)

for file in os.listdir(input_folder):
    if file.endswith(".csv"):

        in_path = os.path.join(input_folder, file)
        out_path = os.path.join(output_folder, file.replace(".csv", "_tall.csv"))
        convert_wide_to_tall(in_path, out_path)
