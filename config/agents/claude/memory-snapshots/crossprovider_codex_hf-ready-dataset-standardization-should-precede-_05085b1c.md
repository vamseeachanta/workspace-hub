---
name: crossprovider codex hf-ready-dataset-standardization-should-precede-
description: HF-ready dataset standardization should precede HTML and well drill-down rollout
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [data-architecture, huggingface, schema-design]
---

For multi-facet data surfaces (HF export, HTML pages, well drill-down), standardize the primary structured format (14-column CSV for BSEE fields) first, then use that manifest to drive secondary surfaces. Publishing HTML without standardized HF backing creates two sources of truth and complicates updates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
