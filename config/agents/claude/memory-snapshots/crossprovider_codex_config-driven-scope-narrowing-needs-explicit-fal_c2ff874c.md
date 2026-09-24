---
name: crossprovider codex config-driven-scope-narrowing-needs-explicit-fal
description: Config-driven scope narrowing needs explicit fallback for unmapped entries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-scoping, config-routing, fallback-logic, under-selection-hazard]
---

When a domain/feature detector maps changed config (e.g., pyproject.toml package-data) to known domains via a lookup table, unmapped entries silently return empty set and skip the full-matrix fallback trigger. Example: detect_touched_domains.py returns `set()` for unknown package-data entries at line 227, continuing before the line-235 full-matrix fallback. Fix: return None or a sentinel when entry is unmapped, so full-matrix trigger fires for unknown config changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
