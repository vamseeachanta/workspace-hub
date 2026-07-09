---
name: crossprovider codex validators-in-isolation-don-t-catch-cross-issue-
description: Validators in isolation don't catch cross-issue gate violations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [validation, gates, system-level]
---

A validator can pass locally but the plan can still violate system-wide gates (e.g., creating public output before #63 approves, or sampling before #70 evidence). Sessions 6-8 found individual validators passed but the plan violated the publication gate—validators need coordinated sequencing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
