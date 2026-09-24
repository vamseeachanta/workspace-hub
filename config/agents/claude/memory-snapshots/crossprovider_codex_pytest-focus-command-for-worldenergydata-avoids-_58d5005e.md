---
name: crossprovider codex pytest-focus-command-for-worldenergydata-avoids-
description: Pytest focus command for worldenergydata avoids slow conftest and coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, pytest, performance]
---

Use `pytest -p no:cov --noconftest` for focused runs in worldenergydata to skip conftest loading and coverage startup. XLSX I/O is slow in this repo; cache workbook reads within a session rather than re-opening.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
