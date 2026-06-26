# Data Handoff — Frontend ↔ Data Layer

**Contract version:** 0.1.0  
**JSON output:** `processed/community_gap_outputs.json`  
**CSV debug output:** `processed/community_gap_scores.csv`

This document defines the stable shape the Next.js frontend should consume. **Do not change the JSON structure without updating this file and the frontend types.**

---

## How to build

From repo root:

```bash
pip install -r requirements.txt
python scripts/build_community_gap_data.py
python scripts/check_community_gap_data.py
```

---

## Top-level JSON shape

```json
{
  "project": "Community Gap & Confidence Copilot",
  "track": "Future Communities",
  "generated_at": "ISO-8601 UTC timestamp",
  "methodology_version": "0.1.0",
  "scoring_weights": {
    "community_need": 0.55,
    "amenity_shortage": 0.35,
    "market_pressure": 0.05,
    "intervention_feasibility": 0.05
  },
  "city_medians": {
    "service_demand_index": 0.0,
    "mobility_score": 0.0,
    "resident_experience_score": 0.0,
    "community_gap_score": 0.0
  },
  "district_count": 20,
  "districts": [ "... DistrictRecord ..." ],
  "ranked_summary": [ "... RankedRow ..." ]
}
```

---

## DistrictRecord

Each item in `districts`:

```json
{
  "district": "Al Ghadeer",
  "rank": 1,
  "area_type": "border",
  "profile": "affordable",
  "coordinates": { "latitude": 24.3, "longitude": 54.78 },
  "scores": {
    "community_need_score": 0.0,
    "amenity_adequacy_score": 0.0,
    "amenity_shortage_score": 0.0,
    "market_pressure_score": 0.0,
    "intervention_feasibility_score": 0.0,
    "community_gap_score": 0.0,
    "confidence_level": "high | medium | low"
  },
  "community_metrics": {
    "population_estimate": 0,
    "community_count": 0,
    "occupancy_rate": 0.0,
    "service_demand_index": 0.0,
    "mobility_score": 0.0,
    "resident_experience_score": 0.0,
    "top_optimization_opportunity": ""
  },
  "amenity_counts": {
    "education": 0,
    "healthcare": 0,
    "mobility": 0,
    "retail": 0,
    "community": 0,
    "services": 0
  },
  "amenity_total": 0,
  "amenity_per_10k": { "...": 0.0 },
  "category_shortages": { "...": 0.0 },
  "supporting_context": {
    "listing_count": 0,
    "transaction_count": 0,
    "vacant_parcel_count": 0
  },
  "recommended_intervention": {
    "category": "mobility_infrastructure",
    "primary_amenity_category": "mobility",
    "label": "Human-readable intervention label",
    "rationale": "One sentence tied to metrics"
  },
  "evidence": [
    "Deterministic bullet citing a visible metric"
  ],
  "confidence_explanation": "Why confidence is high/medium/low"
}
```

---

## RankedRow

Lightweight list for district selector / leaderboard:

```json
{
  "district": "Al Ghadeer",
  "rank": 1,
  "community_gap_score": 0.0,
  "confidence_level": "medium",
  "recommended_intervention": "Accelerate transit and mobility links"
}
```

---

## CSV summary columns

`processed/community_gap_scores.csv` — flat table for debugging:

- `intervention_rank`, `district`, `area_type`, `profile`
- `population_estimate`, `service_demand_index`, `mobility_score`, `resident_experience_score`
- `total_amenities`
- All score columns + `confidence_level`
- Per-category shortage columns (`shortage_education`, etc.)

---

## Frontend integration

1. Copy or import `processed/community_gap_outputs.json` into the app (e.g. `public/data/` or `lib/data/`).
2. District selector reads `districts[].district` or `ranked_summary`.
3. Detail panel reads one `DistrictRecord` by district name.
4. **LLM layer** receives `evidence`, `scores`, and `recommended_intervention` — it summarizes only; never recalculates scores.

---

## TypeScript stub (optional)

```typescript
export interface DistrictScores {
  community_need_score: number;
  amenity_adequacy_score: number;
  amenity_shortage_score: number;
  market_pressure_score: number;
  intervention_feasibility_score: number;
  community_gap_score: number;
  confidence_level: "high" | "medium" | "low";
}

export interface DistrictRecord {
  district: string;
  rank: number;
  scores: DistrictScores;
  evidence: string[];
  recommended_intervention: {
    category: string;
    label: string;
    rationale: string;
  };
  confidence_explanation: string;
}
```

---

## Status

**Scaffold phase** — `build_frontend_payload()` not yet implemented. Stub JSON may have empty `districts` array until scoring is complete.
