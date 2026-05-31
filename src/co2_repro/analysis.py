from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.nonparametric.smoothers_lowess import lowess

from src.co2_repro.data import CO2DataLoader


@dataclass(frozen=True)
class RegressionResult:
    """Compact regression result used in figures and the report."""

    intercept: float
    slope: float
    r_squared: float
    p_value: float
    nobs: int
    summary_text: str

    def to_dict(self) -> dict[str, float | int | str]:
        """Return a JSON-serializable dictionary."""

        return asdict(self)


class CO2Analyzer:
    """Compute tables and analytical objects for the CO2 report.

    Args:
        prepared_data: Dataset returned by :class:`CO2DataLoader.prepare`.
    """

    def __init__(self, prepared_data: pd.DataFrame) -> None:
        self.data = prepared_data.copy()
        self.latest = CO2DataLoader.latest_snapshot(self.data)

    def global_time_series(self) -> pd.DataFrame:
        """Compute unweighted average CO2 per capita by year/date."""

        return (
            self.data.groupby("date", as_index=False)["co2_pc"]
            .mean()
            .rename(columns={"co2_pc": "avg_co2_pc"})
            .sort_values("date")
        )

    def top_countries_by_per_capita(self, n: int = 10) -> pd.DataFrame:
        """Return the latest top countries or regions by CO2 per capita."""

        return self.latest.sort_values("co2_pc", ascending=False).head(n).reset_index(drop=True)

    def top_countries_by_total(self, n: int = 10) -> pd.DataFrame:
        """Return the latest top countries or regions by total CO2 emissions."""

        return self.latest.sort_values("total_co2", ascending=False).head(n).reset_index(drop=True)

    def top5_per_capita_time_series(self) -> pd.DataFrame:
        """Return time-series rows for the latest top five per-capita emitters."""

        top5_codes = self.top_countries_by_per_capita(10)["iso_code"].head(5).tolist()
        return self.data.loc[self.data["iso_code"].isin(top5_codes)].sort_values(["country", "date"])

    def latest_with_gdp_quartiles(self) -> pd.DataFrame:
        """Return latest rows with a GDP quartile column."""

        return CO2DataLoader.add_gdp_quartiles(self.latest)

    def gdp_quartile_summary(self) -> pd.DataFrame:
        """Summarize latest CO2 per capita by GDP quartile."""

        latest_q = self.latest_with_gdp_quartiles()
        return (
            latest_q.groupby("gdp_q")
            .agg(
                countries=("country", "count"),
                avg_co2_pc=("co2_pc", "mean"),
                median_co2_pc=("co2_pc", "median"),
                min_gdp_pc=("gdp_pc", "min"),
                max_gdp_pc=("gdp_pc", "max"),
            )
            .reset_index()
        )

    def heatmap_data(self) -> pd.DataFrame:
        """Compute average CO2 per capita by year and latest GDP quartile."""

        latest_q = self.latest_with_gdp_quartiles()[["iso_code", "gdp_q"]]
        joined = self.data.merge(latest_q, on="iso_code", how="inner")
        return (
            joined.groupby(["year", "gdp_q"], as_index=False)["co2_pc"]
            .mean()
            .rename(columns={"co2_pc": "avg_pc"})
            .sort_values(["year", "gdp_q"])
        )

    def cumulative_per_capita_sum(self) -> pd.DataFrame:
        """Compute cumulative sum of annual country-level CO2 per capita values."""

        cumulative = (
            self.data.groupby("date", as_index=False)["co2_pc"]
            .sum()
            .rename(columns={"co2_pc": "sum_pc"})
            .sort_values("date")
        )
        cumulative["cum_pc"] = cumulative["sum_pc"].cumsum()
        return cumulative

    def yoy_pct_change(self) -> pd.DataFrame:
        """Compute year-over-year percentage change of average CO2 per capita."""

        result = self.global_time_series().copy()
        result["pct"] = result["avg_co2_pc"].pct_change() * 100
        return result

    def eu_non_eu_time_series(self) -> pd.DataFrame:
        """Compute population-weighted CO2 per capita for EU27 and non-EU countries."""

        country_data = CO2DataLoader.add_eu_status(CO2DataLoader.country_only(self.data))
        grouped = (
            country_data.groupby(["date", "year", "region_group"], as_index=False)
            .agg(total_co2=("total_co2", "sum"), population=("population", "sum"))
            .sort_values(["region_group", "date"])
        )
        grouped["weighted_co2_pc"] = grouped["total_co2"] * 1_000_000 / grouped["population"]
        return grouped

    def latest_eu_non_eu_summary(self) -> pd.DataFrame:
        """Summarize latest country-only EU27 versus non-EU emissions."""

        country_latest = CO2DataLoader.add_eu_status(CO2DataLoader.country_only(self.latest))
        summary = (
            country_latest.groupby("region_group", as_index=False)
            .agg(
                countries=("country", "count"),
                latest_year=("year", "max"),
                total_co2_mt=("total_co2", "sum"),
                population=("population", "sum"),
                avg_co2_pc=("co2_pc", "mean"),
                median_co2_pc=("co2_pc", "median"),
            )
            .sort_values("region_group")
        )
        summary["weighted_co2_pc"] = summary["total_co2_mt"] * 1_000_000 / summary["population"]
        return summary

    def regression(self) -> RegressionResult:
        """Fit the latest-snapshot linear model `co2_pc ~ gdp_pc`."""

        data = self.latest[["co2_pc", "gdp_pc"]].dropna().copy()
        x = sm.add_constant(data["gdp_pc"])
        y = data["co2_pc"]
        model = sm.OLS(y, x).fit()
        return RegressionResult(
            intercept=float(model.params["const"]),
            slope=float(model.params["gdp_pc"]),
            r_squared=float(model.rsquared),
            p_value=float(model.pvalues["gdp_pc"]),
            nobs=int(model.nobs),
            summary_text=str(model.summary()),
        )

    def regression_prediction_frame(self) -> pd.DataFrame:
        """Return fitted values and confidence interval for the GDP regression."""

        data = self.latest[["co2_pc", "gdp_pc"]].dropna().sort_values("gdp_pc")
        model = sm.OLS(data["co2_pc"], sm.add_constant(data["gdp_pc"])).fit()
        pred = model.get_prediction(sm.add_constant(data["gdp_pc"])).summary_frame(alpha=0.05)
        return pd.DataFrame(
            {
                "gdp_pc": data["gdp_pc"].to_numpy(),
                "mean": pred["mean"].to_numpy(),
                "mean_ci_lower": pred["mean_ci_lower"].to_numpy(),
                "mean_ci_upper": pred["mean_ci_upper"].to_numpy(),
            }
        )

    def loess_latest(self) -> pd.DataFrame:
        """Compute LOWESS smoother for latest GDP per capita versus CO2 per capita."""

        data = self.latest[["gdp_pc", "co2_pc"]].dropna().sort_values("gdp_pc")
        smooth = lowess(endog=data["co2_pc"], exog=data["gdp_pc"], frac=0.3, return_sorted=True)
        return pd.DataFrame(smooth, columns=["gdp_pc", "co2_pc_smooth"])

    def total_log_regression_line(self) -> pd.DataFrame:
        """Fit a line for CO2 per capita against log10 total CO2 emissions.

        The R plot uses a log-scaled x-axis. This method produces a straight line
        on that log axis by modeling CO2 per capita as a function of log10 total
        emissions.
        """

        data = self.latest[["total_co2", "co2_pc"]].dropna()
        data = data.loc[data["total_co2"] > 0].copy()
        x_log = np.log10(data["total_co2"])
        model = sm.OLS(data["co2_pc"], sm.add_constant(x_log)).fit()
        grid = np.linspace(x_log.min(), x_log.max(), 200)
        y_hat = model.predict(sm.add_constant(grid))
        return pd.DataFrame({"total_co2": 10**grid, "co2_pc_hat": y_hat})
