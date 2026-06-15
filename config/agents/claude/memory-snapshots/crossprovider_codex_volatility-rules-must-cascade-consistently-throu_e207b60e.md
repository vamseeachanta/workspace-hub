---
name: crossprovider codex volatility-rules-must-cascade-consistently-throu
description: Volatility rules must cascade consistently through policy, tests, contracts, and commands
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [issue-planning, test-design, policy-enforcement]
---

When defining source volatility (critical/high/medium/low) in issue plans, enforce the same classification across policy prose, test assertions, source-contract tables, acceptance criteria, and verification commands. Internal conflicts cause tests to fail-open instead of fail-closed. Fix: single-source volatility enum; apply it everywhere.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
