"""
Load and validate challenge CSV datasets.

Primary entry point::

    from community_gap.data_loader import load_challenge_data
    data = load_challenge_data("data")

CLI smoke test::

    python -m community_gap.data_loader
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from community_gap import DATA_DIR

# ---------------------------------------------------------------------------
# Required column contracts (filename → columns)
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS: dict[str, list[str]] = {
    "districts.csv": [
        "district",
        "area_type",
        "profile",
        "infrastructure_score",
        "latitude",
        "longitude",
    ],
    "sample_communities.csv": [
        "district",
        "population_estimate",
        "occupancy_rate",
        "service_demand_index",
        "mobility_score",
        "resident_experience_score",
        "optimization_opportunity",
    ],
    "osm_amenities.csv": [
        "district",
        "category",
        "subtype",
        "name",
        "latitude",
        "longitude",
    ],
    "sample_listings.csv": [
        "district",
        "listing_type",
        "property_type",
        "size_sqm",
        "price_aed",
        "price_per_sqm_aed",
        "status",
        "latitude",
        "longitude",
    ],
    "sample_parcels.csv": [
        "district",
    ],
    "sample_transactions.csv": [
        "district",
        "date",
        "transaction_value_aed",
        "price_per_sqm",
    ],
}

# Files always expected in the starter kit (investors is optional).
REQUIRED_FILES = [
    "districts.csv",
    "sample_communities.csv",
    "osm_amenities.csv",
    "sample_listings.csv",
    "sample_parcels.csv",
    "sample_transactions.csv",
]
OPTIONAL_FILES = ["sample_investors.csv"]

# Dict keys returned by load_challenge_data()
FILE_TO_KEY: dict[str, str] = {
    "districts.csv": "districts",
    "sample_communities.csv": "communities",
    "osm_amenities.csv": "amenities",
    "sample_listings.csv": "listings",
    "sample_parcels.csv": "parcels",
    "sample_transactions.csv": "transactions",
    "sample_investors.csv": "investors",
}

# Backward compatibility for scripts/check_community_gap_data.py
CORE_FILES = ["districts.csv", "sample_communities.csv", "osm_amenities.csv"]


class DataValidationError(ValueError):
    """Raised when a dataset fails schema or quality checks."""


@dataclass
class DatasetBundle:
    """Container for all loaded challenge CSVs."""

    districts: pd.DataFrame
    communities: pd.DataFrame
    amenities: pd.DataFrame
    listings: pd.DataFrame | None = None
    parcels: pd.DataFrame | None = None
    transactions: pd.DataFrame | None = None
    investors: pd.DataFrame | None = None


def clean_district_name(value: object) -> object:
    """
    Normalize a district label for joining.

    Trims whitespace and collapses internal runs of spaces.
    Empty results become NA.
    """
    if pd.isna(value):
        return pd.NA
    cleaned = " ".join(str(value).strip().split())
    return cleaned if cleaned else pd.NA


def clean_district_column(df: pd.DataFrame, column: str = "district") -> pd.DataFrame:
    """Return a copy of *df* with cleaned district names in *column*."""
    if column not in df.columns:
        return df.copy()
    out = df.copy()
    out[column] = out[column].map(clean_district_name)
    return out


def standardize_empty_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Replace blank strings with NA in object/string columns."""
    out = df.copy()
    str_cols = out.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        out[col] = out[col].replace(r"^\s*$", pd.NA, regex=True)
    return out


def _validate_columns(path: Path, df: pd.DataFrame, required_columns: list[str]) -> None:
    """Raise ValueError if any required column is missing."""
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"{path.name} is missing required columns: {', '.join(missing)}"
        )


def _load_csv(path: Path, required_columns: list[str]) -> pd.DataFrame:
    """Load one CSV, validate columns, and apply string cleaning."""
    if not path.exists():
        raise ValueError(f"Missing required file: {path}")

    df = pd.read_csv(path)
    _validate_columns(path, df, required_columns)

    if df.empty:
        raise ValueError(f"{path.name} is empty")

    df = standardize_empty_strings(df)
    if "district" in df.columns:
        df = clean_district_column(df)

    return df


def load_challenge_data(data_dir: str | Path = "data") -> dict[str, pd.DataFrame]:
    """
    Load and validate all challenge CSV datasets.

    Parameters
    ----------
    data_dir:
        Path to the folder containing challenge CSVs (default: ``"data"``).

    Returns
    -------
    dict
        Keys: ``districts``, ``communities``, ``amenities``, ``listings``,
        ``parcels``, ``transactions``, and optionally ``investors``.

    Raises
    ------
    ValueError
        If a required file is missing, empty, or lacks required columns.
    """
    root = Path(data_dir)
    if not root.is_dir():
        raise ValueError(f"Data directory does not exist: {root.resolve()}")

    result: dict[str, pd.DataFrame] = {}

    for filename in REQUIRED_FILES:
        path = root / filename
        key = FILE_TO_KEY[filename]
        result[key] = _load_csv(path, REQUIRED_COLUMNS[filename])

    investors_path = root / "sample_investors.csv"
    if investors_path.exists():
        investors = pd.read_csv(investors_path)
        if investors.empty:
            raise ValueError(f"{investors_path.name} is empty")
        investors = standardize_empty_strings(investors)
        if "preferred_district" in investors.columns:
            investors = clean_district_column(investors, "preferred_district")
        result["investors"] = investors

    return result


def load_core_datasets(
    data_dir: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the three core scoring datasets (backward-compatible wrapper)."""
    data = load_challenge_data(data_dir or DATA_DIR)
    return data["districts"], data["communities"], data["amenities"]


def load_all_datasets(data_dir: Path | None = None) -> DatasetBundle:
    """Load all datasets into a :class:`DatasetBundle` (backward-compatible wrapper)."""
    data = load_challenge_data(data_dir or DATA_DIR)
    return DatasetBundle(
        districts=data["districts"],
        communities=data["communities"],
        amenities=data["amenities"],
        listings=data["listings"],
        parcels=data["parcels"],
        transactions=data["transactions"],
        investors=data.get("investors"),
    )


def get_master_districts(districts: pd.DataFrame) -> list[str]:
    """Return sorted canonical district names from districts.csv."""
    return sorted(districts["district"].dropna().unique().tolist())


def _district_count(df: pd.DataFrame, key: str) -> int | str:
    """Count unique districts (or preferred_district for investors)."""
    if "district" in df.columns:
        return int(df["district"].dropna().nunique())
    if key == "investors" and "preferred_district" in df.columns:
        return int(df["preferred_district"].dropna().nunique())
    return "n/a"


def _filename_for_key(key: str) -> str:
    for filename, dict_key in FILE_TO_KEY.items():
        if dict_key == key:
            return filename
    return key


def main() -> None:
    """Print loaded file names, row counts, and district counts."""
    data = load_challenge_data(DATA_DIR)
    print(f"Data directory: {DATA_DIR.resolve()}\n")
    print(f"{'File':<30} {'Key':<15} {'Rows':>8}  {'Districts':>10}")
    print("-" * 68)
    for key, df in data.items():
        filename = _filename_for_key(key)
        rows = len(df)
        districts = _district_count(df, key)
        print(f"{filename:<30} {key:<15} {rows:>8}  {districts:>10}")


if __name__ == "__main__":
    main()
