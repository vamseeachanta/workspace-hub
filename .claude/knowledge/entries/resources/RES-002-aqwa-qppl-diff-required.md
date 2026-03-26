---
id: RES-002
type: resource
entry_type: procedure
title: "AQWA elements must use QPPL DIFF for diffraction analysis"
category: data
domain:
  primary: hydrodynamics
  sub_domain: diffraction
tags: [aqwa, diffraction, qppl, dat-format, mesh]
repos: [digitalmodel]
confidence: 0.95
created: "2026-03-25"
last_validated: "2026-03-25"
source:
  name: "AQWA User Manual"
  source_kind: manual
  section: "Element type specification"
  edition: "2024R1"
  retrieved: "2026-02-22"
provenance:
  method: manual
  reviewed_by: vamsee
  review_date: "2026-03-25"
related: [GOT-002, RES-001]
ttl_days: 365
status: active
access_count: 0
file: ".claude/knowledge/entries/resources/RES-002-aqwa-qppl-diff-required.md"
---

# RES-002: AQWA elements must use QPPL DIFF for diffraction analysis

## Procedure
When setting up an AQWA DAT input file for diffraction analysis:

1. Elements must be declared with `QPPL DIFF` (not just `QPPL`)
2. Using `QPPL` alone performs only Morison-based loading — no panel pressure integration
3. `OPTIONS GOON` continues past non-fatal errors but does **NOT** bypass mesh FATAL errors
4. Executable path: `$AQWA_HOME/bin/winx64/Aqwa.exe` (set `AQWA_HOME` env var)

## Common Pitfall
If RAO results from AQWA look unreasonable or zero, the first thing to check is whether `DIFF` was included in the element type declaration. This is the most frequent source of silent wrong-results.
