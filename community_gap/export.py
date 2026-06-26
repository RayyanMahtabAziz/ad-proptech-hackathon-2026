"""
Export processed outputs for the frontend and debugging.

Stable output contract (see docs/data_handoff.md):
  - processed/community_gap_outputs.json
  - processed/community_gap_scores.csv
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from community_gap import OUTPUT_CSV, OUTPUT_JSON, PROCESSED_DIR
from community_gap.scoring import GAP_WEIGHTS


def to_json_safe(value: Any) -> Any:
    """
    Convert pandas/numpy types to JSON-serializable Python types.

    Replaces NaN with None.
    """
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if np.isnan(value):
            return None
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def build_frontend_payload(scored: pd.DataFrame) -> dict[str, Any]:
    """
    Build the frontend-ready JSON structure.

    Shape is defined in docs/data_handoff.md — do not change without updating docs.
    """
    raise NotImplementedError("TODO: build_frontend_payload")


def export_json(payload: dict[str, Any], path: Path | None = None) -> Path:
    """Write community_gap_outputs.json."""
    out_path = path or OUTPUT_JSON
    out_path.parent.mkdir(parents=True, exist_ok=True)
    safe_payload = json.loads(json.dumps(payload, default=to_json_safe))
    out_path.write_text(json.dumps(safe_payload, indent=2), encoding="utf-8")
    return out_path


def export_csv_summary(scored: pd.DataFrame, path: Path | None = None) -> Path:
    """Write a flat community_gap_scores.csv for debugging and judge review."""
    raise NotImplementedError("TODO: export_csv_summary — select summary columns and write CSV")


def export_all(scored: pd.DataFrame, output_dir: Path | None = None) -> tuple[Path, Path]:
    """
    Export JSON + CSV to processed/.

    Returns (json_path, csv_path).
    """
    out_dir = output_dir or PROCESSED_DIR
    payload = build_frontend_payload(scored)
    json_path = export_json(payload, out_dir / OUTPUT_JSON.name)
    csv_path = export_csv_summary(scored, out_dir / OUTPUT_CSV.name)
    return json_path, csv_path


def build_metadata_stub() -> dict[str, Any]:
    """Return a minimal payload stub for testing export plumbing."""
    return {
        "project": "Community Gap & Confidence Copilot",
        "track": "Future Communities",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "methodology_version": "0.1.0",
        "scoring_weights": GAP_WEIGHTS,
        "status": "placeholder — run build script after implementing scoring",
        "districts": [],
        "ranked_summary": [],
    }
