"""
Feature engineering — district-level aggregations and joins.

Transforms raw CSV rows into one row per district with:
  - community need signals (from sample_communities.csv)
  - OSM amenity counts by category (from osm_amenities.csv)
  - supporting market / feasibility context (listings, parcels, transactions)
"""

from __future__ import annotations

import pandas as pd

from community_gap.data_loader import DatasetBundle

AMENITY_CATEGORIES = [
    "education",
    "healthcare",
    "mobility",
    "retail",
    "community",
    "services",
]


def aggregate_community_features(communities: pd.DataFrame) -> pd.DataFrame:
    """
    Roll community rows up to district level.

    Expected outputs per district:
      - population_estimate (sum)
      - occupancy_rate, mobility_score, resident_experience_score (mean)
      - service_demand_index (population-weighted mean)
      - community_count, top_optimization_opportunity
    """
    raise NotImplementedError(
        "TODO: aggregate_community_features — roll up sample_communities.csv by district"
    )


def count_amenities_by_district(amenities: pd.DataFrame) -> pd.DataFrame:
    """
    Count OSM amenities per district and category.

    Returns one row per district with columns for each category plus total_amenities.
    """
    raise NotImplementedError(
        "TODO: count_amenities_by_district — pivot osm_amenities.csv by district/category"
    )


def build_market_features(
    listings: pd.DataFrame | None,
    transactions: pd.DataFrame | None,
    population_by_district: pd.Series,
) -> pd.DataFrame:
    """
    Build supporting market-pressure features from listings and transactions.

    Should produce per-district listing_count, transaction_count,
    listings_per_10k_residents, avg_price_per_sqm_aed, etc.
  """
    raise NotImplementedError(
        "TODO: build_market_features — district-level listing/transaction aggregates"
    )


def build_feasibility_features(
    parcels: pd.DataFrame | None,
    districts: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build supporting intervention-feasibility features from parcels + infrastructure.

    Should produce vacant_parcel_count, avg_development_potential, etc.
    """
    raise NotImplementedError(
        "TODO: build_feasibility_features — parcel availability by district"
    )


def build_district_feature_table(bundle: DatasetBundle) -> pd.DataFrame:
    """
    Join all feature tables on district.

    This is the main input to :mod:`community_gap.scoring`.

    Returns one row per district with community metrics, amenity counts,
    and supporting context columns.
    """
    raise NotImplementedError(
        "TODO: build_district_feature_table — merge all district-level features"
    )
