---
name: crossprovider codex physics-based-test-coverage-must-exercise-all-no
description: Physics-based test coverage must exercise all non-zero correction terms
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, physics-testing, viv-fatigue, regression-detection]
---

Tests for physics calculators can have gaps in branch coverage (axial force terms, seabed-proximity effects, fatigue pathways) that hide model behavior changes. Comprehensive coverage requires explicit test cases for each correction term's contribution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
