---
name: crossprovider codex executable-build-test-commands-must-be-self-cont
description: Executable build/test commands must be self-contained
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [script-design, ci-cd, reproducibility]
---

Commands in checklists or documentation that depend on side effects from earlier commands (e.g., wheel acceptance depending on $tmp_dir from a separate checklist command) cannot be independently verified or re-run. Each command should create and clean its own temporary state. Make dependencies explicit via parameters, not shared environment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
