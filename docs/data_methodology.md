# Data Methodology — Community Gap & Confidence Copilot

**Version:** 0.1.0 (scaffold)  
**Package:** `community_gap/`  
**Build script:** `python scripts/build_community_gap_data.py`

This document describes the deterministic scoring methodology. Implementation lives in `community_gap/features.py`, `community_gap/scoring.py`, and `community_gap/evidence.py`.

---

## 1. Question we answer

> Which district needs intervention, what is missing, why do we believe that, and how much should the decision-maker trust the recommendation?

---

## 2. Data tiers

### Core (drive the main score)

| File | Role |
|------|------|
| `data/sample_communities.csv` | Community need signals |
| `data/osm_amenities.csv` | Real amenity coverage (OSM) |
| `data/districts.csv` | Master district dimension |

### Supporting (evidence + small score weight)

| File | Role |
|------|------|
| `data/sample_listings.csv` | Market activity context |
| `data/sample_transactions.csv` | Transaction volume context |
| `data/sample_parcels.csv` | Intervention feasibility |

### Optional

| File | Role |
|------|------|
| `data/sample_investors.csv` | Skipped unless demo needs investor angle |

See [data_inventory.md](./data_inventory.md) for column-level inventory and join quality.

---

## 3. Pipeline stages

```
data_loader.py  →  features.py  →  scoring.py  →  evidence.py  →  export.py
     load            aggregate         score          bullets         JSON/CSV
```

1. **Load & validate** — required columns, district name cleaning
2. **Features** — one row per district with community + amenity + context metrics
3. **Scoring** — deterministic 0–100 scores (see below)
4. **Evidence** — bullets and intervention recommendation per district
5. **Export** — `processed/community_gap_outputs.json` + `.csv`

---

## 4. Score definitions

All scores are 0–100 unless noted.

| Score | Source | Direction |
|-------|--------|-----------|
| `community_need_score` | Service demand, mobility weakness, experience weakness, population, occupancy | Higher = more need |
| `amenity_adequacy_score` | OSM counts per 10k residents vs city medians | Higher = better coverage |
| `amenity_shortage_score` | `100 − amenity_adequacy_score` | Higher = worse gap |
| `market_pressure_score` | Listings + transactions density | Supporting only |
| `intervention_feasibility_score` | Vacant parcels + infrastructure | Supporting only |
| `community_gap_score` | Weighted blend (below) | Primary rank |

### Community gap formula

```
community_gap_score =
    0.55 × community_need_score
  + 0.35 × amenity_shortage_score
  + 0.05 × market_pressure_score
  + 0.05 × intervention_feasibility_score
```

**Community need + amenity shortage = 90%** of the gap score.

---

## 5. Confidence

`confidence_level` is `high`, `medium`, or `low`.

Confidence reflects **evidence agreement**, not ML probability:

- Do community signals and amenity shortages point the same way?
- Are there enough OSM observations to support category claims?
- Are supporting datasets present and consistent?

The LLM may **explain** confidence; it must never **set** it.

---

## 6. Intervention recommendation

Derived from the largest population-adjusted amenity category shortage, weighted by community signals (e.g. low mobility boosts mobility category).

Optional tie-breaker: dominant `optimization_opportunity` from `sample_communities.csv`.

---

## 7. Design rules

- Deterministic — same inputs → same outputs
- Explainable — every score decomposes to visible metrics
- No external APIs, no database, no LLM in the data layer
- NaN → `None` in JSON exports

---

## 8. Implementation status

| Module | Status |
|--------|--------|
| `data_loader.py` | Implemented (load + validate) |
| `features.py` | Placeholder |
| `scoring.py` | Placeholder |
| `evidence.py` | Placeholder |
| `export.py` | Partial (`to_json_safe`, stub export) |

After implementation, re-run `python scripts/build_community_gap_data.py` and update this table.
