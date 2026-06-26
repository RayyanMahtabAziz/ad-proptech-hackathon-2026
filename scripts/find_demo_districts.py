#!/usr/bin/env python3
"""
Find strong demo districts for the hackathon video.

Run from repo root::

    python scripts/find_demo_districts.py

Writes recommendations to docs/demo_districts.md once scoring is implemented.
Until then, prints guidance based on processed outputs or raw data hints.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from community_gap import DOCS_DIR, OUTPUT_JSON  # noqa: E402

DEMO_DOC = DOCS_DIR / "demo_districts.md"


def find_demo_districts_from_payload(payload: dict) -> dict[str, list[dict]]:
    """
    Pick demo districts by confidence and gap score spread.

    Returns dict with keys: high_gap, high_confidence, low_confidence, contrast_pair.
    """
    raise NotImplementedError(
        "TODO: find_demo_districts_from_payload — rank and select demo candidates"
    )


def write_demo_doc(selections: dict[str, list[dict]], path: Path = DEMO_DOC) -> Path:
    """Write docs/demo_districts.md with chosen demo districts and talking points."""
    raise NotImplementedError("TODO: write_demo_doc — format markdown for demo script")


def main() -> int:
    print("Finding demo districts...")

    if not OUTPUT_JSON.exists():
        print(f"No processed output at {OUTPUT_JSON}")
        print("Run: python scripts/build_community_gap_data.py")
        return 1

    payload = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    districts = payload.get("districts", [])

    if not districts:
        print("Processed JSON has no districts yet (scaffold/stub phase).")
        print("Implement scoring, rebuild, then re-run this script.")
        print(f"\nTarget doc: {DEMO_DOC}")
        return 2

    try:
        selections = find_demo_districts_from_payload(payload)
        doc_path = write_demo_doc(selections)
        print(f"Wrote {doc_path}")
    except NotImplementedError as exc:
        print(f"Not implemented: {exc}")
        ranked = payload.get("ranked_summary", [])
        if ranked:
            print("\nTop districts from ranked_summary:")
            for row in ranked[:5]:
                print(f"  {row.get('rank', '?')}. {row.get('district')} — "
                      f"gap {row.get('community_gap_score')} ({row.get('confidence_level')})")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
