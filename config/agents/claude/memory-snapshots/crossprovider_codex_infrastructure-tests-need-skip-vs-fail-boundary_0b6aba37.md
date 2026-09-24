---
name: crossprovider codex infrastructure-tests-need-skip-vs-fail-boundary
description: Infrastructure tests need skip vs fail boundary
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, infrastructure, boundaries]
---

Required-native or unsupported-platform tests must fail with INFRASTRUCTURE_FAILURE (exit 1), not skip. Optional tests skip only on (non-Windows + non-required). Confusing skip and fail hides broken capability as a missing environment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
