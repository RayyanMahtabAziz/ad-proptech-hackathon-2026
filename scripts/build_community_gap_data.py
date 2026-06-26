#!/usr/bin/env python3
"""
Build processed community gap outputs from challenge CSVs.

Run from repo root::

    python scripts/build_community_gap_data.py

Writes:
  - processed/community_gap_outputs.json
  - processed/community_gap_scores.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow imports when run as: python scripts/build_community_gap_data.py
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from community_gap.data_loader import DataValidationError, load_all_datasets  # noqa: E402
from community_gap.export import build_metadata_stub, export_json, export_all  # noqa: E402
from community_gap.features import build_district_feature_table  # noqa: E402
from community_gap.scoring import score_all_districts  # noqa: E402


def _write_stub(bundle, output_dir: Path | None) -> None:
    """Write placeholder outputs when scoring is not yet implemented."""
    out_dir = output_dir or REPO_ROOT / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    stub = build_metadata_stub()
    stub["district_count"] = len(bundle.districts)
    stub["master_districts"] = sorted(bundle.districts["district"].tolist())
    json_path = export_json(stub, out_dir / "community_gap_outputs.json")
    print(f"Wrote stub JSON: {json_path}")
    print("Implement features.py + scoring.py to produce full district records.")


def build(data_dir: Path | None = None, output_dir: Path | None = None) -> bool:
    """
    Load data → features → scores → export.

    Returns True if full pipeline ran; False if stub-only (scaffold phase).
    """
    print("Loading datasets...")
    bundle = load_all_datasets(data_dir)

    try:
        print("Building district features...")
        features = build_district_feature_table(bundle)

        print("Scoring districts...")
        scored = score_all_districts(features)

        print("Exporting...")
        json_path, csv_path = export_all(scored, output_dir)
        print(f"Wrote {json_path}")
        print(f"Wrote {csv_path}")
        return True

    except NotImplementedError as exc:
        print(f"Scaffold mode: {exc}")
        _write_stub(bundle, output_dir)
        return False


def main() -> int:
    try:
        full = build()
        print("Done." + (" Full pipeline complete." if full else " Stub outputs only."))
    except DataValidationError as exc:
        print(f"Data validation error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
