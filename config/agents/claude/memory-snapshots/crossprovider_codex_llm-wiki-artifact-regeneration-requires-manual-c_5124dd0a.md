---
name: crossprovider codex llm-wiki-artifact-regeneration-requires-manual-c
description: llm-wiki artifact regeneration requires manual command tracking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, build-process, stale-state]
---

Changing GitHub issue labels requires regenerating downstream artifacts via specific commands (readiness_matrix.py, domain_parent_delta_audit.py, completeness_score.py). No automatic rebuild. Stale-artifact cascades are a real hazard; encode regeneration into test suite or build step to enforce freshness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
