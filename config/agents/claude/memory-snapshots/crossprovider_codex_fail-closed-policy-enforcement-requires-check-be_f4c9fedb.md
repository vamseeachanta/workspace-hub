---
name: crossprovider codex fail-closed-policy-enforcement-requires-check-be
description: Fail-closed policy enforcement requires check-before-accept, not check-after
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [security, authorization, privacy]
---

When a policy (source roots, allowlists, origin verification) is configured, validate input AGAINST the policy BEFORE accepting it, not after. Resolver that returns Path(value) if it exists before checking configured source roots violates fail-closed principle and enables path leakage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
