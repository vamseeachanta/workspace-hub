# WRK-1069 Plan: Per-WRK Token Cost Attribution

## Mission
Attribute AI token usage to specific WRK items so cost-per-WRK is visible.

## What
- `config/ai-tools/pricing.yaml` — static pricing table per model (input/output per 1M tokens)
- `scripts/ai/wrk_cost_report.py` — aggregation CLI: reads cost-tracking.jsonl, groups by wrk_id
- `scripts/work-queue/close-item.sh` — non-blocking cost summary hook at WRK close

## Why
Enable ROI comparison across Route A/B/C WRKs. Cost transparency drives better routing decisions.

## Phase 1 — pricing.yaml + AC-1 verification
- Confirm cost-tracking.jsonl schema includes wrk, cost_usd, input_tokens, output_tokens
- Create config/ai-tools/pricing.yaml with 8 models + defaults

## Phase 2 — wrk-cost-report.py
- Streaming JSONL reader (line by line)
- aggregate_by_wrk(): parse numerics before bucket creation
- format_cost_table(): table + CSV mode (csv.writer for escaping)
- Exit codes: 0=data, 1=no-data, 2=missing-file

## Phase 3 — close-item.sh integration
- Non-blocking cost block (suppress exit 1 only, warn on others)
- Write cost-summary.yaml evidence artifact

## Tests / Evals
| # | What | Type | Expected |
|---|------|------|----------|
| T1 | load_records all valid lines | happy | 3 records returned |
| T2 | load_records skips malformed JSON | edge | skipped=1 |
| T3 | load_records skip count | happy | skipped=0 |
| T4 | aggregate sums tokens + cost | happy | WRK-100 row correct |
| T5 | aggregate empty input | edge | empty dict |
| T6 | filter by wrk_id | happy | only matching WRK |
| T7 | missing wrk field → unattributed | edge | unattributed bucket |
| T8 | format_cost_table headers | happy | WRK-ID/INPUT/COST_USD |
| T9 | format skipped count | happy | skipped footer shown |
| T10 | load_records missing file | error | ([], 0) |
| T11 | non-numeric fields skip + no orphan bucket | edge | WRK-BAD absent |
| T12 | csv mode valid csv output | happy | parseable CSV |
| T13 | csv mode skipped goes to stderr | edge | not in stdout |

## Risks / Out of Scope
- Out of scope: real-time streaming, UI dashboard, cross-machine JSONL aggregation
- Risk: active-wrk not set → wrk field blank → handled by unattributed bucket
