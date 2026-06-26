"""
Evidence generation and intervention recommendations.

Produces human-readable evidence bullets and recommended intervention
categories — all derived from computed scores and raw metrics.
"""

from __future__ import annotations

import pandas as pd


def build_city_medians(scored: pd.DataFrame) -> dict[str, float]:
    """Return city-wide median values for key comparison metrics."""
    raise NotImplementedError("TODO: build_city_medians")


def generate_evidence_bullets(
    row: pd.Series,
    city_medians: dict[str, float],
) -> list[str]:
    """
    Build deterministic evidence bullets for one district.

    Each bullet must cite a visible metric (OSM count, index value, score).
    """
    raise NotImplementedError("TODO: generate_evidence_bullets")


def recommend_intervention(row: pd.Series) -> dict[str, str]:
    """
    Recommend an intervention category from amenity gaps and community signals.

    Returns dict with keys: category, label, rationale, primary_amenity_category.
    """
    raise NotImplementedError("TODO: recommend_intervention")


def enrich_with_evidence(scored: pd.DataFrame) -> pd.DataFrame:
    """
    Add evidence_bullets and recommended_intervention columns to scored table.

    Used by :mod:`community_gap.export` when building the frontend payload.
    """
    raise NotImplementedError("TODO: enrich_with_evidence")
