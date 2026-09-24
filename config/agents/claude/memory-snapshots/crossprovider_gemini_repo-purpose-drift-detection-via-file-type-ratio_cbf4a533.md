---
name: crossprovider gemini repo-purpose-drift-detection-via-file-type-ratio
description: Repo purpose drift detection via file-type ratio
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci, repo-health, governance]
---

Large shifts in code-to-markup ratio (e.g., 495 markdown : 12 Python files) indicate repo has transitioned its primary purpose. CI scope should follow active usage patterns, not original intent. Justify changes truthfully: 'Python scaffolding tracked but unused; active traffic is markdown' rather than false claims about absence.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
