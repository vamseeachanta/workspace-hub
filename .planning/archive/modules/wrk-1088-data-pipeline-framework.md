---
wrk_id: WRK-1088
title: "Data Pipeline Framework — Consistent ETL for EIA, BSEE, yfinance"
route: C
status: draft
---

# WRK-1088: Data Pipeline Framework

## Context

worldenergydata has one-off patterns for EIA ingestion (client + incremental JSONL) and BSEE loading (router + strategy + Pydantic schemas). assethold uses yfinance directly with a dual-cache fetcher. Each is a custom pattern with no shared ETL abstraction. This WRK creates a lightweight, reusable framework at hub level so future datasets follow a single extract→transform→load pattern with incremental state, schema validation, and deterministic testing.

## Architecture

ABC base classes (Extractor/Transformer/Loader) + PipelineOrchestrator + PipelineState + ManifestManager. Pipelines are thin wrappers around existing repo clients (e.g., `EIAFeedClient`), not reimplementations.

## File Tree (17 production + 10 test files)

```
scripts/data/pipeline/
    __init__.py
    base.py                  # Extractor, Transformer, Loader ABCs (~120 lines)
    pipeline.py              # PipelineOrchestrator — E→T→L chain (~150 lines)
    manifest.py              # ManifestManager — atomic YAML read/update (~100 lines)
    state.py                 # PipelineState — JSON state per pipeline (~80 lines)
    pipelines/
        __init__.py
        eia_production.py    # EIA petroleum production (~180 lines)
        bsee_wells.py        # BSEE well records (~180 lines)
        yfinance_prices.py   # yfinance OHLCV with fixture fallback (~180 lines)
    run-pipeline.sh          # Shell runner (~40 lines)

tests/data/pipeline/
    __init__.py
    conftest.py
    test_base.py
    test_pipeline.py
    test_manifest.py
    test_state.py
    test_eia_production.py
    test_bsee_wells.py
    test_yfinance_prices.py
    fixtures/
        eia_response.json
        bsee_wells_sample.csv
        yfinance_ohlcv.json

config/data/
    pipeline-manifest.yaml   # Committed, updated on each run
    pipeline-state/.gitkeep  # Dir committed, *.json gitignored
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ABC vs Protocol | ABC | Explicit inheritance, clear TypeError on missing methods |
| State location | `config/data/pipeline-state/` | `scripts/` = code only; state is runtime data (gitignored) |
| Manifest update | `os.replace()` (atomic POSIX) | Prevents corrupt manifest on crash |
| Schema location | Inline in each pipeline file | Co-located, each file stays under 200 lines |
| Test structure | One file per module | Clear failure isolation |

## Class Interfaces

### base.py — ABCs

```python
class Extractor(ABC):
    def extract(self, force_refresh: bool = False) -> Any: ...
    def cache_key(self) -> str: ...

class Transformer(ABC):
    def transform(self, raw: Any) -> pd.DataFrame: ...

class Loader(ABC):
    def load(self, df: pd.DataFrame) -> Path: ...
    def output_path(self) -> Path: ...
```

### pipeline.py — Orchestrator

```python
class PipelineOrchestrator:
    def __init__(self, extractor, transformer, loader, state, manifest): ...
    def run(self, force_refresh=False) -> dict:
        # Returns {record_count, output_path, skipped}
```

### state.py — Modeled on EIAIngestionState

```python
class PipelineState:
    def get(self, pipeline_name: str) -> Optional[dict]: ...
    def save(self, pipeline_name: str, last_value: str,
             record_count: int, run_at: str) -> None: ...
```

## Pipeline Implementations

| Pipeline | Extractor source | Schema (Pydantic) | Output |
|----------|-----------------|-------------------|--------|
| eia_production | `EIAFeedClient.fetch_petroleum_weekly()` | `EIAProductionRecord(period, value, series_id)` | JSONL |
| bsee_wells | BSEE public CSV download / local cache | `BSEEWellRecord` (ConfigDict, field_validators) | CSV |
| yfinance_prices | `yfinance.download()` or fixture JSON | `OHLCVRecord(date, open, high, low, close, volume)` | CSV per ticker |

## TDD Build Sequence

### Phase 1: Framework (test first, then implement)
1. `test_base.py` → `base.py` — ABC contract tests
2. `test_state.py` → `state.py` — get/save roundtrip, JSON persistence
3. `test_manifest.py` → `manifest.py` — read empty, update, atomic write
4. `test_pipeline.py` → `pipeline.py` — mock E/T/L, skip-if-fresh, force-refresh

### Phase 2: Pipelines (test first, then implement)
5. `test_eia_production.py` → `eia_production.py` — mock HTTP, schema validation
6. `test_bsee_wells.py` → `bsee_wells.py` — fixture CSV, Pydantic coercion
7. `test_yfinance_prices.py` → `yfinance_prices.py` — sys.modules mock, fixture fallback

### Phase 3: Runner & config
8. `run-pipeline.sh` — dispatch to `uv run --no-project python`
9. `config/data/pipeline-manifest.yaml` — initial empty manifest
10. `.gitignore` additions for `config/data/pipeline-state/*.json`

## Key Patterns Reused

- **EIAIngestionState** (`ingestion.py:39-86`): JSON state file → `state.py`
- **EIAFeedClient delegation** (`client.py`): wrap, don't reimplement → `eia_production.py`
- **Pydantic + field_validator** (`schemas/platform.py`): `ConfigDict(str_strip_whitespace=True)` → all schemas
- **Optional import + fixture fallback** (`fetcher.py:22-25`): `try: import yfinance` → `yfinance_prices.py`
- **Runner with exit codes** (`ingestion_runner.py`): argparse + exit 0/1/2 → `run-pipeline.sh`

## Test Execution

```bash
PYTHONPATH="scripts:worldenergydata/src:assethold/src" \
  uv run --no-project python -m pytest tests/data/pipeline/ -v --tb=short
```

## Verification

1. All tests pass: `uv run --no-project python -m pytest tests/data/pipeline/ -v`
2. Runner dry-run: `bash scripts/data/pipeline/run-pipeline.sh eia_production --force-refresh`
3. Manifest updated: `cat config/data/pipeline-manifest.yaml`
4. Legal scan: `scripts/legal/legal-sanity-scan.sh`
5. Cross-review: `scripts/review/cross-review.sh <file> all`

## Critical Files to Read During Implementation

- `worldenergydata/src/worldenergydata/eia/ingestion.py` — state tracking pattern
- `worldenergydata/src/worldenergydata/eia/client.py` — EIA client to wrap
- `worldenergydata/src/worldenergydata/bsee/data/schemas/platform.py` — Pydantic pattern
- `assethold/tests/unit/analysis/daily_strategy/test_fetcher.py` — yfinance mock pattern
- `worldenergydata/src/worldenergydata/eia/ingestion_runner.py` — CLI runner pattern
