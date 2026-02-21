import pandas as pd


def load_raw_data(path: str) -> pd.DataFrame:
    """Load the raw CO2 dataset."""
    df = pd.read_csv(path, encoding='latin-1')
    return df


def inspect_data(df: pd.DataFrame) -> None:
    """Print useful inspection info."""
    print("\n=== SHAPE ===")
    print(df.shape)

    print("\n=== COLUMNS ===")
    print(df.columns.tolist())

    print("\n=== DATA TYPES ===")
    print(df.dtypes)

    print("\n=== MISSING VALUES ===")
    print(df.isnull().sum())

    print("\n=== SAMPLE ROWS ===")
    print(df.head())


if __name__ == "__main__":
    path = "data/raw/CO2 emission by countries.csv"
    df = load_raw_data(path)

    inspect_data(df)