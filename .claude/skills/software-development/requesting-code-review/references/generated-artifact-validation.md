# Generated artifact validation closeout pattern

Use when a task generates machine-readable artifacts plus a human report (for example JSONL/CSV/summary JSON + Markdown/HTML report).

## Durable lesson

Passing tests against the primary artifact format is not enough. If the task emits multiple synchronized representations, validators must fail closed on every representation and on cross-representation drift.

## Required checks

- Validate every emitted file type, not just the canonical JSON/JSONL:
  - expected headers/schema for CSV/TSV
  - row counts match canonical records
  - required fields are present and non-empty where applicable
  - schema/version fields match expected constants
- Validate summary/report synchronization:
  - metadata counts in report match summary JSON
  - every non-empty gap/warning list in summary appears in the human report
  - report sections exist for every summary gap/warning class, including newly added classes
- Validate public-safety constraints across all generated artifacts and reports:
  - no absolute/private paths
  - no secret-like strings
  - only repo-relative or already-public URLs where allowed
- Add regression tests for validator false negatives before patching validator logic.

## Tool-budget interruption handoff

If context/tool-call limits interrupt this validation loop, do not commit or close. Emit a non-closeout handoff with:

- repo path and branch
- exact dirty/staged files
- targeted test command and current pass/fail count
- each remaining failing test and the implementation gap it proves
- validation gates still missing: regeneration, artifact validator, full tests, legal/public-safety scan, adversarial review, commit/push, issue comment/close
- explicit instruction: `do not close/commit yet`
