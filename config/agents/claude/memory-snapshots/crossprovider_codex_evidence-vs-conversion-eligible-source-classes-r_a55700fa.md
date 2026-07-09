---
name: crossprovider codex evidence-vs-conversion-eligible-source-classes-r
description: Evidence vs. conversion-eligible source classes require explicit enum mapping
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [data-quality, source-classification, provenance]
---

Phrases like 'industry annual survey' or 'secondary source' are too vague. Plans must define a source-class enum (e.g., `regulator`, `operator`, `assay`, `technical_literature`) and explicitly state which are conversion-eligible (drive conversion factors) vs. evidence-only (support but don't drive). Reject ambiguous hybrids.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
