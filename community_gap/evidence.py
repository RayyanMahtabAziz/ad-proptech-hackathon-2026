"""
Evidence generation — deterministic bullets and gap drivers.

All evidence is derived from row values and precomputed signal columns.
The LLM must not invent bullets or drivers.
"""

from __future__ import annotations

import pandas as pd

# Priority order for gap drivers (matches evidence bullet strength).
_DRIVER_ORDER: list[tuple[str, str]] = [
    ("signal_high_service_demand", "Service demand"),
    ("signal_weak_mobility", "Mobility weakness"),
    ("signal_weak_resident_experience", "Resident experience"),
    ("signal_low_education", "Education shortage"),
    ("signal_low_healthcare", "Healthcare shortage"),
    ("signal_low_mobility_amenities", "Mobility amenity shortage"),
    ("signal_high_market_pressure", "Market pressure"),
]

_MIN_BULLETS = 4
_MAX_BULLETS = 7


def _is_true(row: pd.Series, key: str) -> bool:
    """Safely read a boolean signal from a row."""
    if key not in row.index:
        return False
    value = row[key]
    if pd.isna(value):
        return False
    return bool(value)


def _fmt_num(value: object, decimals: int = 0) -> str:
    """Format a numeric value for display in a bullet."""
    if pd.isna(value):
        return "n/a"
    if decimals == 0:
        return f"{int(round(float(value)))}"
    return f"{float(value):.{decimals}f}"


def _amenity_signals_mixed(row: pd.Series) -> bool:
    """True when OSM amenity signals point in different directions."""
    low_flags = [
        _is_true(row, "signal_low_education"),
        _is_true(row, "signal_low_healthcare"),
        _is_true(row, "signal_low_mobility_amenities"),
    ]
    low_count = sum(low_flags)
    return 0 < low_count < 3


def _should_flag_mixed_evidence(row: pd.Series, drivers: list[str]) -> bool:
    """Decide whether to append the Mixed evidence driver."""
    confidence = row.get("confidence_level", "")
    if confidence in ("Medium", "Low"):
        return True
    if _amenity_signals_mixed(row):
        return True
    agreement = row.get("signal_agreement_count", 0)
    if not pd.isna(agreement) and 3 <= int(agreement) <= 5:
        return True
    return False


def _build_bullet_candidates(row: pd.Series) -> list[tuple[int, str]]:
    """Return (priority, bullet_text) candidates derived only from row values."""
    candidates: list[tuple[int, str]] = []

    # --- Core community signals (strongest) ---
    if _is_true(row, "signal_high_service_demand"):
        demand = _fmt_num(row.get("service_demand_index"))
        median = _fmt_num(row.get("city_median_service_demand"))
        candidates.append(
            (0, f"Service demand is above the city median ({demand} vs {median}).")
        )

    if _is_true(row, "signal_weak_mobility"):
        mobility = _fmt_num(row.get("mobility_score"))
        median = _fmt_num(row.get("city_median_mobility_score"))
        candidates.append(
            (1, f"Mobility score is below the city median ({mobility} vs {median}).")
        )

    if _is_true(row, "signal_weak_resident_experience"):
        experience = _fmt_num(row.get("resident_experience_score"))
        median = _fmt_num(row.get("city_median_resident_experience_score"))
        candidates.append(
            (
                2,
                f"Resident experience is weaker than the city median "
                f"({experience} vs {median}).",
            )
        )

    # --- Real OSM amenity coverage ---
    if _is_true(row, "signal_low_education"):
        count = _fmt_num(row.get("education"))
        median = _fmt_num(row.get("city_median_education"))
        candidates.append(
            (
                3,
                f"Education amenity coverage is below the city median "
                f"({count} OSM amenities vs median {median}).",
            )
        )

    if _is_true(row, "signal_low_healthcare"):
        count = _fmt_num(row.get("healthcare"))
        median = _fmt_num(row.get("city_median_healthcare"))
        candidates.append(
            (
                4,
                f"Healthcare amenity coverage is below the city median "
                f"({count} OSM amenities vs median {median}).",
            )
        )

    if _is_true(row, "signal_low_mobility_amenities"):
        count = _fmt_num(row.get("mobility"))
        median = _fmt_num(row.get("city_median_mobility_amenities"))
        candidates.append(
            (
                5,
                f"Mobility-related amenities are limited compared with other districts "
                f"({count} OSM vs median {median}).",
            )
        )

    if _is_true(row, "signal_high_gap"):
        gap = _fmt_num(row.get("community_gap_score"))
        candidates.append(
            (6, f"Community gap score is high ({gap}/100), indicating priority for review.")
        )

    # --- Supporting context (after core evidence) ---
    listing_count = row.get("listing_count")
    if (
        _is_true(row, "signal_high_market_pressure")
        and not pd.isna(listing_count)
        and int(listing_count) > 0
    ):
        candidates.append(
            (
                7,
                f"Residential listing activity suggests added community pressure "
                f"({int(listing_count)} listings in district).",
            )
        )

    transaction_count = row.get("transaction_count")
    if (
        _is_true(row, "signal_high_market_pressure")
        and not pd.isna(transaction_count)
        and int(transaction_count) > 0
        and not any("Transaction activity" in text for _, text in candidates)
    ):
        candidates.append(
            (
                8,
                f"Transaction activity indicates active market movement in this district "
                f"({int(transaction_count)} transactions).",
            )
        )

    feasibility = row.get("intervention_feasibility_score")
    vacant = row.get("vacant_or_available_parcel_count")
    if (
        not pd.isna(feasibility)
        and int(feasibility) >= 60
        and not pd.isna(vacant)
        and int(vacant) > 0
    ):
        candidates.append(
            (
                9,
                f"Parcel/infrastructure context suggests the intervention may be feasible "
                f"({int(vacant)} vacant or developable parcels).",
            )
        )

    if _should_flag_mixed_evidence(row, []):
        candidates.append(
            (
                10,
                "Amenity coverage is mixed, so the recommendation should be treated cautiously.",
            )
        )

    # Fallback bullets when few signals fire — still grounded in actual values.
    if len(candidates) < _MIN_BULLETS:
        total_amenities = row.get("total_amenities")
        if not pd.isna(total_amenities):
            candidates.append(
                (
                    11,
                    f"District has {int(total_amenities)} mapped OSM amenities across "
                    f"six categories.",
                )
            )

        shortage = row.get("amenity_shortage_score")
        need = row.get("community_need_score")
        if not pd.isna(shortage) and not pd.isna(need):
            candidates.append(
                (
                    12,
                    f"Community need score is {_fmt_num(need)} and amenity shortage score "
                    f"is {_fmt_num(shortage)}.",
                )
            )

        population = row.get("population_estimate")
        if not pd.isna(population):
            candidates.append(
                (13, f"Estimated population in this community record: {int(population):,}.")
            )

    return candidates


def generate_top_gap_drivers(row: pd.Series) -> list[str]:
    """Return main gap driver labels for a row (JSON-serializable strings)."""
    drivers = [label for signal, label in _DRIVER_ORDER if _is_true(row, signal)]

    if _should_flag_mixed_evidence(row, drivers) and "Mixed evidence" not in drivers:
        drivers.append("Mixed evidence")

    return drivers


def generate_evidence_for_row(row: pd.Series) -> list[str]:
    """
    Build 4–7 short, demo-friendly evidence bullets for one record.

    Uses only actual row values and boolean signal columns — nothing invented.
    """
    candidates = _build_bullet_candidates(row)
    candidates.sort(key=lambda item: item[0])

    bullets: list[str] = []
    seen: set[str] = set()
    for _, text in candidates:
        if text in seen:
            continue
        seen.add(text)
        bullets.append(text)
        if len(bullets) >= _MAX_BULLETS:
            break

    # Ensure minimum bullet count with non-duplicative fallbacks.
    if len(bullets) < _MIN_BULLETS:
        gap = row.get("community_gap_score")
        level = row.get("gap_level", "")
        if not pd.isna(gap) and f"gap score is" not in " ".join(bullets).lower():
            bullets.append(
                f"Community gap score is {_fmt_num(gap)}/100 ({level} priority band)."
            )

        confidence = row.get("confidence_level", "")
        if confidence and len(bullets) < _MIN_BULLETS:
            bullets.append(f"Confidence level is {confidence} based on signal agreement.")

    return bullets[:_MAX_BULLETS]


def add_evidence(df: pd.DataFrame) -> pd.DataFrame:
    """Add evidence_bullets and top_gap_drivers columns to a scored dataframe."""
    out = df.copy()
    out["evidence_bullets"] = out.apply(generate_evidence_for_row, axis=1)
    out["top_gap_drivers"] = out.apply(generate_top_gap_drivers, axis=1)
    return out


# Backward-compatible aliases
def generate_evidence_bullets(row: pd.Series, city_medians: dict[str, float] | None = None) -> list[str]:
    """Alias for :func:`generate_evidence_for_row` (city_medians unused — medians are on the row)."""
    del city_medians
    return generate_evidence_for_row(row)


def build_city_medians(scored: pd.DataFrame) -> dict[str, float]:
    """Return city-wide median values for key comparison metrics."""
    return {
        "service_demand_index": float(scored["service_demand_index"].median()),
        "mobility_score": float(scored["mobility_score"].median()),
        "resident_experience_score": float(scored["resident_experience_score"].median()),
        "community_gap_score": float(scored["community_gap_score"].median()),
    }


def enrich_with_evidence(scored: pd.DataFrame) -> pd.DataFrame:
    """Add evidence columns to a scored table (alias for :func:`add_evidence`)."""
    return add_evidence(scored)
