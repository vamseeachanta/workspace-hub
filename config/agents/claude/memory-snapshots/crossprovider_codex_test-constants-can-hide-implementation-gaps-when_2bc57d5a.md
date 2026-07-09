---
name: crossprovider codex test-constants-can-hide-implementation-gaps-when
description: Test constants can hide implementation gaps when they match fallback values
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [test-coverage]
---

A test asserting `loader.oil_bbl == 7.33` passes whether the code uses the package registry or silently falls back to legacy `TONNES_TO_BBL`, because both have value 7.33. Verify *how* the value was computed, not just its final value—assert on provenance metadata like `audit.coverage_status` or `audit.defaulted_fields`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
