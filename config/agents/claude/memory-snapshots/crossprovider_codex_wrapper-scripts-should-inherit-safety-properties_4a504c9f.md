---
name: crossprovider codex wrapper-scripts-should-inherit-safety-properties
description: Wrapper scripts should inherit safety properties via delegation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [architecture, scheduling]
---

When a wrapper (e.g., setup-cron.sh) calls a direct owner (e.g., cron_apply.py), it must inherit semantic-identity and exact-state-verify semantics rather than create independent primitives or mixed substring branches. Enforcement must mark primitive-bearing files as direct owners.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
