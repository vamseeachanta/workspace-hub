---
name: crossprovider gemini config-loader-paths-are-hidden-mutations-in-dire
description: Config loader paths are hidden mutations in directory renames
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture-hazard, review-gate, dynamic-loading]
---

When renaming directories that are loaded dynamically (e.g., `base_configs/modules/` loaded by `config_framework.py` via string path), the path changes are invisible in surface-level diffs. These changes require explicit code review gates separate from structural/documentation changes. WRK-204 audit identified this as critical for runtime safety.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
