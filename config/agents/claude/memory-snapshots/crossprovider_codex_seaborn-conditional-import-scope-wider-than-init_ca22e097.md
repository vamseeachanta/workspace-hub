---
name: crossprovider codex seaborn-conditional-import-scope-wider-than-init
description: Seaborn/conditional-import scope wider than initial site
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, code-review, import-management]
---

When fixing unconditional module-level imports to be lazy/conditional, grep widely across src/ and tests/. Single-site fixes (e.g., ocimf.py only) miss duplicates in plotContour.py, visualizer.py, integration_charts.py, ocimf_charts.py, validate_phase2.py. One fixed site + many unfixed = CI still fails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
