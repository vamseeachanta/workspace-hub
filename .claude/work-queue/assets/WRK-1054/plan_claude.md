# WRK-1054 Plan (Revised — Claude, post cross-review)

## Architecture
- `scripts/testing/run-all-tests.sh` — bash orchestrator
- `scripts/testing/parse_pytest_output.py` — Python helper (exit code + raw output → JSONL)
- `scripts/testing/expected-failures.txt` — exact node IDs (initially empty)

## v1 Scope: 4 repos
assetutilities, digitalmodel, worldenergydata, assethold. ogmanufacturing excluded.

## Step 1 — run-all-tests.sh
Repo config table; iterate repos; capture output + exit code; invoke parse_pytest_output.py; collect JSONL; print markdown table.

## Step 2 — parse_pytest_output.py
Handle all pytest exit codes (0-5). Parse summary line with regex. Fall back on missing.
Load expected-failures.txt; compute unexpected = failed_node_ids - expected_set.
Emit single JSONL record per repo.

## Step 3 — expected-failures.txt
Exact node IDs. Initially empty. Populated after first run.

## Step 4 — Output
Markdown table + aggregate. Flags: --repo, --json-out.

## Step 5 — Exit code
0 iff unexpected_failures == 0 and no error-status repos.

## Step 6 — TDD
tests/testing/test_parse_pytest_output.py: all exit-code paths, edge cases.

## Step 7 — Cross-review
Implementation cross-review via Codex after code is written.
