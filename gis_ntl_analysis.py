
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# GIS COURSE PROJECT
# Nighttime Light (NTL), GDP and Population Analysis - India
# Study period: 2000-2025 for GDP and population
#               Up to 2013 for NTL
# ============================================================


# ============================================================
# 1. CONFIGURATION
# ============================================================

# Absolute directory containing this Python script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Input CSV file paths
NTL_FILE = os.path.join(
    BASE_DIR, "NTL_Statistics_upto2013.csv"
)

GDP_FILE = os.path.join(
    BASE_DIR,
    "India_GDP_2000_2025.csv"
)

POPULATION_FILE = os.path.join(
    BASE_DIR,
    "India_Population_2000_2025.csv"
)

# Create output directory beside this script
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Consistent plot style
sns.set_theme(style="whitegrid", context="notebook")


# ============================================================
# 2. LOAD DATA
# ============================================================

def load_data():
    """Load the NTL, GDP and population CSV files."""

    print("Loading datasets...")

    # Check that the required files exist
    for file_path in [NTL_FILE, GDP_FILE, POPULATION_FILE]:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"Required file not found:\n{file_path}"
            )

    # Load NTL data
    ntl_df = pd.read_csv(NTL_FILE)

    # Handle YEAR / Year column naming
    ntl_df.columns = ntl_df.columns.str.strip()

    if "YEAR" in ntl_df.columns:
        ntl_df.rename(columns={"YEAR": "Year"}, inplace=True)

    # Load GDP data
    gdp_df = pd.read_csv(GDP_FILE)
    gdp_df.columns = gdp_df.columns.str.strip()

    # Load population data
    pop_df = pd.read_csv(POPULATION_FILE)
    pop_df.columns = pop_df.columns.str.strip()

    # Check required columns
    if "Year" not in ntl_df.columns:
        raise ValueError(
            f"NTL CSV must contain a Year or YEAR column. "
            f"Found: {list(ntl_df.columns)}"
        )

    if not {"Year", "GDP"}.issubset(gdp_df.columns):
        raise ValueError(
            f"GDP CSV must contain Year and GDP columns. "
            f"Found: {list(gdp_df.columns)}"
        )

    if not {"Year", "Population"}.issubset(pop_df.columns):
        raise ValueError(
            f"Population CSV must contain Year and Population "
            f"columns. Found: {list(pop_df.columns)}"
        )

    if "MEAN NTL" not in ntl_df.columns:
        raise ValueError(
            f"NTL CSV must contain MEAN NTL. "
            f"Found: {list(ntl_df.columns)}"
        )

    # Convert years to a consistent numeric type
    for data in [ntl_df, gdp_df, pop_df]:
        data["Year"] = pd.to_numeric(
            data["Year"], errors="coerce"
        )

        data.dropna(subset=["Year"], inplace=True)
        data["Year"] = data["Year"].astype(int)

    # Convert measurements to numeric values
    for col in ["GDP",]:
        gdp_df[col] = pd.to_numeric(
            gdp_df[col], errors="coerce"
        )

    pop_df["Population"] = pd.to_numeric(
        pop_df["Population"], errors="coerce"
    )

    ntl_numeric_cols = [
        col for col in ["MEAN NTL", "MIN", "MAX", "STD DEV"]
        if col in ntl_df.columns
    ]

    for col in ntl_numeric_cols:
        ntl_df[col] = pd.to_numeric(
            ntl_df[col], errors="coerce"
        )

    print("Datasets loaded successfully.")

    print(f"NTL years: {ntl_df['Year'].min()}-"
          f"{ntl_df['Year'].max()}")

    print(f"GDP years: {gdp_df['Year'].min()}-"
          f"{gdp_df['Year'].max()}")

    print(f"Population years: {pop_df['Year'].min()}-"
          f"{pop_df['Year'].max()}")

    return ntl_df, pop_df, gdp_df


# ============================================================
# 3. MERGE DATASETS
# ============================================================

def merge_data(ntl_df, pop_df, gdp_df):
    """
    Merge GDP, population and NTL datasets on Year.
    GDP and population cover the longer time period.
    NTL values remain missing for years without NTL data.
    """

    print("\nMerging datasets on Year...")

    # Avoid accidental many-to-many merges
    for name, data in [
        ("NTL", ntl_df),
        ("GDP", gdp_df),
        ("Population", pop_df)
    ]:
        if data["Year"].duplicated().any():
            duplicate_years = data.loc[
                data["Year"].duplicated(keep=False), "Year"
            ].unique()

            raise ValueError(
                f"{name} dataset contains duplicate years: "
                f"{duplicate_years.tolist()}"
            )

    # GDP and population
    merged_df = pd.merge(
        gdp_df,
        pop_df,
        on="Year",
        how="inner",
        validate="one_to_one"
    )

    # Add NTL data
    final_df = pd.merge(
        merged_df,
        ntl_df,
        on="Year",
        how="left",
        validate="one_to_one"
    )

    final_df = final_df.sort_values("Year").reset_index(drop=True)

    print(f"Merged dataset contains {len(final_df)} yearly rows.")
    print(f"Years with NTL data: "
          f"{final_df['MEAN NTL'].notna().sum()}")

    return final_df


# ============================================================
# 4. SAVE FIGURES SAFELY
# ============================================================

def save_plot(filename):
    """
    Save the current Matplotlib figure inside outputs/.
    Using an absolute path avoids dependence on the
    current working directory.
    """

    output_path = os.path.join(OUTPUT_DIR, filename)

    plt.tight_layout()
    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        format="png"
    )
    plt.close()

    print(f"Saved: {output_path}")


# ============================================================
# 5. PLOT 1 - NATIONAL TRENDS
# ============================================================

def plot_national_trends(df):
    """
    Plot GDP, population and mean NTL separately.
    Separate panels are used because their units differ.
    """

    print("\nGenerating national trend plots...")

    fig, axes = plt.subplots(
        3, 1,
        figsize=(12, 14),
        sharex=True
    )

    # GDP
    sns.lineplot(
        data=df,
        x="Year",
        y="GDP",
        ax=axes[0],
        marker="o",
        color="blue"
    )

    axes[0].set_title(
        "India GDP Growth (2000-2025)"
    )
    axes[0].set_ylabel("GDP (source units)")
    axes[0].grid(True, alpha=0.3)

    # Population
    sns.lineplot(
        data=df,
        x="Year",
        y="Population",
        ax=axes[1],
        marker="s",
        color="green"
    )

    axes[1].set_title(
        "India Population Growth (2000-2025)"
    )
    axes[1].set_ylabel("Population (persons)")
    axes[1].grid(True, alpha=0.3)

    # NTL
    ntl_data = df.dropna(subset=["MEAN NTL"])

    sns.lineplot(
        data=ntl_data,
        x="Year",
        y="MEAN NTL",
        ax=axes[2],
        marker="^",
        color="darkorange"
    )

    axes[2].set_title(
        "India Mean Nighttime Light Intensity "
        f"({ntl_data['Year'].min()}-"
        f"{ntl_data['Year'].max()})"
        if not ntl_data.empty
        else "India Mean Nighttime Light Intensity"
    )

    axes[2].set_ylabel("Mean NTL")
    axes[2].set_xlabel("Year")
    axes[2].grid(True, alpha=0.3)

    save_plot("National_Trends.png")


# ============================================================
# 6. HELPER - CREATE AN INDEX WITH BASE YEAR = 100
# ============================================================

def create_index(series):
    """
    Convert a time series into an index.
    The first available observation is assigned 100.
    """

    series = pd.to_numeric(series, errors="coerce")

    valid_values = series.dropna()

    if valid_values.empty:
        raise ValueError("Cannot create an index from empty data.")

    base_value = valid_values.iloc[0]

    if base_value == 0:
        raise ValueError(
            "Cannot create an index because the base value is zero."
        )

    return (series / base_value) * 100


def get_ntl_comparison_data(df, comparison_column):
    """
    Retain only years with valid NTL and comparison data.
    Restrict comparisons to the period with available NTL.
    """

    comparison_df = df[
        ["Year", "MEAN NTL", comparison_column]
    ].dropna().copy()

    comparison_df = comparison_df.sort_values("Year")

    if comparison_df.empty:
        raise ValueError(
            f"No overlapping years with valid NTL and "
            f"{comparison_column} data."
        )

    # Avoid misleading indices if the first overlapping
    # year is not 2000.
    first_year = int(comparison_df["Year"].iloc[0])

    if first_year != 2000:
        print(
            f"Warning: First overlapping year is {first_year}, "
            "not 2000. The index will use the first available "
            "overlapping year as its base."
        )

    return comparison_df


# ============================================================
# 7. PLOT 2 - NTL VS GDP INDEXED TREND
# ============================================================

def plot_ntl_gdp_index(df):
    """
    Compare GDP and NTL trends on the same index scale.
    The first overlapping year is set to 100.
    """

    print("\nGenerating NTL vs GDP indexed plot...")

    comparison_df = get_ntl_comparison_data(df, "GDP")

    comparison_df["GDP Index"] = create_index(
        comparison_df["GDP"]
    )

    comparison_df["NTL Index"] = create_index(
        comparison_df["MEAN NTL"]
    )

    plt.figure(figsize=(12, 7))

    plt.plot(
        comparison_df["Year"],
        comparison_df["GDP Index"],
        marker="o",
        linewidth=2,
        label="GDP Index"
    )

    plt.plot(
        comparison_df["Year"],
        comparison_df["NTL Index"],
        marker="^",
        linewidth=2,
        label="Mean NTL Index"
    )

    plt.axhline(
        y=100,
        linestyle="--",
        color="gray",
        alpha=0.7,
        label="Base index = 100"
    )

    plt.title(
        "NTL vs GDP: Indexed Trend for India "
        f"({comparison_df['Year'].min()}-"
        f"{comparison_df['Year'].max()})"
    )

    plt.xlabel("Year")
    plt.ylabel("Index (first overlapping year = 100)")
    plt.xticks(comparison_df["Year"], rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_plot("NTL_GDP_Indexed.png")


# ============================================================
# 8. PLOT 3 - NTL VS POPULATION INDEXED TREND
# ============================================================

def plot_ntl_population_index(df):
    """
    Compare population and NTL trends on the same index scale.
    """

    print("\nGenerating NTL vs population indexed plot...")

    comparison_df = get_ntl_comparison_data(
        df, "Population"
    )

    comparison_df["Population Index"] = create_index(
        comparison_df["Population"]
    )

    comparison_df["NTL Index"] = create_index(
        comparison_df["MEAN NTL"]
    )

    plt.figure(figsize=(12, 7))

    plt.plot(
        comparison_df["Year"],
        comparison_df["Population Index"],
        marker="s",
        linewidth=2,
        label="Population Index"
    )

    plt.plot(
        comparison_df["Year"],
        comparison_df["NTL Index"],
        marker="^",
        linewidth=2,
        label="Mean NTL Index"
    )

    plt.axhline(
        y=100,
        linestyle="--",
        color="gray",
        alpha=0.7,
        label="Base index = 100"
    )

    plt.title(
        "NTL vs Population: Indexed Trend for India "
        f"({comparison_df['Year'].min()}-"
        f"{comparison_df['Year'].max()})"
    )

    plt.xlabel("Year")
    plt.ylabel("Index (first overlapping year = 100)")
    plt.xticks(comparison_df["Year"], rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_plot("NTL_Population_Indexed.png")


# ============================================================
# 9. PLOT 4 - ANNUAL GROWTH RATE COMPARISON
# ============================================================

def plot_growth_rates(df):
    """
    Compare annual percentage changes in NTL, GDP
    and population over years with available NTL data.
    """

    print("\nGenerating annual growth rate comparison...")

    # Use the shared period where all three variables exist
    growth_df = df[
        ["Year", "GDP", "Population", "MEAN NTL"]
    ].dropna().copy()

    growth_df = growth_df.sort_values("Year")

    if len(growth_df) < 2:
        print(
            "Skipping growth comparison: at least two "
            "overlapping years are required."
        )
        return

    # Calculate year-on-year percentage changes
    growth_df["GDP Growth (%)"] = (
        growth_df["GDP"].pct_change() * 100
    )

    growth_df["Population Growth (%)"] = (
        growth_df["Population"].pct_change() * 100
    )

    growth_df["NTL Growth (%)"] = (
        growth_df["MEAN NTL"].pct_change() * 100
    )

    growth_df = growth_df.replace(
        [float("inf"), float("-inf")],
        float("nan")
    ).dropna(
        subset=[
            "GDP Growth (%)",
            "Population Growth (%)",
            "NTL Growth (%)"
        ]
    )

    plt.figure(figsize=(12, 7))

    plt.plot(
        growth_df["Year"],
        growth_df["NTL Growth (%)"],
        marker="^",
        linewidth=2,
        label="NTL Growth"
    )

    plt.plot(
        growth_df["Year"],
        growth_df["GDP Growth (%)"],
        marker="o",
        linewidth=2,
        label="GDP Growth"
    )

    plt.plot(
        growth_df["Year"],
        growth_df["Population Growth (%)"],
        marker="s",
        linewidth=2,
        label="Population Growth"
    )

    plt.axhline(
        y=0,
        linestyle="--",
        color="gray",
        alpha=0.7
    )

    plt.title(
        "Annual Growth Rate Comparison: NTL, GDP "
        "and Population"
    )

    plt.xlabel("Year")
    plt.ylabel("Year-on-year change (%)")
    plt.xticks(growth_df["Year"], rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_plot("Growth_Rate_Comparison.png")


# ============================================================
# 10. MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    try:
        # Load datasets
        ntl_df, pop_df, gdp_df = load_data()

        # Merge datasets
        final_df = merge_data(
            ntl_df,
            pop_df,
            gdp_df
        )

        # Save merged dataset inside outputs/
        merged_path = os.path.join(
            OUTPUT_DIR,
            "Merged_NTL_Socioeconomic_Data.csv"
        )

        final_df.to_csv(
            merged_path,
            index=False
        )

        print(f"\nSaved merged dataset: {merged_path}")

        # Generate visualizations
        plot_national_trends(final_df)
        plot_ntl_gdp_index(final_df)
        plot_ntl_population_index(final_df)
        plot_growth_rates(final_df)

        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print(f"\nAll output files are located in:\n{OUTPUT_DIR}")

        print("\nExpected outputs:")
        print("1. Merged_NTL_Socioeconomic_Data.csv")
        print("2. National_Trends.png")
        print("3. NTL_GDP_Indexed.png")
        print("4. NTL_Population_Indexed.png")
        print("5. Growth_Rate_Comparison.png")

    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"\nERROR: {error}")
        print(
            "\nPlease verify the input CSV paths, column names, "
            "and data values."
        )

    except OSError as error:
        print(f"\nFILE SYSTEM ERROR: {error}")
        print(
            "\nCheck that the outputs folder is writable and "
            "that the output files are not locked by another "
            "application."
        )