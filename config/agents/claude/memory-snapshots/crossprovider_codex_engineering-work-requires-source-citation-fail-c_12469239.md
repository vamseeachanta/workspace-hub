---
name: crossprovider codex engineering-work-requires-source-citation-fail-c
description: Engineering work requires source/citation fail-close gates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [engineering, tdd, source-control]
---

Physics/engineering calculations (OCIMF coefficients, hydrodynamic models, empirical data) cannot use placeholder/invented data if sources are unavailable. TDD must test citation provenance and source availability, not just calculation results. If a required source cannot be pinned before implementation, add a fail-close gate and block rather than substituting approximations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
