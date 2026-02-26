# WRK-357 Plan: Extract Offshore Vessel Fleet Data from PDF Posters

## Context

Two Offshore Magazine survey posters (2010 heavy lift, 2011 pipelay) contain structured
fleet data for offshore contractors. Both are **vector PDFs** (Adobe InDesign CS5 —
machine-readable text, no OCR needed). Data is currently inaccessible for programmatic
querying. Goal: load into `frontierdeepwater/data/` so downstream agents can query
contractor capabilities (e.g. "find all J-lay vessels capable of 2000m WD").

`frontierdeepwater/data/raw/` and `data/processed/` are **empty** (only `.gitkeep`).
No existing ETL scripts. Python tooling: uv + assetutilities dep, pytest 80% threshold.

---

## Phase 1 — Stage Raw Data

**Files to create/copy:**

1. `frontierdeepwater/data/raw/offshore-magazine/`
   - Copy `1111PipelayPoster112711APPads.pdf` → `pipelay-contractors-2011.pdf`
   - Copy `OFF1011HeavyLift-Poster.pdf` → `heavy-lift-vessels-2010.pdf`
   - Create `README.md` documenting provenance (publisher, date, source path)

---

## Phase 2 — Extract Script

**File:** `frontierdeepwater/scripts/python/extract_vessel_data.py`

Strategy: Use **PyMuPDF** (`fitz`) — available or install in frontierdeepwater venv.
PyMuPDF provides `page.get_text("dict")` giving text blocks with bounding-box
coordinates. Group blocks by y-coordinate bands → rows; x-coordinate ranges → columns.

```
extract_vessel_data.py --pdf <path> --type [pipelay|heavylift] --out <csv_path>
```

**Pipelay schema** → `data/processed/vessel-fleet/pipelay-contractors-2011.csv`:
```
contractor, vessel_name, vessel_type, operating_region,
loa_ft, beam_ft, draft_load_ft, draft_light_ft,
accommodation_persons, mooring_system, dp_class,
lay_method,            # s-lay | j-lay | reel | flex
min_pipe_dia_in, max_pipe_dia_in,
max_water_depth_ft, burial_capable,
notes, needs_review    # flag for partially-legible rows
```

**Heavy-lift schema** → `data/processed/vessel-fleet/heavy-lift-vessels-2010.csv`:
```
contractor, vessel_name, vessel_type, operating_region,
loa_ft, beam_ft, draft_ft, deck_capacity_t,
classification,        # ABS | Lloyd's | DNV | BV
crane_model,
primary_lift_capacity_t, primary_lift_radius_ft,
secondary_lift_capacity_t, secondary_lift_radius_ft,
max_hook_height_ft,
mooring_system, dp_class,
notes, needs_review
```

**Parsing notes:**
- Dimensions in feet (') — store numeric, strip unit
- Lift ratings in "NNN st @ RRR'" format — regex `(\d+)\s*st\s*@\s*(\d+)'`
- `lay_method` inferred from vessel_type text (contains "S-lay", "J-lay", "reel")
- `needs_review: true` when >3 empty mandatory fields (data confidence flag)
- Rows with only `--` or blank cells → skip with log entry

---

## Phase 3 — Tests

**File:** `frontierdeepwater/tests/unit/test_extract_vessel_data.py`

Test cases (TDD first):
- `test_parse_dimension_strips_unit` — "984'" → 984.0
- `test_parse_lift_rating` — "600 st @ 70'" → (600, 70)
- `test_lay_method_inference` — "DP pipelay J-lay vessel" → "j-lay"
- `test_needs_review_flag` — row with >3 empty fields → needs_review=True
- `test_csv_output_schema` — output CSV has all required columns

---

## Phase 4 — Provenance README

**File:** `frontierdeepwater/data/raw/offshore-magazine/README.md`

Documents:
- Source: Offshore Magazine survey posters
- Dates: November 2010 (heavy lift), November 2011 (pipelay)
- Original paths on ace-linux-2 (archival reference)
- Schema references to processed CSV files
- Known limitations (data vintage: 2010/2011; some TBD/N/A fields)

---

## Verification

```bash
# Run tests first (TDD)
cd frontierdeepwater && python -m pytest tests/unit/test_extract_vessel_data.py -v

# Run extraction
python scripts/python/extract_vessel_data.py \
  --pdf data/raw/offshore-magazine/pipelay-contractors-2011.pdf \
  --type pipelay --out data/processed/vessel-fleet/pipelay-contractors-2011.csv

python scripts/python/extract_vessel_data.py \
  --pdf data/raw/offshore-magazine/heavy-lift-vessels-2010.pdf \
  --type heavylift --out data/processed/vessel-fleet/heavy-lift-vessels-2010.csv

# Spot-check row counts (expect ~50-60 pipelay, ~40-50 heavylift)
wc -l data/processed/vessel-fleet/*.csv

# Check needs_review flags
grep "True" data/processed/vessel-fleet/*.csv | wc -l
```

Commit: `feat(data): WRK-357 — extract pipelay + heavy-lift fleet data from PDF posters`

---

## Follow-on: WRK-358 (to be captured after this item)

Deep online research to update and enrich the 2010/2011 data:
- Find current fleet status for each contractor (active/stacked/scrapped)
- Source newer Offshore Magazine surveys (2015–2024) for updated specs
- Add IMO numbers, flag state, current owner if vessels changed hands
- Target: `data/processed/vessel-fleet/pipelay-contractors-current.csv` and
  `heavy-lift-vessels-current.csv` alongside the archival 2010/2011 snapshots
