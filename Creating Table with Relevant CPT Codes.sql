CREATE TABLE medical_charges_CPT AS
SELECT *
FROM medical_charges
WHERE "code|1|type" = 'CPT'
   OR "code|2|type" = 'CPT'
   OR "code|3|type" = 'CPT'
   OR "code|4|type" = 'CPT';


DELETE FROM medical_charges_cpt
WHERE (
    (CASE WHEN "code|1|type" = 'CPT' THEN 1 ELSE 0 END) +
    (CASE WHEN "code|2|type" = 'CPT' THEN 1 ELSE 0 END) +
    (CASE WHEN "code|3|type" = 'CPT' THEN 1 ELSE 0 END)
) > 1;

ALTER TABLE medical_charges_cpt ADD COLUMN cpt_code TEXT;

UPDATE medical_charges_cpt
SET cpt_code = CASE
    WHEN "code|1|type" = 'CPT' THEN "code|1"
    WHEN "code|2|type" = 'CPT' THEN "code|2"
    WHEN "code|3|type" = 'CPT' THEN "code|3"
    ELSE NULL
END;

