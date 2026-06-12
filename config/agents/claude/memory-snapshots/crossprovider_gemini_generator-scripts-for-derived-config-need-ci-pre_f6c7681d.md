---
name: crossprovider gemini generator-scripts-for-derived-config-need-ci-pre
description: Generator scripts for derived config need CI/pre-commit automation
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [automation, ci-cd, configuration-management, drift-prevention]
---

WRK-1073: Hand-running generator scripts (e.g., generate-repo-map.py) for derived configuration (repo-map.yaml) leads to drift when source files (AGENTS.md) are updated. Integrate into CI pipeline or pre-commit hook to auto-regenerate and validate.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
