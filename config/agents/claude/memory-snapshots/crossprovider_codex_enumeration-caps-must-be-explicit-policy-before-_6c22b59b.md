---
name: crossprovider codex enumeration-caps-must-be-explicit-policy-before-
description: Enumeration caps must be explicit policy before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [requirements, policy, bounded-collection]
---

Without a concrete numeric cap (per-endpoint/per-run/global), enumeration implementations will either invent policy during coding or fail-close unpredictably. Define cap value, granularity, and approval authority in requirements, not as an implementation detail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
