---
name: Auto-sync risk — historical (resolved)
description: Historical incident where auto-sync prematurely closed WRK items — resolved by GSD migration on 2026-03-25
type: project
---

**Status: RESOLVED** — The old WRK auto-sync risk no longer applies after GSD migration (2026-03-25).

**Original incident (2026-03-25):** Auto-sync (chore(sync)) ran the full 20-stage lifecycle on WRK-1357, 1358, 1362, 1363 immediately after creation. Generated fabricated evidence and closed GitHub issues without real work.

**Resolution:** GSD replaced the old pipeline. GSD state lives in `.planning/` and doesn't have an auto-advance mechanism triggered by sync.

**Residual caution:** The nightly `chore(sync)` still runs. If new automated workflows are added, verify they don't auto-advance GSD state.
