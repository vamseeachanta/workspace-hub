---
name: crossprovider gemini per-stage-micro-skills-with-dynamic-loading
description: Per-stage micro-skills with dynamic loading
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [skill-design, cognitive-load, dynamic-loading]
---

Load stage-specific skill files (`stage-{stage:02d}-*.md`) dynamically rather than using one monolithic skill. Reduces cognitive load per stage and allows specialized context/rules for each stage without bloat. Glob pattern prevents nondeterminism; multiple matches raise RuntimeError.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
