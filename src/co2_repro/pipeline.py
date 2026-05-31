from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.co2_repro.analysis import CO2Analyzer, RegressionResult
from src.co2_repro.data import CO2DataLoader
from src.co2_repro.visualization import CO2Visualizer


class ReportPipeline:
    """Generate figures, tables, metrics, and markdown for the Quarto report.

    Args:
        data_path: Path to the OWID CO2 CSV.
        output_dir: Directory where generated report assets are written.
    """

    def __init__(self, data_path: str | Path, output_dir: str | Path = "reports/_generated") -> None:
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.figures_dir = self.output_dir / "figures"
        self.tables_dir = self.output_dir / "tables"

    def run(self) -> dict[str, Path]:
        """Run the full analysis and return generated asset paths."""

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)

        prepared = CO2DataLoader(self.data_path).prepare()
        analyzer = CO2Analyzer(prepared)
        visualizer = CO2Visualizer(self.figures_dir)

        global_ts = analyzer.global_time_series()
        latest = analyzer.latest
        top10_pc = analyzer.top_countries_by_per_capita(10)
        top10_total = analyzer.top_countries_by_total(10)
        ts_top5 = analyzer.top5_per_capita_time_series()
        latest_q = analyzer.latest_with_gdp_quartiles()
        quartile_summary = analyzer.gdp_quartile_summary()
        heat_data = analyzer.heatmap_data()
        cumulative = analyzer.cumulative_per_capita_sum()
        pct_change = analyzer.yoy_pct_change()
        eu_ts = analyzer.eu_non_eu_time_series()
        eu_summary = analyzer.latest_eu_non_eu_summary()
        regression = analyzer.regression()
        prediction_frame = analyzer.regression_prediction_frame()
        loess_data = analyzer.loess_latest()
        total_line = analyzer.total_log_regression_line()

        figure_paths = {
            "co2_1_global_average": visualizer.global_average(global_ts),
            "co2_2_gdp_vs_co2_loess": visualizer.gdp_vs_co2_loess(latest, loess_data),
            "co2_3_regression": visualizer.regression_plot(latest, regression, prediction_frame),
            "co2_4_top10_per_capita": visualizer.top10_per_capita(top10_pc),
            "co2_5_top5_time_series": visualizer.top5_time_series(ts_top5),
            "co2_6_gdp_quartile_boxplot": visualizer.gdp_quartile_boxplot(latest_q),
            "co2_7_gdp_quartile_violin": visualizer.gdp_quartile_violin(latest_q),
            "co2_8_quartile_heatmap": visualizer.quartile_heatmap(heat_data),
            "co2_9_cumulative_per_capita": visualizer.cumulative_per_capita(cumulative),
            "co2_10_yoy_pct_change": visualizer.yoy_pct_change(pct_change),
            "co2_11_total_vs_per_capita": visualizer.total_vs_per_capita(latest, total_line),
            "co2_12_eu_vs_non_eu": visualizer.eu_non_eu(eu_ts),
        }

        table_paths = self._write_tables(
            prepared=prepared,
            latest=latest,
            top10_pc=top10_pc,
            top10_total=top10_total,
            quartile_summary=quartile_summary,
            eu_summary=eu_summary,
        )
        metrics_path = self._write_metrics(prepared, latest, regression)
        summary_path = self._write_summary_markdown(
            prepared=prepared,
            latest=latest,
            top10_pc=top10_pc,
            top10_total=top10_total,
            quartile_summary=quartile_summary,
            eu_summary=eu_summary,
            regression=regression,
        )

        return {"summary": summary_path, "metrics": metrics_path, **figure_paths, **table_paths}

    def _write_tables(
        self,
        prepared: pd.DataFrame,
        latest: pd.DataFrame,
        top10_pc: pd.DataFrame,
        top10_total: pd.DataFrame,
        quartile_summary: pd.DataFrame,
        eu_summary: pd.DataFrame,
    ) -> dict[str, Path]:
        table_map = {
            "prepared_sample.csv": prepared.head(25),
            "latest_snapshot.csv": latest,
            "top10_per_capita.csv": top10_pc,
            "top10_total.csv": top10_total,
            "gdp_quartile_summary.csv": quartile_summary,
            "eu_non_eu_summary.csv": eu_summary,
        }
        output_paths: dict[str, Path] = {}
        for filename, dataframe in table_map.items():
            path = self.tables_dir / filename
            dataframe.to_csv(path, index=False)
            output_paths[filename] = path
        return output_paths

    def _write_metrics(self, prepared: pd.DataFrame, latest: pd.DataFrame, regression: RegressionResult) -> Path:
        metrics = {
            "data_path": str(self.data_path),
            "prepared_rows": int(len(prepared)),
            "latest_rows": int(len(latest)),
            "year_min": int(prepared["year"].min()),
            "year_max": int(prepared["year"].max()),
            "regression": asdict(regression),
        }
        path = self.output_dir / "metrics.json"
        path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        return path

    def _write_summary_markdown(
        self,
        prepared: pd.DataFrame,
        latest: pd.DataFrame,
        top10_pc: pd.DataFrame,
        top10_total: pd.DataFrame,
        quartile_summary: pd.DataFrame,
        eu_summary: pd.DataFrame,
        regression: RegressionResult,
    ) -> Path:
        lines = [
            "## Generated data summary",
            "",
            "The Python pipeline uses the same filtering logic as the reference R project:",
            "non-missing CO2 per capita, non-missing GDP, positive population, and years from 1960 onward.",
            "",
            f"- Prepared analytical rows: **{len(prepared):,}**",
            f"- Latest snapshot rows: **{len(latest):,}**",
            f"- Year range after filtering: **{int(prepared['year'].min())}-{int(prepared['year'].max())}**",
            f"- Latest year present in the snapshot: **{int(latest['year'].max())}**",
            "",
            "## Regression reproduction",
            "",
            "The reproduced model is `co2_pc ~ gdp_pc`, fit on the latest observation for each country or region.",
            "",
            f"- Number of observations: **{regression.nobs}**",
            f"- Intercept: **{regression.intercept:.4f}**",
            f"- GDP per capita slope: **{regression.slope:.8f}**",
            f"- R-squared: **{regression.r_squared:.4f}**",
            f"- p-value for GDP per capita: **{regression.p_value:.4g}**",
            "",
            "## Top 10 by latest CO2 per capita",
            "",
            self._to_markdown_table(top10_pc[["country", "year", "co2_pc", "gdp_pc"]]),
            "",
            "## Top 10 by latest total CO2 emissions",
            "",
            self._to_markdown_table(top10_total[["country", "year", "total_co2", "co2_pc"]]),
            "",
            "## GDP quartile summary",
            "",
            self._to_markdown_table(quartile_summary),
            "",
            "## EU27 versus non-EU latest summary",
            "",
            "The EU extension uses country-only rows and population-weighted CO2 per capita for the aggregate comparison.",
            "",
            self._to_markdown_table(eu_summary),
            "",
        ]
        path = self.output_dir / "summary.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    @staticmethod
    def _to_markdown_table(dataframe: pd.DataFrame) -> str:
        formatted = dataframe.copy()
        for column in formatted.select_dtypes(include=["float"]).columns:
            formatted[column] = formatted[column].map(lambda value: f"{value:,.3f}")
        return formatted.to_markdown(index=False)
