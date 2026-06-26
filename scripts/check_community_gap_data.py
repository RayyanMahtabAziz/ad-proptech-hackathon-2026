#!/usr/bin/env python3
"""
Validate raw data files and processed community gap outputs.

Run from repo root::

    python scripts/check_community_gap_data.py

Exit codes:
  0 — all checks passed
  1 — validation failure
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from community_gap import DATA_DIR, OUTPUT_CSV, OUTPUT_JSON  # noqa: E402
from community_gap.data_loader import (  # noqa: E402
    CORE_FILES,
    REQUIRED_COLUMNS,
    DataValidationError,
    load_core_datasets,
)

REQUIRED_JSON_KEYS = [
    "project",
    "track",
    "generated_at",
    "districts",
    "ranked_summary",
]

REQUIRED_SCORE_KEYS = [
    "community_need_score",
    "amenity_adequacy_score",
    "amenity_shortage_score",
    "community_gap_score",
    "confidence_level",
]


def check_raw_data(data_dir: Path) -> list[str]:
    """Verify core CSV files exist and load without validation errors."""
    errors: list[str] = []

    for filename in CORE_FILES:
        path = data_dir / filename
        if not path.exists():
            errors.append(f"Missing core file: {path}")
            continue
        missing_cols = [
            c for c in REQUIRED_COLUMNS[filename] if c not in __import__("pandas").read_csv(path, nrows=0).columns
        ]
        if missing_cols:
            errors.append(f"{filename}: missing columns {missing_cols}")

    try:
        districts, communities, amenities = load_core_datasets(data_dir)
        master = set(districts["district"])
        for label, df in [("communities", communities), ("amenities", amenities)]:
            orphans = set(df["district"]) - master
            if orphans:
                errors.append(f"{label}: districts not in districts.csv: {sorted(orphans)}")
        print(f"  Core data OK — {len(master)} districts, "
              f"{len(communities)} community rows, {len(amenities)} OSM amenities")
    except DataValidationError as exc:
        errors.append(str(exc))

    return errors


def check_processed_outputs() -> list[str]:
    """Verify processed JSON and CSV exist and have expected shape."""
    errors: list[str] = []

    if not OUTPUT_JSON.exists():
        errors.append(f"Missing processed output: {OUTPUT_JSON}")
        return errors

    try:
        payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {OUTPUT_JSON}: {exc}")
        return errors

    for key in REQUIRED_JSON_KEYS:
        if key not in payload:
            errors.append(f"JSON missing required key: {key}")

    districts = payload.get("districts", [])
    if not districts:
        print("  JSON districts array empty (scaffold/stub — OK for now)")
    else:
        sample = districts[0]
        scores = sample.get("scores", {})
        for key in REQUIRED_SCORE_KEYS:
            if key not in scores:
                errors.append(f"District scores missing key: {key}")

    print(f"  JSON OK — {len(districts)} district(s) in payload")

    if OUTPUT_CSV.exists():
        import pandas as pd

        df = pd.read_csv(OUTPUT_CSV)
        if "district" not in df.columns or "community_gap_score" not in df.columns:
            errors.append("CSV missing district or community_gap_score column")
        else:
            print(f"  CSV OK — {len(df)} rows")
    else:
        print(f"  CSV not found (optional during scaffold): {OUTPUT_CSV}")

    return errors


def main() -> int:
    print("Checking raw data...")
    raw_errors = check_raw_data(DATA_DIR)

    print("Checking processed outputs...")
    output_errors = check_processed_outputs()

    all_errors = raw_errors + output_errors
    if all_errors:
        print("\nFAILED:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
