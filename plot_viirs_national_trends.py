"""
India VIIRS Nighttime Lights + GDP + Population plotting script
-------------------------------------------------------------
Creates:
1. NTL vs Population (indexed trends, common VIIRS years)
2. NTL vs GDP (indexed trends, common VIIRS years)
3. Annual growth rate comparison: Mean NTL, GDP, Population
4. National trends (separate panels for NTL, GDP, Population)

Expected input files:
- VIIRS_2014-2025.csv
- India_GDP_2000_2025.csv
- India_Population_2000_2025.csv

Optional historical NTL file:
- NTL_Statistics_upto2013.csv
  If present, it is combined with VIIRS so the NTL national trend can span
  2000–2025. The comparisons are still restricted to the years available
  in the VIIRS file (2014–2025).

Edit the file paths in the CONFIG section if your files are in another folder.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------- CONFIG ---------------------------------
# VIIRS is set to the uploaded file location. Change if you move it.
VIIRS_FILE = Path("./VIIRS_2014-2025.csv")

# These match the paths used in your earlier analysis. Adjust if needed.
GDP_FILE = Path("./India_GDP_2000_2025.csv")
POPULATION_FILE = Path("./India_Population_2000_2025.csv")

# Optional; used only to extend the NTL national trend before 2014.
HISTORICAL_NTL_FILE = Path("./NTL_Statistics_upto2013.csv")

OUTPUT_DIR = Path("./VIIRS_Plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_YEAR = 2014  # Index base year for comparisons over VIIRS period
# ------------------------------------------------------------------------


def find_column(df, candidates, required=True, label="column"):
    """Find a column by case-insensitive exact match from candidate names."""
    lookup = {str(col).strip().lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    if required:
        raise ValueError(
            f"Could not find {label}. Tried {candidates}. "
            f"Available columns: {list(df.columns)}"
        )
    return None


def clean_numeric(series):
    """Convert values such as '5,352.76' to numeric."""
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce"
    )


def load_viirs():
    df = pd.read_csv(VIIRS_FILE)
    year_col = find_column(df, ["Year", "YEAR"], label="VIIRS year")
    mean_col = find_column(
        df, ["Mean", "MEAN", "Mean NTL", "MEAN NTL", "Mean Radiance"],
        label="VIIRS mean NTL"
    )

    viirs = df[[year_col, mean_col]].copy()
    viirs.columns = ["Year", "Mean_NTL"]
    viirs["Year"] = clean_numeric(viirs["Year"]).astype("Int64")
    viirs["Mean_NTL"] = clean_numeric(viirs["Mean_NTL"])
    viirs = viirs.dropna(subset=["Year", "Mean_NTL"])
    viirs["Year"] = viirs["Year"].astype(int)
    viirs = viirs.groupby("Year", as_index=False)["Mean_NTL"].mean()
    return viirs


def load_historical_ntl():
    """Load pre-VIIRS NTL data if the optional file exists."""
    if not HISTORICAL_NTL_FILE.exists():
        print(f"Optional historical NTL file not found: {HISTORICAL_NTL_FILE}")
        print("The national NTL trend will use VIIRS years only.")
        return pd.DataFrame(columns=["Year", "Mean_NTL"])

    df = pd.read_csv(HISTORICAL_NTL_FILE)
    year_col = find_column(df, ["Year", "YEAR"], label="historical NTL year")
    mean_col = find_column(
        df, ["Mean NTL", "MEAN NTL", "Mean", "MEAN", "Mean Radiance"],
        label="historical mean NTL"
    )

    historical = df[[year_col, mean_col]].copy()
    historical.columns = ["Year", "Mean_NTL"]
    historical["Year"] = clean_numeric(historical["Year"]).astype("Int64")
    historical["Mean_NTL"] = clean_numeric(historical["Mean_NTL"])
    historical = historical.dropna(subset=["Year", "Mean_NTL"])
    historical["Year"] = historical["Year"].astype(int)
    historical = historical[historical["Year"] < int(viirs_year_min)]
    historical = historical.groupby("Year", as_index=False)["Mean_NTL"].mean()
    return historical


def load_world_bank_series(file_path, value_candidates, output_name):
    """Load GDP/population CSV and return normalized Year + requested value."""
    df = pd.read_csv(file_path)
    year_col = find_column(df, ["Year", "YEAR"], label=f"{output_name} year")
    value_col = find_column(df, value_candidates, label=output_name)

    result = df[[year_col, value_col]].copy()
    result.columns = ["Year", output_name]
    result["Year"] = clean_numeric(result["Year"]).astype("Int64")
    result[output_name] = clean_numeric(result[output_name])
    result = result.dropna(subset=["Year", output_name])
    result["Year"] = result["Year"].astype(int)
    result = result.groupby("Year", as_index=False)[output_name].mean()
    return result


def indexed_to_base(series, base_year):
    """Return index with base year = 100; values before/after are relative."""
    base_rows = series.loc[series["Year"] == base_year, series.columns[1]]
    if base_rows.empty or pd.isna(base_rows.iloc[0]) or base_rows.iloc[0] == 0:
        raise ValueError(
            f"Cannot calculate index: base year {base_year} missing or zero "
            f"for column {series.columns[1]}."
        )
    value_col = series.columns[1]
    result = series.copy()
    result[value_col] = result[value_col] / base_rows.iloc[0] * 100
    return result


def save_plot(filename):
    path = OUTPUT_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_ntl_vs_population(common):
    """Indexed Mean NTL and population for common VIIRS years."""
    ntl_idx = indexed_to_base(common[["Year", "Mean_NTL"]], BASE_YEAR)
    pop_idx = indexed_to_base(common[["Year", "Population"]], BASE_YEAR)

    plt.figure(figsize=(10, 6))
    plt.plot(ntl_idx["Year"], ntl_idx["Mean_NTL"], marker="o", label="Mean NTL Index")
    plt.plot(pop_idx["Year"], pop_idx["Population"], marker="s", label="Population Index")
    plt.axhline(100, linestyle="--", linewidth=1)
    plt.title(f"NTL vs Population: Indexed Trend for India ({BASE_YEAR}–{common['Year'].max()})")
    plt.xlabel("Year")
    plt.ylabel(f"Index ({BASE_YEAR} = 100)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    save_plot("NTL_vs_Population.png")


def plot_ntl_vs_gdp(common):
    """Indexed Mean NTL and GDP for common VIIRS years."""
    ntl_idx = indexed_to_base(common[["Year", "Mean_NTL"]], BASE_YEAR)
    gdp_idx = indexed_to_base(common[["Year", "GDP"]], BASE_YEAR)

    plt.figure(figsize=(10, 6))
    plt.plot(ntl_idx["Year"], ntl_idx["Mean_NTL"], marker="o", label="Mean NTL Index")
    plt.plot(gdp_idx["Year"], gdp_idx["GDP"], marker="s", label="GDP Index")
    plt.axhline(100, linestyle="--", linewidth=1)
    plt.title(f"NTL vs GDP: Indexed Trend for India ({BASE_YEAR}–{common['Year'].max()})")
    plt.xlabel("Year")
    plt.ylabel(f"Index ({BASE_YEAR} = 100)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    save_plot("NTL_vs_GDP.png")


def plot_annual_growth(common):
    """Annual percentage growth rates for the three series."""
    growth = common[["Year", "Mean_NTL", "GDP", "Population"]].copy()
    for col in ["Mean_NTL", "GDP", "Population"]:
        growth[col] = growth[col].pct_change() * 100

    plt.figure(figsize=(11, 6))
    plt.plot(growth["Year"], growth["Mean_NTL"], marker="o", label="Mean NTL Growth")
    plt.plot(growth["Year"], growth["GDP"], marker="s", label="GDP Growth")
    plt.plot(growth["Year"], growth["Population"], marker="^", label="Population Growth")
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title("Annual Growth Rate Comparison: India (VIIRS Period)")
    plt.xlabel("Year")
    plt.ylabel("Annual Growth Rate (%)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    save_plot("Annual_Growth_Rate_Comparison.png")


def plot_national_trends(all_ntl, gdp, population):
    """
    Make a 3-panel figure showing national levels over time.
    NTL may span 2000–2025 if historical NTL is available; GDP/population
    show all years in their respective files.
    """
    fig, axes = plt.subplots(3, 1, figsize=(11, 12))

    axes[0].plot(all_ntl["Year"], all_ntl["Mean_NTL"], marker="o")
    axes[0].set_title("India Mean Nighttime Light Intensity")
    axes[0].set_ylabel("Mean NTL")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(gdp["Year"], gdp["GDP"], marker="o")
    axes[1].set_title("India GDP")
    axes[1].set_ylabel("GDP (constant 2015 US$)")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(population["Year"], population["Population"], marker="o")
    axes[2].set_title("India Population")
    axes[2].set_ylabel("Population")
    axes[2].set_xlabel("Year")
    axes[2].grid(True, alpha=0.3)

    fig.suptitle("National Trends: India", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    path = OUTPUT_DIR / "National_Trends.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def main():
    global viirs_year_min

    viirs = load_viirs()
    if viirs.empty:
        raise ValueError("No usable VIIRS rows found.")
    viirs_year_min = int(viirs["Year"].min())

    gdp = load_world_bank_series(
        GDP_FILE,
        ["GDP", "GDP (constant 2015 US$)", "GDP (constant 2015 USD)",
         "NY.GDP.MKTP.KD", "Value"],
        "GDP"
    )
    population = load_world_bank_series(
        POPULATION_FILE,
        ["Population", "Total Population", "SP.POP.TOTL", "Value"],
        "Population"
    )

    # Merge all series by year; comparisons use only years with all 3 values.
    merged = pd.merge(viirs, gdp, on="Year", how="inner")
    merged = pd.merge(merged, population, on="Year", how="inner")
    common = merged.dropna(subset=["Mean_NTL", "GDP", "Population"]).sort_values("Year")

    if common.empty:
        raise ValueError(
            "No overlapping years among VIIRS, GDP, and population. "
            "Check that all files use the same year range and columns."
        )
    if BASE_YEAR not in common["Year"].values:
        raise ValueError(
            f"Base year {BASE_YEAR} is not present in the common data. "
            f"Available common years: {common['Year'].tolist()}"
        )

    historical_ntl = load_historical_ntl()
    all_ntl = pd.concat([historical_ntl, viirs], ignore_index=True)
    all_ntl = all_ntl.drop_duplicates(subset=["Year"], keep="last").sort_values("Year")

    print("\nCommon comparison years:", common["Year"].min(), "to", common["Year"].max())
    print("Number of common years:", len(common))
    print("NTL years in national trend:", all_ntl["Year"].min(), "to", all_ntl["Year"].max())

    plot_ntl_vs_population(common)
    plot_ntl_vs_gdp(common)
    plot_annual_growth(common)
    plot_national_trends(all_ntl, gdp, population)

    # Also save the aligned data used for plotting.
    common.to_csv(OUTPUT_DIR / "VIIRS_GDP_Population_Aligned.csv", index=False)
    print(f"Saved: {OUTPUT_DIR / 'VIIRS_GDP_Population_Aligned.csv'}")
    print("\nAll plots completed.")


if __name__ == "__main__":
    main()
