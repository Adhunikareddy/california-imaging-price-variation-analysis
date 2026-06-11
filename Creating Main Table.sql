CREATE TABLE medical_charges (
    id SERIAL PRIMARY KEY,

    -- Hospital metadata (from first 2 rows of CSV)
    hospital_name TEXT,
    hospital_location TEXT,
    hospital_address TEXT,

    -- Charge-level data
    description TEXT,
    "code|1" TEXT,
    "code|1|type" TEXT,
    "code|2" TEXT,
    "code|2|type" TEXT,
    "code|3" TEXT,
    "code|3|type" TEXT,
    "code|4" TEXT,
    "code|4|type" TEXT,
    setting TEXT,
    "standard_charge|gross" NUMERIC,
    "standard_charge|discounted_cash" NUMERIC,
    payer_name TEXT,
    plan_name TEXT,
    "standard_charge|negotiated_dollar" NUMERIC,
    "standard_charge|negotiated_percentage" NUMERIC,
    "standard_charge|negotiated_algorithm" TEXT,
    estimated_amount NUMERIC,
    "standard_charge|min" NUMERIC,
    "standard_charge|max" NUMERIC,
    "standard_charge|methodology" TEXT
);

