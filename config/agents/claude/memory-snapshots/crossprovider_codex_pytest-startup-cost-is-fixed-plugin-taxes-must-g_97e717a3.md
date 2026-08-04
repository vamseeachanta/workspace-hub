---
name: crossprovider codex pytest-startup-cost-is-fixed-plugin-taxes-must-g
description: pytest startup cost is fixed; plugin taxes must gate per-lane, not globally
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [pytest, performance, ci-lanes, optimization]
---

`--collect-only` pays the full pytest startup cost from pytest-randomly (order-dependency detection), pytest-benchmark (git metadata shell), and faker locale scanning. These plugins must remain in the full/nightly lane but be disabled in the fast lane via invocation flags, never removed globally—fast lane must not reduce coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
