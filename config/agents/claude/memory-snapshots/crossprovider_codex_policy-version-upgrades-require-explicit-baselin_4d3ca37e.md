---
name: crossprovider codex policy-version-upgrades-require-explicit-baselin
description: Policy version upgrades require explicit baseline carry-forward
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [policy-migration, backward-compatibility, audit-policy]
---

#2486 v1→v2 audit-policy migration showed v1 baseline artifacts dropped when policy loader required exact policy_version match. Fix: policy v2 must declare `append_only_v1: true` and loader must accept previous-version artifacts with matching `audit_scope`. This is not automatic and must be tested explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
