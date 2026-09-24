---
name: crossprovider codex pytest-tool-constraints-determine-fixture-locati
description: Pytest tool constraints determine fixture location strategy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, fixtures, testing, discovery]
---

Flags like `--noconftest` suppress root conftest.py. Discover tool constraints upfront and design fixture locations accordingly (e.g., per-subdirectory conftest for --noconftest mode). Constraints change where fixtures can live, not just how they're used.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
