---
name: crossprovider codex acceptance-criteria-must-align-with-actual-execu
description: Acceptance criteria must align with actual execution scope
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [acceptance-criteria, scope, WRK-1016, WRK-1071]
---

WRK-1016 acceptance criteria say 'all settings files' but plan covers only .claude/settings, harness markdown, hooks, plugins, pyproject.toml — missing pre-commit, uv.toml, .vscode/settings.json, cron config. Mismatch causes gate failure or scope creep mid-work. Narrow criteria to match execution or expand plan to match criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
