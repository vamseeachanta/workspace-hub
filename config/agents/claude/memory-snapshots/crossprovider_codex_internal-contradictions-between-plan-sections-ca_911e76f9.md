---
name: crossprovider codex internal-contradictions-between-plan-sections-ca
description: Internal contradictions between plan sections cause implementation divergence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, correctness, internal-consistency]
---

Plans describe one behavior in Pseudocode (hard-fail, no fallback) and a conflicting behavior in Files-to-Change (argv fallback), or cite incompatible regexes in multiple sections. One source of truth per design decision must propagate everywhere. Detect via consistency audit: Pseudocode vs Files-to-Change vs Risks/Open-Questions vs pseudocode variable definitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
