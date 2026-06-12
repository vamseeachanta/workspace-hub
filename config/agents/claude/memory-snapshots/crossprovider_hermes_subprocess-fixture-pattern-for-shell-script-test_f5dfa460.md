---
name: crossprovider hermes subprocess-fixture-pattern-for-shell-script-test
description: Subprocess fixture pattern for shell script testing without editing production
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, subprocess-fixtures, shell-scripts, isolation]
---

Safe, reusable pattern: (1) copy script to temp repo with self-derived paths, (2) mock upstream binaries (uv, python) via fake PATH entry, (3) set HOME to temp home with fixtures, (4) run subprocess, (5) assert behavior + state files. Avoids editing production, works for any shell CLI, fixtures are cheap and composable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
