---
name: crossprovider codex architecture-layer-separation-data-execution-rep
description: Architecture layer separation: data → execution → report → curated-learning
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [architecture, layering, data-boundaries]
---

Layered architecture with strict boundaries: A-DATA owns source truth/residency, A-EXEC owns tool/compute evidence (never raw data ownership), A-REPORT owns audience surfaces, A-CURATED-LEARNING owns promoted knowledge only after gates. Each transition requires explicit promotion gate; raw/private data must not route directly to public surfaces; fail closed by default.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
