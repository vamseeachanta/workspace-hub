# Evidence-threshold approval — evidence ledger (#3296)

Append-only audit records for the **shadow-mode** evidence-threshold eligibility
pilot. Each record makes one (shadow) eligibility decision reconstructable.

- **Policy:** [`../2026-06-28-evidence-threshold-approval-policy.md`](../2026-06-28-evidence-threshold-approval-policy.md)
- **Evaluator:** `scripts/governance/evidence_threshold_eligibility.py` (pure, fail-closed, shadow-mode only — it records, it never applies `status:plan-approved`).
- **Records land in:** `ledger/` (one append-only JSON object per shadow-eligible decision).

## Record schema

Produced by `build_ledger_record(...)`:

| Field | Meaning |
|---|---|
| `reviewed_commit_sha` | commit the decision was computed against |
| `plan_path` | the plan file under review |
| `review_artifact_paths` | the adversarial-review artifacts the metrics were read from |
| `issue_class` | the DERIVED class (`classify()` output) — never caller-supplied |
| `raw_metric_snapshot` | raw metric values as gathered |
| `normalized_metric_snapshot` | metrics after normalization to higher-is-better [0,1] |
| `thresholds` | the normalized thresholds in force at decision time |
| `window_bounds` | the trailing window the metrics were computed over |
| `sample_size` | number of eligible-class issues in the window |
| `decision` | `ELIGIBLE_SHADOW` (shadow-eligible) |
| `decided_at_utc` | ISO-8601 UTC timestamp |
| `mode` | always `"shadow"` — there is no `auto_apply` mode |

## Scope boundary (D6)

This is **governance-internal audit only**. It does NOT define the
envelope-determinism fields (`input_hash`, `result_hash`,
`provenance.code_version`) owned by #3282/#3283, nor the deckhand routing /
`result:` registry descriptor owned by #3282/#3295.

## Reconstruction

To audit a shadow decision: read the JSON record, confirm `reviewed_commit_sha`,
re-read the `review_artifact_paths` at that SHA, and re-run the evaluator with the
recorded `raw_metric_snapshot` + thresholds — the verdict must reproduce.
