import pandas as pd


def load_raw_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="latin-1")


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to clean snake_case."""
    df = df.rename(columns={
        "Country": "country",
        "Code": "code",
        "Calling Code": "calling_code",
        "Year": "year",
        "CO2 emission (Tons)": "co2_tons",
        "Population(2022)": "population_2022",
        "Area": "area_km2",
        "% of World": "pct_world",
        "Density(km2)": "density_km2"
    })
    return df


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert messy string columns to numeric."""

    # pct_world: remove %
    df["pct_world"] = (
        df["pct_world"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )
    df["pct_world"] = pd.to_numeric(df["pct_world"], errors="coerce")

    # density_km2: remove '/km²'
    df["density_km2"] = (
        df["density_km2"]
        .astype(str)
        .str.replace("/km²", "", regex=False)
    )
    df["density_km2"] = pd.to_numeric(df["density_km2"], errors="coerce")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate country-year rows."""
    df = df.drop_duplicates(subset=["country", "year"])
    return df


def save_processed(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)


if __name__ == "__main__":
    raw_path = "data/raw/CO2 emission by countries.csv"
    output_path = "data/processed/co2_cleaned.csv"

    df = load_raw_data(raw_path)
    df = clean_columns(df)
    df = convert_types(df)
    df = remove_duplicates(df)

    print("Final shape:", df.shape)

    save_processed(df, output_path)