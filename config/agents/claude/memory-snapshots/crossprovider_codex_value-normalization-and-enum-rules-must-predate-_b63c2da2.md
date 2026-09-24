---
name: crossprovider codex value-normalization-and-enum-rules-must-predate-
description: Value normalization and enum rules must predate implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-review, normalization, enum-mapping, brittleness]
---

Plans requiring matching source names to enum values (bend names to bend-sign direction) must define exact normalization rules: case sensitivity, space handling, allowed synonyms, source of truth. Hardcoding in implementation invites brittleness. Pre-define the mapping table before implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
