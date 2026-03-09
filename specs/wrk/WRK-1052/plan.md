# WRK-1052 Plan: Log model/context/effort at session start

## Approach

**Route A — Simple**. Two changes:
1. New helper script `scripts/ai/session-params.py` — reads all 3 provider configs, outputs JSONL
2. Patch `.claude/hooks/session-logger.sh` — emit session_params lines on first write of daily log

## Files

| Action | File |
|--------|------|
| CREATE | `scripts/ai/session-params.py` |
| PATCH  | `.claude/hooks/session-logger.sh` |

## Design

### session-params.py
- Reads `~/.claude/settings.json` (model + thinking), `.codex/config.toml` (model + effort), `~/.gemini/settings.json` (model + thinking_budget)
- Same CTX_MAP as ai-usage-summary.sh (reuse logic)
- Outputs one JSONL line per provider to stdout:
  ```jsonl
  {"event":"session_params","provider":"claude","model":"claude-sonnet-4-6","context_k":200,"effort":"thinking=off","ts":"..."}
  ```
- Graceful: missing config → emits line with `"model":"not-set"`

### session-logger.sh patch
- After mkdir / before writing ENTRY: if log file is empty/new, call session-params.py and prepend lines
- Dual-write to both state/sessions and orchestrator log
- Runs via `uv run --no-project python` per python-runtime.md

## Tests/Evals

| ID | Test | Expected |
|----|------|----------|
| T1 | `test_session_params_output`: run `session-params.py` with real config | 3 JSONL lines, each with event/provider/model/context_k/effort/ts keys |
| T2 | `test_session_params_missing_config`: run with HOME pointing to empty temp dir | 3 graceful lines with `model: not-set`, no crash |
| T3 | `test_session_logger_emits_params`: call session-logger.sh with empty log file | session_params lines appear before first tool event |
