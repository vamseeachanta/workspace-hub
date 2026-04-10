---
name: project_hermes_codex_quota
description: Hermes #6551 Codex quota tracking and base_url hardening — implemented 2026-04-09, changes local only (not pushed)
type: project
originSessionId: 6c98825e-8e93-4281-b3cd-7718eb7294a7
---
Implemented NousResearch/hermes-agent#6551 on 2026-04-09 — all 8 acceptance criteria done.

**Why:** Codex weekly usage limits caused silent failures with no early warning; bad base_url values (like "h-which") could poison config; global model switches left stale base_url residue.

**How to apply:** Changes are in `~/.hermes/hermes-agent/` (local, not pushed). Key new module: `hermes_cli/codex_quota.py`. Follow-up issues: #6564 (API header wiring), #6565 (gateway support), #6566 (extended validation), #6567 (configurable thresholds).
