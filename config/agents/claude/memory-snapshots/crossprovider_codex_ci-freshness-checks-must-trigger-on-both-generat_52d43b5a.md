---
name: crossprovider codex ci-freshness-checks-must-trigger-on-both-generat
description: CI freshness checks must trigger on both generators and checker code
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [ci-cd, generated-code, verification]
---

A docs-validation job checked published HTML but was not triggered by changes to `scripts/capabilities/**` or `scripts/check_generated_html.py`. Generator-only regressions bypassed verification. Freshness checkers should be triggered on: (1) all generator families via glob patterns, (2) the checker script itself, and placed after dependency installation but before downstream guards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
