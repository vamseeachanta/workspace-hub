# WRK-1023 Self-Review (Route A — Claude)

**Verdict**: APPROVE

## Changes
- Replaced hardcoded "Models in Use" table in `ai-usage-summary.sh` with live "Active Provider Config" block
- Reads: Claude `~/.claude/settings.json` (model + thinking), Codex `config.toml` (model + effort), Gemini `settings.json` (model)
- Added context window map (model alias → K tokens) — shows 200K/128K/1000K
- Graceful on missing configs

## P1: None
## P2: None
## P3
- Context window sizes are hardcoded map (not queried from API) — acceptable; these are stable published values
- Gemini thinking_budget not yet exposed in settings.json — shows "—" for now; correct behavior

## Codex Note
Route A self-review only — no Codex cross-review required for simple single-file change.
Codex would verify: context map accuracy, graceful fallback, TOML parsing correctness.
