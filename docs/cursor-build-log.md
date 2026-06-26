# Cursor Build Log

Team log for the **Best Use of Cursor** award. Update after each meaningful Cursor-assisted step.

---

## 2026-06-26 — Data pipeline scaffold

**Prompt used:**
> Create community_gap/ package structure with data_loader, features, scoring, evidence, export modules; scripts for build/check/find_demo_districts; processed/ output folder; and docs for inventory, methodology, handoff, demo districts, and this build log. Use pandas and pathlib. Placeholder functions first.

**Output created:**
- `community_gap/` package (6 modules)
- `scripts/build_community_gap_data.py`
- `scripts/check_community_gap_data.py`
- `scripts/find_demo_districts.py`
- `processed/.gitkeep`
- `docs/data_methodology.md`, `docs/data_handoff.md`, `docs/demo_districts.md`

**Issue solved:**
Established the canonical data-layer layout expected by `.cursor/rules/002-data-layer.mdc` and `005-hackathon-workflow.mdc`, with stable output paths and frontend JSON contract.

**How it helped:**
Gives the team a clear fill-in-the-blanks structure — `data_loader.py` works today; features/scoring/evidence can be implemented in parallel without reorganizing folders.

---

## Template for next entries

```markdown
## YYYY-MM-DD — Short title

**Prompt used:**
> ...

**Output created:**
- ...

**Issue solved:**
...

**How it helped:**
...
```
