---
name: crossprovider codex hf-dataset-readiness-separates-maturity-tiers
description: HF dataset readiness separates maturity tiers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [huggingface, data-release, reproducibility]
---

Datasets exist in three distinct states: committed HF-ready exports (reproducible from repo), locally-generated-but-gitignored builds (undatable, schema-drifted), and discovery spines (metadata only). 'Present in checkout' does not equal 'durably publishable'—every export candidate must validate source regenerability, schema versioning, and license/provenance consistency before promotion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
