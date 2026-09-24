---
name: crossprovider codex red-green-verification-required-for-ci-gate-chan
description: Red/green verification required for CI gate changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, ci-gates, tdd, codex-adversarial]
---

Plans proposing CI/lint gate changes must include explicit TDD acceptance commands for the exact replacement commands themselves (e.g., `flake8 src/ tests/`), not alternative tools or shape-verifiers. Plan must show command failure before fixes and passage after fixes. Alternative tool invocations do not satisfy this gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
