import pandas as pd


def load_data(filepath="data/raw/owid-co2-data.csv"):
    """Load the OWID CO2 dataset."""
    return pd.read_csv(filepath)


if __name__ == "__main__":
    df = load_data()
    print(df.head())
    print(df.columns)
