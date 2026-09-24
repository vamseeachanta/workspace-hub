---
name: crossprovider codex making-a-required-input-optional-with-fallback-d
description: Making a required input optional with fallback defeats its purpose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, requirements-enforcement, catalog-segmentation]
---

If a feature like catalog-based segmentation requires a mandatory input (e.g., `--docs-master-catalog`), do not make it optional with a silent fallback to nominal behavior. Fallback paths undermine the whole fix and are difficult to detect in review. Enforce the requirement at the entry point and fail early and loudly if the input is missing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
