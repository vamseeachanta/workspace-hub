# AI Scripts

> AI tools, assessments, and model integration utilities.

Contains AI tool assessment frameworks for evaluating and comparing
AI capabilities across different use cases.

## Scripts

### `observed_exposure_report.py`

Measures observed AI automation rate per WRK category by reading
stage-evidence files and classifying stages as AI or human-gated.

```bash
uv run --no-project python scripts/ai/observed_exposure_report.py        # Markdown table
uv run --no-project python scripts/ai/observed_exposure_report.py --csv  # CSV output
```

### `wrk_cost_report.py`

Aggregates AI token costs by WRK item from cost-tracking JSONL.

```bash
uv run --no-project python scripts/ai/wrk_cost_report.py           # all WRKs
uv run --no-project python scripts/ai/wrk_cost_report.py WRK-NNN  # single WRK
uv run --no-project python scripts/ai/wrk_cost_report.py --csv     # CSV output
```
