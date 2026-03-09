# WRK-1023 Plan — Per-Provider Model/Effort Summary in Daily Cron

## Route
A (simple) — single file change, ace-linux-1 only.

## Implementation
Replace hardcoded "Models in Use" section in `scripts/productivity/sections/ai-usage-summary.sh`
with a live "Active Provider Config" block that reads from:
- Claude: `~/.claude/settings.json` → `model` field
- Codex: repo `.codex/config.toml` (overrides user config) → `model` + `model_reasoning_effort`
- Gemini: `~/.gemini/settings.json` → `model.name`

Uses inline Python (no external deps) to parse JSON and TOML with regex fallback.
Graceful: prints `not set` if config missing.

## Test
Run `bash scripts/productivity/sections/ai-usage-summary.sh` and confirm new section appears.
