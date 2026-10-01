import pandas as pd
import os

# ============================================================
# USER INPUT
# ============================================================

# Specify the path to the input World Bank CSV file
input_csv = r"C:\Users\cs3006tx\Downloads\API_NY.GDP.MKTP.KD_DS2_en_csv_v2_34247\API_NY.GDP.MKTP.KD_DS2_en_csv_v2_34247.csv"


# ============================================================
# OUTPUT PATH
# ============================================================

# Get the directory where this Python script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Output CSV will be saved in the same directory as this script
output_csv = os.path.join(
    script_directory,
    "India_GDP_2000_2025.csv"
)


# ============================================================
# READ WORLD BANK DATA
# ============================================================

# World Bank CSV contains metadata rows before the actual table
df = pd.read_csv(input_csv, skiprows=4)


# ============================================================
# SELECT INDIA
# ============================================================

india = df[df["Country Code"] == "IND"].copy()


# ============================================================
# SELECT YEARS 2000–2025
# ============================================================

years = [str(year) for year in range(2000, 2026)]


# ============================================================
# CONVERT WIDE FORMAT → YEAR-GDP FORMAT
# ============================================================

india_gdp = india[years].T.reset_index()

# Rename columns
india_gdp.columns = ["Year", "GDP"]


# ============================================================
# CLEAN DATA TYPES
# ============================================================

india_gdp["Year"] = india_gdp["Year"].astype(int)

india_gdp["GDP"] = pd.to_numeric(
    india_gdp["GDP"],
    errors="coerce"
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\nIndia GDP (2000–2025)")
print("-" * 40)
print(india_gdp.to_string(index=False))


# ============================================================
# SAVE OUTPUT
# ============================================================

india_gdp.to_csv(
    output_csv,
    index=False
)

print("\n" + "-" * 40)
print("GDP data successfully extracted!")
print(f"Output saved to:")
print(output_csv)