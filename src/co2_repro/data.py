from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CO2DataLoader:
    """Load and prepare the Our World in Data CO2 dataset.

    The filtering logic mirrors the reference R project:
    keep rows with available CO2 per capita, available GDP, positive population,
    and years from 1960 onward. The class also retains population so the project
    can add an EU27 versus non-EU extension.
    """

    source: str | Path

    REQUIRED_COLUMNS: ClassVar[set[str]] = {
        "country",
        "year",
        "iso_code",
        "population",
        "gdp",
        "co2",
        "co2_per_capita",
    }

    EU27_ISO_CODES: ClassVar[set[str]] = {
        "AUT",
        "BEL",
        "BGR",
        "HRV",
        "CYP",
        "CZE",
        "DNK",
        "EST",
        "FIN",
        "FRA",
        "DEU",
        "GRC",
        "HUN",
        "IRL",
        "ITA",
        "LVA",
        "LTU",
        "LUX",
        "MLT",
        "NLD",
        "POL",
        "PRT",
        "ROU",
        "SVK",
        "SVN",
        "ESP",
        "SWE",
    }

    def load_raw(self) -> pd.DataFrame:
        """Read the raw OWID CSV file or URL.

        Returns:
            Raw dataframe.

        Raises:
            ValueError: If required columns are missing.
        """

        data = pd.read_csv(self.source)
        missing = self.REQUIRED_COLUMNS.difference(data.columns)
        if missing:
            raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
        return data

    def prepare(self) -> pd.DataFrame:
        """Prepare the analytical dataset.

        Returns:
            Dataframe with `country`, `iso_code`, `date`, `year`, `co2_pc`,
            `total_co2`, `gdp_pc`, and `population`.
        """

        raw = self.load_raw()
        filtered = raw.loc[
            raw["co2_per_capita"].notna()
            & raw["gdp"].notna()
            & raw["population"].gt(0)
            & raw["year"].ge(1960),
            ["country", "iso_code", "year", "population", "co2_per_capita", "co2", "gdp"],
        ].copy()

        filtered["date"] = pd.to_datetime(filtered["year"].astype(str) + "-01-01")
        filtered["co2_pc"] = filtered["co2_per_capita"]
        filtered["total_co2"] = filtered["co2"]
        filtered["gdp_pc"] = filtered["gdp"] / filtered["population"]

        return filtered[
            ["country", "iso_code", "date", "year", "co2_pc", "total_co2", "gdp_pc", "population"]
        ].reset_index(drop=True)

    @staticmethod
    def latest_snapshot(data: pd.DataFrame) -> pd.DataFrame:
        """Return the latest observation for each `(iso_code, country)` pair."""

        return (
            data.sort_values(["iso_code", "country", "year"], na_position="last")
            .groupby(["iso_code", "country"], dropna=False, as_index=False)
            .tail(1)
            .reset_index(drop=True)
        )

    @staticmethod
    def country_only(data: pd.DataFrame) -> pd.DataFrame:
        """Keep only standard three-letter ISO country-code rows.

        OWID also contains aggregates such as World or regional groups. These are
        useful for reproducing some R charts, but EU versus non-EU comparisons
        should use country rows only.
        """

        mask = data["iso_code"].astype(str).str.fullmatch(r"[A-Z]{3}", na=False)
        return data.loc[mask].copy()

    @classmethod
    def add_eu_status(cls, data: pd.DataFrame) -> pd.DataFrame:
        """Add a `region_group` column with EU27 or Non-EU labels."""

        result = data.copy()
        result["region_group"] = np.where(result["iso_code"].isin(cls.EU27_ISO_CODES), "EU27", "Non-EU")
        return result

    @staticmethod
    def add_gdp_quartiles(latest: pd.DataFrame, n: int = 4) -> pd.DataFrame:
        """Add GDP-per-capita ntiles similar to `dplyr::ntile` in R."""

        result = latest.copy()
        if result.empty:
            result["gdp_q"] = pd.Series(dtype="int64")
            return result
        ranks = result["gdp_pc"].rank(method="first")
        result["gdp_q"] = np.floor((ranks - 1) * n / len(result)).astype(int) + 1
        return result

