---
name: crossprovider gemini canonical-data-generated-documentation-requires-
description: Canonical data + generated documentation requires automated drift validation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [state-management, validation, automation, yaml-markdown]
---

When splitting state across YAML (canonical source) and Markdown (generated), manual linkage creates silent drift risk. Solution: require automated `--check` scripts (e.g., `sync-maturity-summary.py --check`) that fail if Markdown diverges from YAML. The check runs before acceptance gates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
