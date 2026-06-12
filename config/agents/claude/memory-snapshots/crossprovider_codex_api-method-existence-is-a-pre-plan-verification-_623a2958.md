---
name: crossprovider codex api-method-existence-is-a-pre-plan-verification-
description: API method existence is a pre-plan verification gate
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [api-design, verification, blocker]
---

Pseudocode calling non-existent methods (e.g., GeometryQualityChecker.check() when only generate_report() exists) is a blocker. Verify method signatures, class APIs, and available overloads before plan approval; discovery post-plan requires full redesign.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
