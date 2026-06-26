"""
Deterministic scoring — all district scores and confidence levels.

The LLM must never invent these values. Every score must be traceable
to community metrics and OSM amenity counts.

Main outputs per district:
  - community_need_score
  - amenity_adequacy_score
  - amenity_shortage_score
  - market_pressure_score          (supporting — max ~5% of gap)
  - intervention_feasibility_score (supporting — max ~5% of gap)
  - community_gap_score            (primary rank — need + shortage dominate)
  - confidence_level               (high | medium | low)
"""

from __future__ import annotations

import pandas as pd

# Core gap weights — community need + amenity shortage must dominate.
GAP_WEIGHTS = {
    "community_need": 0.55,
    "amenity_shortage": 0.35,
    "market_pressure": 0.05,
    "intervention_feasibility": 0.05,
}


def compute_community_need_score(features: pd.DataFrame) -> pd.Series:
    """
    Score community demand pressure (0–100, higher = more need).

    Inputs: service_demand_index, mobility_score, resident_experience_score,
    population_estimate, occupancy_rate.
    """
    raise NotImplementedError("TODO: compute_community_need_score")


def compute_amenity_adequacy_score(features: pd.DataFrame) -> pd.Series:
    """
    Score OSM amenity coverage vs city medians (0–100, higher = better coverage).

    Normalize amenity counts per 10k residents before comparing to medians.
    """
    raise NotImplementedError("TODO: compute_amenity_adequacy_score")


def compute_amenity_shortage_score(adequacy: pd.Series) -> pd.Series:
    """Amenity shortage = 100 - amenity_adequacy_score."""
    raise NotImplementedError("TODO: compute_amenity_shortage_score")


def compute_market_pressure_score(features: pd.DataFrame) -> pd.Series:
    """
    Supporting market activity signal (0–100).

    Uses listings and transactions density. Must not dominate the main gap score.
    """
    raise NotImplementedError("TODO: compute_market_pressure_score")


def compute_intervention_feasibility_score(features: pd.DataFrame) -> pd.Series:
    """
    Supporting feasibility signal (0–100).

    Uses vacant/developable parcels and infrastructure context.
    """
    raise NotImplementedError("TODO: compute_intervention_feasibility_score")


def compute_community_gap_score(
    need: pd.Series,
    shortage: pd.Series,
    market: pd.Series,
    feasibility: pd.Series,
) -> pd.Series:
    """
    Primary intervention-priority score.

    Default weights: 55% need + 35% shortage + 5% market + 5% feasibility.
    """
    raise NotImplementedError("TODO: compute_community_gap_score")


def compute_confidence_level(scored: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """
  Return (confidence_level, confidence_explanation) per district.

    Confidence reflects evidence agreement, not ML probability.
    """
    raise NotImplementedError("TODO: compute_confidence_level")


def score_all_districts(features: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all scoring functions and return a ranked district table.

    Adds score columns, confidence fields, and intervention_rank (1 = highest gap).
    """
    raise NotImplementedError("TODO: score_all_districts — orchestrate all score functions")
