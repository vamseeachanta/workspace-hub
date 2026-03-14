# Stream A: Data Completeness — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Maximize data capture from the 1M doc index and all public O&G sources, then produce a data vision document.

**Architecture:** Three-phase approach: (1) audit existing coverage using the standards-transfer-ledger and index.jsonl, (2) extract content from unprocessed docs and ingest missing public data sources, (3) capture remaining work as WRK items and write the data vision doc in worldenergydata.

**Tech Stack:** Python (uv run), PyYAML, existing Phase A–G pipeline scripts, worldenergydata loaders, calculation-report schema

**Parent WRK:** WRK-1179 (Feature WRK)

---

## Chunk 1: Audit & Research (Days 1–3)

### Task 1: Audit Doc Index Coverage

**Files:**
- Read: `data/document-index/standards-transfer-ledger.yaml`
- Read: `data/document-index/index.jsonl` (query via scripts)
- Read: `scripts/data/document-index/config.yaml`
- Create: `data/document-index/data-audit-report.md`

- [ ] **Step 1: Query current ledger status**

Run:
```bash
cd /mnt/local-analysis/workspace-hub
uv run --no-project python scripts/data/document-index/query-ledger.py --summary
```
Expected: summary table showing 425 standards with status counts (done/gap/wrk_captured/reference)

- [ ] **Step 2: Generate domain coverage report**

Run:
```bash
uv run --no-project python scripts/data/document-index/generate-coverage-report.py
```
Expected: markdown report at `docs/document-intelligence/domain-coverage.md`

- [ ] **Step 3: Count index records by source and domain**

Run:
```bash
uv run --no-project python -c "
import json
from collections import Counter
sources = Counter()
domains = Counter()
with_summary = 0
total = 0
with open('data/document-index/index.jsonl') as f:
    for line in f:
        rec = json.loads(line)
        total += 1
        sources[rec.get('source', 'unknown')] += 1
        domains[rec.get('domain') or 'unclassified'] += 1
        if rec.get('summary'):
            with_summary += 1
print(f'Total: {total}')
print(f'With summary (Phase B): {with_summary} ({with_summary*100//total}%)')
print(f'\nBy source:')
for s, c in sources.most_common():
    print(f'  {s}: {c}')
print(f'\nBy domain:')
for d, c in domains.most_common(15):
    print(f'  {d}: {c}')
"
```
Expected: breakdown showing what % have Phase B content extraction vs. metadata-only

- [ ] **Step 4: Identify exhaustion status**

Run:
```bash
uv run --no-project python scripts/data/document-index/query-ledger.py --status gap --domain all | head -50
```
Expected: list of gap standards that still need implementation

- [ ] **Step 5: Write audit summary**

Create `data/document-index/data-audit-report.md` with:
- Total records and Phase B coverage %
- Records by source and domain
- Standards ledger status summary (done/gap/wrk_captured/reference per domain)
- Top priority gaps by domain
- List of unclassified records that need domain assignment

- [ ] **Step 6: Commit audit**

```bash
git add data/document-index/data-audit-report.md docs/document-intelligence/domain-coverage.md
git commit -m "docs(WRK-1179): data audit — doc index coverage report" && git push
```

---

### Task 2: Audit worldenergydata Source Coverage

**Files:**
- Read: `worldenergydata/src/worldenergydata/` (all modules)
- Read: `specs/data-sources/worldenergydata.yaml`
- Create: `data/document-index/public-og-data-sources.yaml`

- [ ] **Step 1: Catalog existing worldenergydata modules**

```bash
ls -d /mnt/local-analysis/workspace-hub/worldenergydata/src/worldenergydata/*/
```
Expected: 30+ directories (bsee, eia, sodir, mexico_cnh, brazil_anp, canada, texas_rrc, ukcs, west_africa, metocean, marine_safety, etc.)

- [ ] **Step 2: For each module, check data freshness and completeness**

Run:
```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
PYTHONPATH="src:../assetutilities/src" uv run python -c "
import importlib
import pkgutil
import worldenergydata
for importer, modname, ispkg in pkgutil.walk_packages(worldenergydata.__path__, worldenergydata.__name__ + '.'):
    if ispkg:
        print(modname)
"
```
Expected: full module tree showing what's implemented

- [ ] **Step 3: Research public O&G data sources globally**

This is an agent research step (web search + existing knowledge). Time box: 2 hours max.
Use web search tools to catalog public O&G data APIs and datasets in these categories:
- **Government regulatory**: BOEM (data.boem.gov), PHMSA (phmsa.dot.gov), USGS (usgs.gov/science-explorer)
- **International energy**: OPEC (opec.org/opec_web/en/publications), IEA (iea.org/data-and-statistics), BP Statistical Review
- **Environmental**: ERA5 (cds.climate.copernicus.eu), NOAA NDBC (ndbc.noaa.gov), CO-OPS, CMEMS (marine.copernicus.eu)
- **Academic/open data**: The Well (huggingface.co/datasets), OpenSubsurface, SEG open data
- **Financial**: EIA spot prices (api.eia.gov), Baker Hughes rig count (bakerhughes.com/rig-count)
- **Safety**: BSEE incidents (bsee.gov/stats-facts), MAIB reports, IMO GISIS casualty database

For each source found, record: name, URL, API availability (yes/no), data format, update frequency.

- [ ] **Step 4: Create public data source catalog**

Create `data/document-index/public-og-data-sources.yaml`:
```yaml
generated: "2026-03-14"
total_sources: N
categories:
  already_ingested:
    - name: "BSEE Production"
      module: "worldenergydata.bsee"
      coverage: "GOM wells and production, 1947-present"
      freshness: "quarterly"
    # ... all existing modules
  known_not_ingested:
    - name: "BOEM Lease Data"
      url: "https://www.data.boem.gov/"
      api: true
      priority: high
      rationale: "Complements BSEE production with lease/block data"
    # ... known gaps
  newly_discovered:
    - name: "Source Name"
      url: "..."
      api: true/false
      data_format: "CSV/JSON/API"
      priority: high/medium/low
      rationale: "Why this matters for the ecosystem"
    # ... research findings
```

- [ ] **Step 5: Commit source catalog**

```bash
git add data/document-index/public-og-data-sources.yaml
git commit -m "docs(WRK-1179): public O&G data source catalog" && git push
```

---

### Task 3: Day 3 Checkpoint — Review Audit Outputs

- [ ] **Step 1: Present audit summary to user**

Show: doc index coverage %, ledger gap count, source catalog summary (ingested vs. not vs. new)

- [ ] **Step 2: Get user direction on priorities**

Which gaps to focus on in Phase 2? Which new data sources are highest priority?

---

## Chunk 2: Extract & Ingest (Days 4–10)

### Task 4: Maximize Doc Content Extraction

**Files:**
- Modify: `scripts/data/document-index/phase-b-extract.py`
- Modify: `data/document-index/index.jsonl` (via pipeline)
- Read: `scripts/data/document-index/config.yaml`

- [ ] **Step 1: Identify unprocessed records**

Run:
```bash
uv run --no-project python -c "
import json
unprocessed = []
with open('data/document-index/index.jsonl') as f:
    for line in f:
        rec = json.loads(line)
        if not rec.get('summary') and rec.get('source') in ('og_standards', 'ace_standards'):
            unprocessed.append(rec)
print(f'Unprocessed standards docs: {len(unprocessed)}')
# Show top extensions
from collections import Counter
exts = Counter(r.get('ext','?') for r in unprocessed)
for e, c in exts.most_common(10):
    print(f'  .{e}: {c}')
"
```

- [ ] **Step 2: Run Phase B extraction on unprocessed batches**

Run in batches (respecting API budget). Check actual flags first:
```bash
uv run --no-project python scripts/data/document-index/phase-b-extract.py --help
```
Then run with correct flags:
```bash
uv run --no-project python scripts/data/document-index/phase-b-extract.py \
  --source og_standards --limit 100
```
Repeat with increasing `--limit` values. Monitor cost against $20/day budget.

- [ ] **Step 3: Run Phase C classification on newly extracted**

```bash
uv run --no-project python scripts/data/document-index/phase-c-classify.py --dry-run
```
Review output, then run without `--dry-run` to apply:
```bash
uv run --no-project python scripts/data/document-index/phase-c-classify.py
```

- [ ] **Step 4: Rebuild ledger with new extractions**

```bash
uv run --no-project python scripts/data/document-index/build-ledger.py
```

- [ ] **Step 5: Rebuild capability maps**

```bash
uv run --no-project python scripts/data/document-index/build-capability-map.py
```

- [ ] **Step 6: Commit extraction progress**

Count new summaries, then commit:
```bash
NEW_COUNT=$(find data/document-index/summaries/ -newer data/document-index/data-audit-report.md -name "*.json" | wc -l)
git add data/document-index/standards-transfer-ledger.yaml specs/capability-map/
git commit -m "feat(WRK-1179): Phase B extraction batch — ${NEW_COUNT} new summaries" && git push
```

---

### Task 5: Ingest Missing Public O&G Data Sources

**Files:**
- Create: `worldenergydata/src/worldenergydata/<new_source>/` (per source)
- Create: `worldenergydata/tests/test_<new_source>.py` (per source)

For each high-priority source from the catalog (Task 2, Step 4):

- [ ] **Step 1: Write failing test for new data source loader**

```python
# worldenergydata/tests/test_<source_name>.py
def test_<source>_loader_returns_dataframe():
    from worldenergydata.<source> import load_data
    df = load_data()
    assert len(df) > 0
    assert "required_column" in df.columns
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
PYTHONPATH="src:../assetutilities/src" uv run python -m pytest tests/test_<source>.py -v --noconftest
```
Expected: FAIL — module not found

- [ ] **Step 3: Implement data source loader**

Create `worldenergydata/src/worldenergydata/<source>/__init__.py` with:
- API client or file parser
- Data validation
- Structured output (pandas DataFrame or typed dict)

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
PYTHONPATH="src:../assetutilities/src" uv run python -m pytest tests/test_<source>.py -v --noconftest
```
Expected: PASS

- [ ] **Step 5: Commit new source**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
git add src/worldenergydata/<source>/ tests/test_<source>.py
git commit -m "feat(WRK-1179): add <source> data loader" && git push
```

Repeat Steps 1–5 for each new data source.

---

### Task 6: Reclassify Unclassified Records

**Files:**
- Modify: `data/document-index/index.jsonl` (via reclassify script)

- [ ] **Step 1: Count unclassified records**

```bash
uv run --no-project python -c "
import json
unclassified = 0
with open('data/document-index/index.jsonl') as f:
    for line in f:
        rec = json.loads(line)
        if not rec.get('domain'):
            unclassified += 1
print(f'Unclassified: {unclassified}')
"
```

- [ ] **Step 2: Run reclassification audit (dry run)**

```bash
uv run --no-project python scripts/data/document-index/reclassify-audit.py --dry-run --batch-size 1000
```
Review proposed reclassifications before applying.

- [ ] **Step 3: Apply reclassifications**

```bash
uv run --no-project python scripts/data/document-index/reclassify-audit.py --apply --batch-size 1000
```

- [ ] **Step 4: Commit reclassification**

```bash
git add data/document-index/
git commit -m "feat(WRK-1179): reclassify N unclassified doc index records" && git push
```

---

## Chunk 3: Capture & Vision (Days 11–15)

### Task 7: Generate WRK Items for Remaining Gaps

**Files:**
- Read: `data/document-index/standards-transfer-ledger.yaml`
- Create: `.claude/work-queue/pending/WRK-*.md` (multiple)

- [ ] **Step 1: Run gap-to-WRK generator**

```bash
uv run --no-project python scripts/data/document-index/phase-f-gap-wrk-generator.py --dry-run
```
Review proposed WRK items.

- [ ] **Step 2: Generate WRK items**

Run without `--dry-run` to generate (the script writes WRK files by default when not in dry-run mode):
```bash
uv run --no-project python scripts/data/document-index/phase-f-gap-wrk-generator.py
```

- [ ] **Step 3: Create WRK items for unintegrated data sources**

For each source in `public-og-data-sources.yaml` with status `known_not_ingested` or `newly_discovered`:
- Create a WRK item in `.claude/work-queue/pending/` with:
  - Title: "Ingest <source> into worldenergydata"
  - Priority based on catalog rating
  - Acceptance criteria: loader module + tests + data schema
  - `parent: WRK-1179`

- [ ] **Step 4: Commit WRK items**

```bash
git add .claude/work-queue/pending/
git commit -m "feat(WRK-1179): generate WRK items for data gaps" && git push
```

---

### Task 8: Write Data Vision Document

**Files:**
- Create: `worldenergydata/docs/vision/DATA-VISION.md`

- [ ] **Step 1: Write the vision document**

Structure:
```markdown
# Data Vision — ACE Engineering Ecosystem

## Current State
- Doc index: N records, X% with content extraction
- Standards ledger: N standards tracked, X done, Y gaps
- Public data sources: N ingested, M identified but not ingested
- Domain coverage by discipline (table)

## Data Needs by Workflow Pattern
(Cross-reference agent-vision.md Patterns 1–4)
- Pattern 1 (Subsea Fatigue): needs metocean scatter data, S-N curve library
- Pattern 2 (Pipeline Feasibility): needs ERA5/NDBC metocean, BSEE regulatory
- Pattern 3 (Field Screening): needs BSEE production + EIA pricing + metocean
- Pattern 4 (Portfolio Risk): needs yfinance + EIA commodity prices

## Data-to-Analysis Roadmap
Which sources unlock which engineering capabilities:
- Tier 1: data exists and is queryable
- Tier 2: data feeds into automated calculations
- Tier 3: data triggers autonomous Sense → Plan → Act

## Gap Register
- Unimplemented standards by domain (link to WRK items)
- Unintegrated public sources (link to WRK items)
- Content extraction backlog (records needing Phase B)

## Success Metrics
- Standards implementation rate (done / total)
- Data source coverage (ingested / identified)
- Content extraction % (with_summary / total)
```

- [ ] **Step 2: Commit vision document**

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata
git add docs/vision/DATA-VISION.md
git commit -m "docs(WRK-1179): data vision document" && git push
```

- [ ] **Step 3: Update hub submodule pointer**

```bash
cd /mnt/local-analysis/workspace-hub
git add worldenergydata
git commit -m "chore(WRK-1179): update worldenergydata submodule pointer" && git push
```

---

### Task 9: Final Day 15 Review

- [ ] **Step 1: Regenerate coverage report**

```bash
uv run --no-project python scripts/data/document-index/generate-coverage-report.py
```

- [ ] **Step 2: Compare before/after metrics**

Compare data-audit-report.md (Day 1) with current state:
- Content extraction % change
- Standards done/gap counts change
- New data sources ingested count
- WRK items generated count

- [ ] **Step 3: Present results to user**

Summary table: what was achieved, what remains, link to DATA-VISION.md
