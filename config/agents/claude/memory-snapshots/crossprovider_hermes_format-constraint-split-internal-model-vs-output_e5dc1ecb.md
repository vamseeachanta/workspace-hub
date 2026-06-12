---
name: crossprovider hermes format-constraint-split-internal-model-vs-output
description: Format-constraint split: internal model vs output text
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-architecture, output-constraints, contracts, design]
---

When spec forbids JSON/XML in user output but internal manifest is JSON/YAML, keep model intact and patch only output strings per format type (HTML text, CSV, keys separately). Prevents constraint creep into data architecture.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
