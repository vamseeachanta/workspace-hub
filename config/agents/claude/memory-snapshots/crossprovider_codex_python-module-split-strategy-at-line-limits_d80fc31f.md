---
name: crossprovider codex python-module-split-strategy-at-line-limits
description: Python module split strategy at line limits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-organization, python, maintainability]
---

When implementation modules reach the 400-line soft cap, continue splitting into separate modules rather than optimizing code density. Modules at 398–400 lines indicate further feature work should create split modules instead of expanding existing ones.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
