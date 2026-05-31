import pandas as pd


def filter_world_data(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only World observations."""
    return df[df["country"] == "World"]


def top_emitters(df: pd.DataFrame, year: int = 2023) -> pd.DataFrame:
    """Top 10 emitters in a selected year."""
    data = df[df["year"] == year]
    return data.nlargest(10, "co2")[["country", "co2"]]
