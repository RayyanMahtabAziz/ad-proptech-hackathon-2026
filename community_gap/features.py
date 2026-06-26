"""
Feature engineering — amenity counts and core community/district dataset.

Transforms raw CSV rows into enriched community records with district metadata,
OSM amenity counts, city medians, and percentile ranks.
"""

from __future__ import annotations

import pandas as pd

from community_gap.data_loader import DatasetBundle

AMENITY_CATEGORIES = [
    "education",
    "healthcare",
    "retail",
    "services",
    "community",
    "mobility",
]

AMENITY_COUNT_COLUMNS = AMENITY_CATEGORIES + ["total_amenities", "amenity_diversity_count"]

CITY_MEDIAN_COMMUNITY_COLUMNS = {
    "city_median_service_demand": "service_demand_index",
    "city_median_mobility_score": "mobility_score",
    "city_median_resident_experience_score": "resident_experience_score",
    "city_median_population": "population_estimate",
}

CITY_MEDIAN_AMENITY_COLUMNS = {
    "city_median_education": "education",
    "city_median_healthcare": "healthcare",
    "city_median_retail": "retail",
    "city_median_services": "services",
    "city_median_community": "community",
    "city_median_mobility_amenities": "mobility",
    "city_median_total_amenities": "total_amenities",
}

PERCENTILE_COLUMNS = {
    "population_percentile": "population_estimate",
    "service_demand_percentile": "service_demand_index",
    "mobility_percentile": "mobility_score",
    "resident_experience_percentile": "resident_experience_score",
    "total_amenities_percentile": "total_amenities",
}


def build_amenity_counts(osm_amenities: pd.DataFrame) -> pd.DataFrame:
    """
    Count OSM amenities per district and pivot to one row per district.

    Returns
    -------
    pd.DataFrame
        Columns: district, six category counts, total_amenities,
        amenity_diversity_count.
    """
    counts = (
        osm_amenities.groupby(["district", "category"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=AMENITY_CATEGORIES, fill_value=0)
        .astype(int)
    )

    counts["total_amenities"] = counts[AMENITY_CATEGORIES].sum(axis=1)
    counts["amenity_diversity_count"] = (counts[AMENITY_CATEGORIES] > 0).sum(axis=1).astype(int)

    return counts.reset_index()


def _percentile_rank(series: pd.Series) -> pd.Series:
    """Map values to 0–100 percentile rank across the series."""
    if series.empty:
        return series.astype(float)
    if len(series) == 1:
        return pd.Series([50.0], index=series.index)
    return (series.rank(pct=True) * 100).round(2)


def build_core_dataset(
    communities: pd.DataFrame,
    districts: pd.DataFrame,
    osm_amenities: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge communities with district metadata and amenity counts.

    Returns one row per community record with city median and percentile columns.
    """
    amenity_counts = build_amenity_counts(osm_amenities)

    df = communities.merge(districts, on="district", how="left")
    df = df.merge(amenity_counts, on="district", how="left")

    for col in AMENITY_COUNT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)

    for median_col, source_col in CITY_MEDIAN_COMMUNITY_COLUMNS.items():
        df[median_col] = communities[source_col].median()

    for median_col, source_col in CITY_MEDIAN_AMENITY_COLUMNS.items():
        df[median_col] = amenity_counts[source_col].median()

    for percentile_col, source_col in PERCENTILE_COLUMNS.items():
        df[percentile_col] = _percentile_rank(df[source_col])

    return df


def count_amenities_by_district(amenities: pd.DataFrame) -> pd.DataFrame:
    """Alias for :func:`build_amenity_counts` (backward compatibility)."""
    return build_amenity_counts(amenities)


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
