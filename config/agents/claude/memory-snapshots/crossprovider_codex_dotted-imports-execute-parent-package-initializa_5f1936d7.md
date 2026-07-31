---
name: crossprovider codex dotted-imports-execute-parent-package-initializa
description: Dotted imports execute parent package initialization chains
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [python-imports, package-structure, refactoring-hazards, logging]
---

Moving code from file-path imports (spec_from_file_location) to dotted imports exposes parent package __init__.py execution. This can trigger unexpected side effects (eager subsystem imports, network calls, third-party initialization) that were previously bypassed. Logger __name__ also changes, breaking existing filter configurations. Multiprocessing.spawn also repeats initialization in child processes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
