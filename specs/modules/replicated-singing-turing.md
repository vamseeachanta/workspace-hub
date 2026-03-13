# WRK-1128: Observed-Exposure Tracker

## Context

Anthropic's labor market research introduces "observed exposure" — the fraction of tasks AI *actually* automates vs what it theoretically could. We have a 20-stage WRK lifecycle where 4 stages (1, 5, 7, 17) are human-gated and 16 are AI-executable, giving 80% theoretical max. This script measures our actual automation rate per WRK category by reading stage-evidence files.

## Plan

### 1. Create `scripts/ai/observed_exposure_report.py`

**Data flow:**
1. Scan WRK `.md` files in `pending/`, `working/`, `archive/**/` — extract `id`, `category` from YAML frontmatter
2. For each WRK, load `assets/WRK-NNN/evidence/stage-evidence.yaml` — extract completed stages (`status: done`)
3. Classify each completed stage: stages 1,5,7,17 = human; rest = AI (mirrors `is-human-gate.sh`)
4. Aggregate by category → output Markdown table

**Functions (reuse `wrk_cost_report.py` patterns):**
- `REPO_ROOT = Path(__file__).parent.parent.parent`
- `QUEUE_ROOT = REPO_ROOT / ".claude/work-queue"`
- `HUMAN_GATE_STAGES = {1, 5, 7, 17}`
- `scan_wrk_files() -> list[dict]` — glob `pending/*.md`, `working/*.md`, `archive/**/*.md`; parse YAML frontmatter for `id`, `category`
- `load_stage_evidence(wrk_id: str) -> list[dict]` — read `assets/{wrk_id}/evidence/stage-evidence.yaml`; return `stages` list
- `classify_stages(stages: list[dict]) -> tuple[int, int, int]` — returns `(total_done, ai_done, human_done)`
- `aggregate_by_category(wrk_data: list[dict]) -> dict[str, dict]` — group and sum
- `format_table(data: dict, include_theoretical: bool) -> str` — Markdown table output
- `main()` — argparse CLI with `--csv` flag

**Output table columns:**
```
| Category | WRKs | Total Stages | AI Stages | Human Stages | Observed Exposure % | Theoretical Max % |
```

Theoretical max per WRK = `(total_completed - human_gates_completed) / total_completed * 100`

### 2. Create `scripts/ai/tests/test_observed_exposure_report.py`

TDD tests (≥3 required, will write ~6):
1. `test_empty_queue` — no WRK files → empty table
2. `test_single_wrk_all_stages_done` — verify correct AI/human split
3. `test_mixed_categories` — multiple categories aggregate correctly
4. `test_partial_stages` — WRK with only some stages done
5. `test_missing_stage_evidence` — WRK exists but no stage-evidence.yaml → skip gracefully
6. `test_csv_output` — CSV mode works

### 3. Update `scripts/ai/README.md`

Add entry for `observed-exposure-report.py` with usage examples.

## Critical Files

| File | Action |
|------|--------|
| `scripts/ai/observed_exposure_report.py` | CREATE |
| `scripts/ai/tests/test_observed_exposure_report.py` | CREATE |
| `scripts/ai/README.md` | EDIT |
| `scripts/ai/wrk_cost_report.py` | READ (pattern reference) |
| `scripts/work-queue/is-human-gate.sh` | READ (stage classification) |
| `.claude/work-queue/assets/*/evidence/stage-evidence.yaml` | READ (data source) |

## Reuse

- `wrk_cost_report.py` pattern: `REPO_ROOT`, argparse, `--csv`, streaming JSONL, `csv.writer`
- `is-human-gate.sh` logic: hardcoded set `{1, 5, 7, 17}`
- YAML frontmatter parsing: simple `yaml.safe_load` on `---` delimited block

## Verification

```bash
# Run TDD tests
uv run --no-project python -m pytest scripts/ai/tests/test_observed_exposure_report.py -v

# Run script on real data
uv run --no-project python scripts/ai/observed_exposure_report.py

# CSV mode
uv run --no-project python scripts/ai/observed_exposure_report.py --csv
```
