# Demo Districts

**Status:** Pending — run `python scripts/find_demo_districts.py` after scoring is implemented.

This file will list recommended districts for the 2–3 minute hackathon demo video.

---

## What we need from demo districts

| Slot | Purpose | Ideal traits |
|------|---------|--------------|
| **Primary** | Main walkthrough | High gap score, medium/high confidence, clear evidence |
| **Contrast** | Show confidence badge | High gap but low confidence — honest uncertainty |
| **Positive** | Balanced district | Lower gap, good amenity coverage — "no intervention needed" |

---

## Candidates (to be filled by script)

### Primary demo district

_TBD_

**Talking points:**
- Service demand vs city median
- Weakest OSM amenity category
- Recommended intervention
- Confidence explanation

### Contrast district (low confidence)

_TBD_

**Talking points:**
- Why evidence is mixed
- What a decision-maker should do before acting

### Positive reference district

_TBD_

**Talking points:**
- Adequate amenity coverage relative to need
- Lower intervention priority

---

## How this file is generated

```bash
python scripts/build_community_gap_data.py
python scripts/find_demo_districts.py
```

The script writes selections and talking-point hints into this document.

---

## Manual override

If the auto-selected districts are not demo-friendly, edit this file and use these districts in `docs/demo-script.md`.
