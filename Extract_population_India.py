import pandas as pd
import os

# ============================================================
# SETTINGS
# ============================================================

# Name of the downloaded World Bank CSV
INPUT_FILE = "API_SP.POP.TOTL_DS2_en_csv_v2_*.csv"

# Output file
OUTPUT_FILE = "India_Population_2000_2025.csv"


# ============================================================
# FIND THE WORLD BANK CSV
# ============================================================

import glob

files = glob.glob(INPUT_FILE)

if not files:
    raise FileNotFoundError(
        "World Bank population CSV not found in the same folder as this script."
    )

input_file = files[0]

print("Reading:", input_file)


# ============================================================
# READ DATA
# ============================================================

# World Bank CSVs usually have 4 metadata rows before the actual table
df = pd.read_csv(input_file, skiprows=4)

print("Columns found:")
print(df.columns.tolist())


# ============================================================
# EXTRACT INDIA
# ============================================================

india = df[df["Country Code"] == "IND"].copy()


# ============================================================
# SELECT YEARS
# ============================================================

years = list(range(2000, 2026))

population_data = india[["Country Name", "Country Code"] + [str(y) for y in years]].copy()


# ============================================================
# CONVERT FROM WIDE FORMAT TO LONG FORMAT
# ============================================================

population_data = population_data.melt(
    id_vars=["Country Name", "Country Code"],
    var_name="Year",
    value_name="Population"
)

population_data["Year"] = population_data["Year"].astype(int)


# ============================================================
# REMOVE MISSING VALUES
# ============================================================

population_data = population_data.dropna(subset=["Population"])


# ============================================================
# CALCULATE POPULATION INDEX
# ============================================================

population_2000 = population_data.loc[
    population_data["Year"] == 2000, "Population"
].iloc[0]

population_data["Population_Index"] = (
    population_data["Population"] / population_2000
) * 100


# ============================================================
# ROUND VALUES
# ============================================================

population_data["Population"] = population_data["Population"].astype(int)

population_data["Population_Index"] = population_data[
    "Population_Index"
].round(2)


# ============================================================
# KEEP ONLY REQUIRED COLUMNS
# ============================================================

population_data = population_data[
    ["Year", "Population", "Population_Index"]
]


# ============================================================
# SAVE OUTPUT
# ============================================================

output_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    OUTPUT_FILE
)

population_data.to_csv(output_path, index=False)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\nPopulation data extracted successfully!")
print("\nPopulation in 2000:", population_2000)

print("\nFinal dataset:")
print(population_data.to_string(index=False))

print("\nSaved to:")
print(output_path)