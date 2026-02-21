import pandas as pd


def load_raw_data(path: str) -> pd.DataFrame:
    """Load the raw CO2 dataset."""
    df = pd.read_csv(path, encoding='latin-1')
    return df


if __name__ == "__main__":
    path = "data/raw/CO2 emission by countries.csv"
    df = load_raw_data(path)

    print("Shape:", df.shape)
    print("\nColumns:")
    print(df.columns)
    print("\nPreview:")
    print(df.head())