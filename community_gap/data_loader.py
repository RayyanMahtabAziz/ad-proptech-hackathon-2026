"""
Load and validate challenge CSV datasets.

Core inputs (required):
  - data/districts.csv
  - data/sample_communities.csv
  - data/osm_amenities.csv

Supporting inputs (optional but expected in starter kit):
  - data/sample_listings.csv
  - data/sample_parcels.csv
  - data/sample_transactions.csv

Optional:
  - data/sample_investors.csv
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from community_gap import DATA_DIR

# ---------------------------------------------------------------------------
# Required column contracts
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
        "community_id",
        "district",
        "population_estimate",
        "occupancy_rate",
        "service_demand_index",
        "mobility_score",
        "resident_experience_score",
        "optimization_opportunity",
    ],
    "osm_amenities.csv": [
        "amenity_id",
        "category",
        "subtype",
        "district",
        "latitude",
        "longitude",
    ],
    "sample_listings.csv": [
        "listing_id",
        "district",
        "listing_type",
        "price_per_sqm_aed",
        "status",
    ],
    "sample_parcels.csv": [
        "parcel_id",
        "district",
        "land_use",
        "current_status",
        "development_potential_score",
    ],
    "sample_transactions.csv": [
        "transaction_id",
        "district",
        "price_per_sqm",
        "transaction_value_aed",
    ],
}

CORE_FILES = ["districts.csv", "sample_communities.csv", "osm_amenities.csv"]
SUPPORTING_FILES = [
    "sample_listings.csv",
    "sample_parcels.csv",
    "sample_transactions.csv",
]
OPTIONAL_FILES = ["sample_investors.csv"]


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


def clean_district_name(value: str) -> str:
    """
    Normalize a district label for joining.

    Trims whitespace and applies title-case normalization.
    Alias mapping can be added here as new data drops appear.
    """
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def clean_district_column(df: pd.DataFrame, column: str = "district") -> pd.DataFrame:
    """Return a copy of *df* with cleaned district names."""
    out = df.copy()
    out[column] = out[column].map(clean_district_name)
    return out


def _load_csv(path: Path, required_columns: list[str]) -> pd.DataFrame:
    """Load one CSV and validate required columns."""
    if not path.exists():
        raise DataValidationError(f"Missing required file: {path}")

    df = pd.read_csv(path)
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise DataValidationError(
            f"{path.name} is missing required columns: {', '.join(missing)}"
        )
    if df.empty:
        raise DataValidationError(f"{path.name} is empty")

    return df


def load_core_datasets(data_dir: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load the three core scoring datasets.

    Returns
    -------
    districts, communities, amenities
    """
    root = data_dir or DATA_DIR

    districts = _load_csv(root / "districts.csv", REQUIRED_COLUMNS["districts.csv"])
    communities = _load_csv(
        root / "sample_communities.csv", REQUIRED_COLUMNS["sample_communities.csv"]
    )
    amenities = _load_csv(root / "osm_amenities.csv", REQUIRED_COLUMNS["osm_amenities.csv"])

    master = set(districts["district"].map(clean_district_name))
    for name, df in [("communities", communities), ("amenities", amenities)]:
        cleaned = clean_district_column(df)
        unknown = set(cleaned["district"]) - master - {""}
        if unknown:
            raise DataValidationError(
                f"{name}: districts not in districts.csv: {sorted(unknown)}"
            )

    return (
        clean_district_column(districts),
        clean_district_column(communities),
        clean_district_column(amenities),
    )


def load_supporting_datasets(
    data_dir: Path | None = None,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None]:
    """
    Load supporting context datasets.

    Returns None for any file that is missing (logged by caller).
    """
    root = data_dir or DATA_DIR
    results: list[pd.DataFrame | None] = []

    for filename, cols in zip(
        SUPPORTING_FILES,
        [
            REQUIRED_COLUMNS["sample_listings.csv"],
            REQUIRED_COLUMNS["sample_parcels.csv"],
            REQUIRED_COLUMNS["sample_transactions.csv"],
        ],
    ):
        path = root / filename
        if not path.exists():
            results.append(None)
            continue
        results.append(clean_district_column(_load_csv(path, cols)))

    return results[0], results[1], results[2]  # type: ignore[return-value]


def load_all_datasets(data_dir: Path | None = None) -> DatasetBundle:
    """
    Load core + supporting datasets into a :class:`DatasetBundle`.

    Raises :class:`DataValidationError` if core files fail validation.
    """
    districts, communities, amenities = load_core_datasets(data_dir)
    listings, parcels, transactions = load_supporting_datasets(data_dir)

    investors_path = (data_dir or DATA_DIR) / "sample_investors.csv"
    investors = pd.read_csv(investors_path) if investors_path.exists() else None

    return DatasetBundle(
        districts=districts,
        communities=communities,
        amenities=amenities,
        listings=listings,
        parcels=parcels,
        transactions=transactions,
        investors=investors,
    )


def get_master_districts(districts: pd.DataFrame) -> list[str]:
    """Return sorted canonical district names from districts.csv."""
    return sorted(districts["district"].unique().tolist())
