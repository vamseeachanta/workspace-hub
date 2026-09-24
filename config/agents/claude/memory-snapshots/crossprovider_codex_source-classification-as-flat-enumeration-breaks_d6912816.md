---
name: crossprovider codex source-classification-as-flat-enumeration-breaks
description: Source classification as flat enumeration breaks independent governance dimensions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-governance, classification-model, design-modeling]
---

Modeling source as {canonical, duplicate, public, synthetic, private, licensed, derived} is a single enum that prevents deterministic eligibility decisions. These must be independent dimensions: source_class, visibility, license_status, origin. Mixing them prevents clean separation of concerns for release gating and publication policy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
