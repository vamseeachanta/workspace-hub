---
wrk_id: WRK-1101
title: Extend detect-drift.sh to parse Codex JSONL log format
route: B
---

# WRK-1101 Plan: Codex JSONL Support for detect-drift.sh

## Context

`detect-drift.sh` scans session logs for rule violations (python_runtime, file_placement, git_workflow). It currently only handles Claude's flat JSONL format (`{"cmd": "...", "path": "..."}`). Codex logs at `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` use an envelope format with double-parsed arguments. This blocks Phase 1b comprehensive-learning from covering Codex sessions.

## Implementation Steps (TDD order)

### 1. Create 3 Codex test fixtures
**Dir**: `scripts/session/tests/fixtures/`

| Fixture | Contents |
|---------|----------|
| `codex-session-with-violations.jsonl` | bare python3, file write to src/*/tests/*, non-conventional commit + noise records |
| `codex-session-clean.jsonl` | uv run python, conventional commit with WRK ref, git status |
| `codex-session-compound-cmd.jsonl` | `uv run something && python3 bar.py` |

Format: `{"timestamp":"...","type":"response_item","payload":{"type":"function_call","name":"exec_command","arguments":"{\"cmd\":\"...\"}"}}`

### 2. Extend test_detect_drift.sh
- Modify `run_test()` to accept optional 5th arg (`extra_flags`) — backwards compatible
- Add 7 Codex test cases covering all 3 violation patterns + clean + compound

### 3. Add `--provider` flag to detect-drift.sh
- New variable `PROVIDER="claude"` with `--provider) PROVIDER="$2"; shift 2` in parser
- Validate: must be `claude` or `codex`

### 4. Add Codex Python extractor (`PY_EXTRACT_CODEX`)
- Filter: `type == "response_item"` → `payload.type == "function_call"` → `payload.name == "exec_command"`
- Double-parse: `json.loads(payload["arguments"])` → extract `cmd`
- python_runtime: reuse `is_python3_violation()` (duplicated — acceptable at ~10 lines)
- file_placement: regex for write patterns (`>`, `tee`, `cat >`, `touch`, `cp`, `mv`) → check path for `src/` + `/tests/`
- git_workflow: same commit message extraction as Claude extractor
- Output: identical 3-line format (`python_runtime=N`, `file_placement=N`, `git_cmds=...`)

### 5. Provider-conditional dispatch
```bash
if [[ "$PROVIDER" == "codex" ]]; then
    result=$(uv run --no-project python -c "$PY_EXTRACT_CODEX" "$LOG_FILE" 2>/dev/null)
else
    result=$(uv run --no-project python -c "$PY_EXTRACT" "$LOG_FILE" 2>/dev/null)
fi
```
All downstream bash logic unchanged.

### 6. Add `provider` field to YAML output
Include `$PROVIDER` in the drift-summary.yaml append.

### 7. Wire Phase 1b into nightly cron
**File**: `scripts/cron/comprehensive-learning-nightly.sh`
- Add step scanning `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` for yesterday
- Loop over all session files, call `detect-drift.sh --log <file> --provider codex`

### 8. Update pipeline-detail.md
- Add Codex log path, `--provider codex` flag, nightly iteration docs

## Critical Files

| File | Action |
|------|--------|
| `scripts/session/detect-drift.sh` | MODIFY — add --provider, Codex extractor, conditional dispatch |
| `scripts/session/tests/test_detect_drift.sh` | MODIFY — extend run_test(), add 7 Codex tests |
| `scripts/session/tests/fixtures/codex-session-*.jsonl` | CREATE — 3 fixtures |
| `scripts/cron/comprehensive-learning-nightly.sh` | MODIFY — add Phase 1b Codex step |
| `.claude/skills/.../comprehensive-learning/references/pipeline-detail.md` | MODIFY — document Codex support |

## Verification

1. `bash scripts/session/tests/test_detect_drift.sh` — all tests pass (10 existing + 7 new)
2. Manual run against real Codex session with `--provider codex --no-git`
3. `wc -l scripts/session/detect-drift.sh` — under 400 lines (~200 expected)
4. Backwards compat: run without `--provider` → identical output to current version
