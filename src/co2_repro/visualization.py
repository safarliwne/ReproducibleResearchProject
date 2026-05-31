from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib.ticker import AutoMinorLocator, FuncFormatter, LogLocator, NullFormatter

from src.co2_repro.analysis import RegressionResult


class CO2Visualizer:
    """Generate figures that visually resemble the reference R/ggplot outputs.

    Args:
        output_dir: Directory where PNG files will be saved.
    """

    GGPLOT_COLORS = ["#F8766D", "#A3A500", "#00BF7D", "#00B0F6", "#E76BF3"]

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save(self, fig: plt.Figure, filename: str) -> Path:
        path = self.output_dir / filename
        fig.savefig(path, dpi=160, bbox_inches="tight")
        plt.close(fig)
        return path

    @staticmethod
    def _apply_ggplot_theme(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
        ax.set_title(title, loc="left", fontsize=20, pad=12)
        ax.set_xlabel(xlabel, fontsize=15)
        ax.set_ylabel(ylabel, fontsize=15)
        ax.tick_params(axis="both", labelsize=12, length=0)
        ax.set_facecolor("white")
        ax.grid(True, which="major", color="#e6e6e6", linewidth=1.2)
        ax.grid(True, which="minor", color="#e6e6e6", linewidth=0.6)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():
            spine.set_visible(False)
        try:
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.yaxis.set_minor_locator(AutoMinorLocator())
        except ValueError:
            pass

    @staticmethod
    def _date_axis(ax: plt.Axes) -> None:
        ax.xaxis.set_major_locator(mdates.YearLocator(20))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_minor_locator(mdates.YearLocator(10))

    @staticmethod
    def _scientific_axis(ax: plt.Axes) -> None:
        ticks = [0, 50_000, 100_000]
        ax.set_xticks(ticks)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0e}"))

    def global_average(self, data: pd.DataFrame) -> Path:
        """Save global average CO2 per capita over time."""

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data["date"], data["avg_co2_pc"], color="#228B22", linewidth=1.5)
        self._apply_ggplot_theme(ax, "Global Average CO2 per Capita Over Time", "Date", "t CO2 per Capita")
        self._date_axis(ax)
        return self._save(fig, "co2-1-global-average.png")

    def gdp_vs_co2_loess(self, latest: pd.DataFrame, loess_data: pd.DataFrame) -> Path:
        """Save GDP per capita versus CO2 per capita with a LOWESS curve."""

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(latest["gdp_pc"], latest["co2_pc"], color="black", alpha=0.45, s=32)
        ax.plot(loess_data["gdp_pc"], loess_data["co2_pc_smooth"], color="#8B0000", linewidth=2.6)
        self._apply_ggplot_theme(
            ax,
            "GDP per Capita vs CO2 per Capita (Latest)",
            "GDP per Capita (USD)",
            "t CO2 per Capita",
        )
        self._scientific_axis(ax)
        return self._save(fig, "co2-2-gdp-vs-co2-loess.png")

    def regression_plot(
        self,
        latest: pd.DataFrame,
        regression: RegressionResult,
        prediction_frame: pd.DataFrame,
    ) -> Path:
        """Save GDP regression plot with a blue line and grey confidence band."""

        data = latest[["gdp_pc", "co2_pc"]].dropna()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(data["gdp_pc"], data["co2_pc"], color="black", alpha=0.35, s=32)
        ax.fill_between(
            prediction_frame["gdp_pc"].to_numpy(),
            prediction_frame["mean_ci_lower"].to_numpy(),
            prediction_frame["mean_ci_upper"].to_numpy(),
            color="#BDBDBD",
            alpha=0.7,
            linewidth=0,
        )
        ax.plot(prediction_frame["gdp_pc"], prediction_frame["mean"], color="#0000FF", linewidth=2.8)
        self._apply_ggplot_theme(
            ax,
            "",
            "GDP per Capita (USD)",
            "t CO2 per Capita",
        )
        ax.text(
            0.0,
            1.11,
            "Linear Regression: CO2 per Capita ~ GDP per Capita",
            transform=ax.transAxes,
            fontsize=20,
            ha="left",
            va="bottom",
        )
        ax.text(
            0.0,
            1.05,
            f"R2={regression.r_squared:.2f}; p={regression.p_value:.3g}",
            transform=ax.transAxes,
            fontsize=15,
            ha="left",
            va="bottom",
        )
        self._scientific_axis(ax)
        return self._save(fig, "co2-3-regression.png")

    def top10_per_capita(self, top10: pd.DataFrame) -> Path:
        """Save top 10 countries by latest CO2 per capita."""

        data = top10.sort_values("co2_pc")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(data["country"], data["co2_pc"], color="#483D8B")
        self._apply_ggplot_theme(
            ax,
            "Top 10 Countries by CO2 per Capita (Latest)",
            "t CO2 per Capita",
            "",
        )
        return self._save(fig, "co2-4-top10-per-capita.png")

    def top5_time_series(self, data: pd.DataFrame) -> Path:
        """Save time series for the latest top five CO2-per-capita emitters."""

        fig, ax = plt.subplots(figsize=(10, 6))
        for idx, (country, group) in enumerate(data.groupby("country")):
            color = self.GGPLOT_COLORS[idx % len(self.GGPLOT_COLORS)]
            group = group.sort_values("date")
            ax.plot(group["date"], group["co2_pc"], label=country, color=color, linewidth=1.5)
        self._apply_ggplot_theme(ax, "CO2 per Capita Over Time: Top 5 Countries", "Date", "t CO2 per Capita")
        self._date_axis(ax)
        ax.legend(title="Country", frameon=False, bbox_to_anchor=(1.02, 0.5), loc="center left", fontsize=11, title_fontsize=14)
        return self._save(fig, "co2-5-top5-time-series.png")

    def gdp_quartile_boxplot(self, latest_q: pd.DataFrame) -> Path:
        """Save CO2 per capita boxplot by GDP quartile."""

        groups = [grp["co2_pc"].to_numpy() for _, grp in latest_q.groupby("gdp_q")]
        labels = [str(q) for q in sorted(latest_q["gdp_q"].unique())]
        colors = [cm.viridis(i) for i in np.linspace(0.02, 0.98, len(groups))]
        fig, ax = plt.subplots(figsize=(10, 6))
        box = ax.boxplot(groups, patch_artist=True, showfliers=True, widths=0.75)
        for patch, color in zip(box["boxes"], colors, strict=False):
            patch.set_facecolor(color)
            patch.set_edgecolor("#333333")
            patch.set_linewidth(1.5)
        for element in ["whiskers", "caps", "medians"]:
            for artist in box[element]:
                artist.set_color("#333333")
                artist.set_linewidth(1.5)
        for flier in box["fliers"]:
            flier.set_markerfacecolor("#222222")
            flier.set_markeredgecolor("#222222")
            flier.set_markersize(5)
        ax.set_xticks(np.arange(1, len(labels) + 1), labels)
        self._apply_ggplot_theme(
            ax,
            "CO2 per Capita by GDP per Capita Quartile",
            "GDP Quartile",
            "t CO2 per Capita",
        )
        handles = [plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="#333333") for color in colors]
        ax.legend(handles, labels, title="GDP Quartile", frameon=False, bbox_to_anchor=(1.02, 0.5), loc="center left", fontsize=11, title_fontsize=14)
        return self._save(fig, "co2-6-gdp-quartile-boxplot.png")

    def gdp_quartile_violin(self, latest_q: pd.DataFrame) -> Path:
        """Save CO2 per capita violin plot by GDP quartile."""

        groups = [grp["co2_pc"].to_numpy() for _, grp in latest_q.groupby("gdp_q")]
        labels = [str(q) for q in sorted(latest_q["gdp_q"].unique())]
        colors = [cm.turbo(i) for i in np.linspace(0.02, 0.98, len(groups))]
        fig, ax = plt.subplots(figsize=(10, 6))
        violin = ax.violinplot(groups, showmeans=False, showmedians=False, showextrema=False)
        for body, color in zip(violin["bodies"], colors, strict=False):
            body.set_facecolor(color)
            body.set_edgecolor("#333333")
            body.set_alpha(0.95)
            body.set_linewidth(1.5)
        ax.set_xticks(np.arange(1, len(labels) + 1), labels)
        self._apply_ggplot_theme(
            ax,
            "Distribution of CO2 per Capita by GDP Quartile",
            "GDP Quartile",
            "t CO2 per Capita",
        )
        handles = [plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="#333333") for color in colors]
        ax.legend(handles, labels, title="GDP Quartile", frameon=False, bbox_to_anchor=(1.02, 0.5), loc="center left", fontsize=11, title_fontsize=14)
        return self._save(fig, "co2-7-gdp-quartile-violin.png")

    def quartile_heatmap(self, heat_data: pd.DataFrame) -> Path:
        """Save heatmap of average CO2 per capita by year and GDP quartile."""

        pivot = heat_data.pivot(index="gdp_q", columns="year", values="avg_pc").sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        image = ax.imshow(pivot.to_numpy(), aspect="auto", origin="lower", cmap="viridis")
        years = list(pivot.columns)
        tick_positions = [i for i, year in enumerate(years) if year % 20 == 0]
        if not tick_positions:
            tick_positions = list(np.linspace(0, len(years) - 1, num=min(6, len(years)), dtype=int))
        ax.set_xticks(tick_positions, [str(years[i]) for i in tick_positions])
        ax.set_yticks(np.arange(len(pivot.index)), [str(i) for i in pivot.index])
        self._apply_ggplot_theme(ax, "Avg CO2 per Capita by Year & GDP Quartile", "Year", "GDP Quartile")
        colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.06)
        colorbar.set_label("Avg t CO2 per Capita", fontsize=13)
        colorbar.outline.set_visible(False)
        colorbar.ax.tick_params(labelsize=11, length=0)
        return self._save(fig, "co2-8-quartile-heatmap.png")

    def cumulative_per_capita(self, data: pd.DataFrame) -> Path:
        """Save cumulative sum of CO2 per capita over time."""

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data["date"], data["cum_pc"], color="#A020F0", linewidth=1.6)
        self._apply_ggplot_theme(ax, "Cumulative Sum of CO2 per Capita Over Time", "Date", "Cumulative t CO2 per Capita")
        self._date_axis(ax)
        return self._save(fig, "co2-9-cumulative-per-capita.png")

    def yoy_pct_change(self, data: pd.DataFrame) -> Path:
        """Save year-over-year percentage change chart."""

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(data["date"], data["pct"], color="#FF8C00", linewidth=1.6)
        ax.axhline(0, color="#666666", linewidth=0.8)
        self._apply_ggplot_theme(ax, "Year-over-Year % Change in Global Avg CO2 per Capita", "Date", "% Change")
        self._date_axis(ax)
        return self._save(fig, "co2-10-yoy-pct-change.png")

    def total_vs_per_capita(self, latest: pd.DataFrame, line_data: pd.DataFrame) -> Path:
        """Save total CO2 versus per-capita CO2 with log-scaled x-axis."""

        data = latest[["total_co2", "co2_pc"]].dropna()
        data = data.loc[data["total_co2"] > 0]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(data["total_co2"], data["co2_pc"], color="black", alpha=0.45, s=32)
        ax.plot(line_data["total_co2"], line_data["co2_pc_hat"], color="#006400", linewidth=2.8)
        self._apply_ggplot_theme(
            ax,
            "CO2 per Capita vs Total CO2 Emissions (Latest)",
            "Total CO2 (Mt, log scale)",
            "t CO2 per Capita",
        )
        ax.set_xscale("log")
        ax.xaxis.set_major_locator(LogLocator(base=10, numticks=5))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}" if x >= 1 else f"{x:g}"))
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
        ax.xaxis.set_minor_formatter(NullFormatter())
        return self._save(fig, "co2-11-total-vs-per-capita.png")

    def eu_non_eu(self, data: pd.DataFrame) -> Path:
        """Save EU27 versus non-EU population-weighted CO2 per capita chart."""

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = {"EU27": "#1F77B4", "Non-EU": "#D62728"}
        for region, group in data.groupby("region_group"):
            group = group.sort_values("date")
            ax.plot(group["date"], group["weighted_co2_pc"], label=region, color=colors.get(region), linewidth=1.8)
        self._apply_ggplot_theme(ax, "EU27 vs Non-EU CO2 per Capita Over Time", "Date", "Population-weighted t CO2 per Capita")
        self._date_axis(ax)
        ax.legend(title="Group", frameon=False, bbox_to_anchor=(1.02, 0.5), loc="center left", fontsize=11, title_fontsize=14)
        return self._save(fig, "co2-12-eu-vs-non-eu.png")
