---
name: crossprovider gemini traceability-check-uses-12-hour-git-window-as-se
description: Traceability check uses 12-hour git window as session proxy
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [traceability, git-integration, session-scoping]
---

wrk-traceability-check.sh sums both uncommitted changes and commits from the last 12 hours to detect session work. This is a heuristic; true session-scoping requires session-start timestamp infrastructure (noted as future improvement in WRK-285 follow-up).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
