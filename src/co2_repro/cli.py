from __future__ import annotations

import argparse
from pathlib import Path
from urllib.request import urlretrieve

from src.co2_repro.pipeline import ReportPipeline


DEFAULT_OWID_URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"


def build_assets(args: argparse.Namespace) -> None:
    """Generate figures and tables for the report."""

    assets = ReportPipeline(data_path=args.data, output_dir=args.output).run()
    print(f"Generated {len(assets)} assets in {args.output}")


def fetch_data(args: argparse.Namespace) -> None:
    """Download the OWID CO2 dataset."""

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists() and not args.force:
        print(f"Data already exists at {output}. Use --force to overwrite.")
        return

    print(f"Downloading {args.url} -> {output}")
    urlretrieve(args.url, output)
    print(f"Saved {output}")


def make_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""

    parser = argparse.ArgumentParser(description="Reproducible CO2 emissions analysis")
    subparsers = parser.add_subparsers(dest="command", required=True)

    assets_parser = subparsers.add_parser("build-assets", help="generate report assets")
    assets_parser.add_argument("--data", default="data/raw/owid-co2-data.csv", help="path to OWID CSV")
    assets_parser.add_argument("--output", default="reports/_generated", help="asset output directory")
    assets_parser.set_defaults(func=build_assets)

    fetch_parser = subparsers.add_parser("fetch-data", help="download the OWID CO2 dataset")
    fetch_parser.add_argument("--url", default=DEFAULT_OWID_URL, help="dataset URL")
    fetch_parser.add_argument("--output", default="data/raw/owid-co2-data.csv", help="output CSV path")
    fetch_parser.add_argument("--force", action="store_true", help="overwrite existing CSV")
    fetch_parser.set_defaults(func=fetch_data)

    return parser


def main() -> None:
    """Run the command line interface."""

    parser = make_parser()
    args = parser.parse_args()
    args.func(args)