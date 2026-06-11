# Medical Data for all California Hospital

The focus of this project is analysis of variation in term of negotiated dollar amount for 3 main groups of imaging-related procedure (CT, X-Ray, MRI) from top 10 payers across California.

The project includes files that can be used to successfully preprocess the data for all imaging-related procedure (based on CPT codes) and generate basic statistic for them for further analysis. 

This project is using data provided by [https://github.com/CMSgov/hospital-price-transparency](https://github.com/CMSgov/hospital-price-transparency) which is highly reliable and definition of data can be found from that repository.

## Repository Overview

### **Data Extraction & Standardization**
Scripts that read wide-format hospital pricing files, parse payer/plan columns, and convert them into a standardized tall schema.

### **CPT Code Classification**
Groups CPT codes (CT, X-Ray, MRI, etc.) using external reference lists for segmented analytics.

### **Data Cleaning & Preprocessing**
Handles missing values, type conversion, NaN removal, and outlier detection (IQR).

### **Statistical Analysis**
Computes summary metrics such as mean, median, standard deviation, skewness, and kurtosis.

### **Visualization Tools**
Generates line charts and comparative plots to visualize price distributions and trends.

### **Database Integration**
Connects to PostgreSQL, runs MedicalPricing queries, and loads CPT data for analysis.

### **Batch Processing Utilities**
Processes multiple wide-format hospital files and outputs normalized tall-format datasets.

## File Definition

### Desc stats for negotiated dollar for all CPT codes.py

This file contains the statistical analysis of the Negotiated Dollar amounts, including outlier detection and summary metrics. It also includes the results after applying IQR-based outlier removal and imputation strategies.

### Desc stats for negotiated dollar grouped CPT.py

This script connects to a medical pricing database, retrieves CPT charge data, and groups it into CT, X-Ray, and MRI categories. It then computes summary statistics for each group and visualizes the negotiated dollar trends.

### Conversion from Wide to Tall Code.py

This script converts hospital pricing files from wide format into a standardized tall schema by parsing payer–plan columns and restructuring each charge into individual records. It processes all CSV files in a folder and outputs normalized datasets ready for database loading or analysis.



### Code to Import Data.py
This Python script loads multiple hospital price transparency CSVs into a PostgreSQL table **medical_charges** using `COPY FROM STDIN` (much faster than row-by-row inserts).  
It handles files that have hospital metadata on **row 2** and the charge table header on **row 3**, quotes column names that contain `|`, normalizes missing values, and strips `$`/`,` from numeric-like fields.


### Creating Main Table.sql

This SQL script creates the **medical_charges** table — the foundational dataset for storing hospital price transparency data as required under the **CMS Hospital Price Transparency Rule (45 CFR §180.50)**.  
Each record represents one hospital service or procedure (CPT/DRG/etc.) for a specific payer and plan, with multiple price types such as **gross**, **cash**, and **negotiated** rates.

###  Creating Table with Relevant CPT Codes.sql

This SQL script filters the medical_charges table to create a new subset called medical_charges_CPT, which contains only records where any of the code types are CPT (Current Procedural Terminology) codes.It then removes duplicate entries with multiple CPT codes and adds a new column, cpt_code, that extracts and stores the relevant CPT code for each record — enabling cleaner, CPT-level analysis of hospital pricing data.

### Conversion from Wide to tall Code.py

This Python script converts **wide-format** hospital price transparency CSVs into a **normalized tall format** ready for loading into the `medical_charges` schema.  It parses payer/plan columns (both **bracket** and **pipe** styles), carries forward hospital metadata, and writes only meaningful payer-plan rows.

### Clean payers and plans.py
This script connects to a PostgreSQL database and cleans the payer_name and plan_name columns in the medical_charges_cpt table by removing bracketed numbers, symbols, and extra spaces. It updates the cleaned values back into the database, ensuring consistent, standardized text entries.

### Desc Stats for Negotiated Dollar Grouped CPT code 

This script analyzes and visualizes negotiated dollar rates for CT, X-ray, and MRI medical procedures by pulling CPT code data from a PostgreSQL database. It computes key statistical metrics (mean, median, std, skewness, kurtosis) for each group and plots their value trends using line charts.
 
### Desc Stats for Negotiated Dollar for all CPT codes.py
This script analyzes and visualizes negotiated dollar charges from a PostgreSQL medical pricing database, identifying outliers using the IQR method. It computes key statistics (mean, median, std, skewness, kurtosis) and plots a sorted line chart to reveal overall pricing trends.

### Abbr to full form code.py
Expands common **plan name abbreviations** (e.g., `HMO`, `PPO`, `UHC`) to their full forms in a PostgreSQL table (default: `public.medical_charges_cpt.plan_name`).  
Uses boundary-safe regex so only true tokens are replaced (not substrings), and performs a single **set-based UPDATE** for speed. A backup column `<COL>_orig` is created once.

### Payers Grouping Code.py
Maps raw payer names in PostgreSQL to standardized **payer families** using a CSV lookup table.  
Performs a fast, set-based `UPDATE`, preserves originals in a backup column, and reports any **unmatched** payer names for you to add to the mapping file.



