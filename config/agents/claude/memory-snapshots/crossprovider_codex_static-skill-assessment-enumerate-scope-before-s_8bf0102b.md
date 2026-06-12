---
name: crossprovider codex static-skill-assessment-enumerate-scope-before-s
description: Static skill assessment: enumerate scope before scoring
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [static-analysis, scope-boundaries, assessment-methodology]
---

When performing static analysis of multiple interdependent components (skills, lifecycle stages), enumerate the full scope set and document boundaries explicitly first. Adjacent items excluded from scope can be material to overlap/delta scores and merge recommendations. WRK-1010 excluded plan-mode and workflow-html from assessment but then used them to justify merge recommendations, leaving scoring unsupported.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
