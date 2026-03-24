# Cross-Review — Codex — WRK-1075 Plan v2

**Verdict: REQUEST_CHANGES**

## Issues Addressed in v3
- Rollback policy not CI-safe → fixed: mkdocs.yml presence = enable flag; CI uses `hashFiles`
- AC contradiction → fixed: ACs now say "enabled repos" consistently
- --serve test underspecified → fixed: SIGTERM after 3s + assert process state
