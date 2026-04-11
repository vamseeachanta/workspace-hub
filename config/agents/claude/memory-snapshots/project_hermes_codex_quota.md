---
name: project_hermes_codex_quota
description: Hermes Codex quota tracking — #6551 done 2026-04-09, stale-state fix 2026-04-10, follow-ups #2107-2109 + #6564-6567
type: project
originSessionId: 02ac3add-e23c-497d-ba18-256a6a5d40cd
---
Implemented NousResearch/hermes-agent#6551 on 2026-04-09 — all 8 acceptance criteria done.

**Why:** Codex weekly usage limits caused silent failures with no early warning; bad base_url values (like "h-which") could poison config; global model switches left stale base_url residue.

**Stale exhaustion fix (2026-04-10):** After weekly reset, false warnings persisted because exhaustion state lived in 3 layers (auth.json error fields, ~/.cache/agent-quota.json synthetic entries, codex_quota.py state). Fixed `build_codex_quota_state()` and `_check_pool_health()` with reset-time recovery, error-message detection, and 12h cache expiry.

**How to apply:** Changes are in `~/.hermes/hermes-agent/` (local, not pushed). Key module: `hermes_cli/codex_quota.py`. Follow-ups: #6564-6567 (upstream), #2107 (auto-clear), #2108 (cache cron), #2109 (test coverage).
