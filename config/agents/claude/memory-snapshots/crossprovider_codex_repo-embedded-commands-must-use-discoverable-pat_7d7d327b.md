---
name: crossprovider codex repo-embedded-commands-must-use-discoverable-pat
description: Repo-embedded commands must use discoverable paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [documentation, discoverability, usability]
---

Validation/verification commands embedded in markdown summaries must use repo-relative paths or absolute positions (e.g., `scripts/ingest/abs_static_manifest.py` not bare `abs_static_manifest.py`), else readers cannot rerun them from repo root.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
