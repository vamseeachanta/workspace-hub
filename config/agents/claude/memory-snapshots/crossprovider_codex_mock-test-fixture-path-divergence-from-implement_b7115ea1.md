---
name: crossprovider codex mock-test-fixture-path-divergence-from-implement
description: Mock test fixture path divergence from implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, bash, mocking, fixtures]
---

Test fixtures written to one location but implementation reads from another causes tests to pass while real code fails. Example: fixtures at `assetutilities/baseline.json` but implementation reads `config/quality/bandit-baseline-assetutilities.json`. Align fixture and implementation paths before writing tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
