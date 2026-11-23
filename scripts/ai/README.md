# AI Scripts

> AI tools, assessments, and model integration utilities.

Contains AI tool assessment frameworks for evaluating and comparing
AI capabilities across different use cases.

## Scripts

### `context_budget.py`

Accounts for an explicit context observation, with tool results nested inside
messages. Reports unmeasured prose savings as `NOT_EVALUATED`.

```bash
uv run --no-project python scripts/ai/context_budget.py docs/examples/context-budget.json
```

See [bounded tool output guidance](../../docs/standards/BOUNDED_TOOL_OUTPUT.md)
for the input schema, method, worked example and limits of the reported evidence.

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
