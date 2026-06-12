---
name: crossprovider gemini doc-recommendations-are-not-enforcement-pyprojec
description: Doc recommendations are not enforcement; pyproject.toml is source of truth
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [dependency-management, documentation-vs-config, ci-enforcement]
---

Integration guides and evaluation documents can recommend a dependency (e.g., `pylife>=2.2`) without triggering CI enforcement. Missing-dep failures only surface at import time in tests. Explicit `pyproject.toml` entries are the enforcement boundary.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
