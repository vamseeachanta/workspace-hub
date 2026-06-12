---
name: crossprovider codex documentation-can-diverge-from-runtime-when-logi
description: Documentation can diverge from runtime when logic lives in multiple places
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [documentation-drift, maintenance, WRK-1053, WRK-1105]
---

WRK-1053 Phase 9 declared in SKILL.md, executed in shell runner, AND implemented in Python code — three authorities that can fall out of sync. WRK-1053 skill-eval docs point to validate-skills.sh instead of skill-coverage-audit.sh. Pick one source of truth (e.g., Python is implementation), or enforce strict sync tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
