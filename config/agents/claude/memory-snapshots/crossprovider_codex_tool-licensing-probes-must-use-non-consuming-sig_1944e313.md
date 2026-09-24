---
name: crossprovider codex tool-licensing-probes-must-use-non-consuming-sig
description: Tool licensing probes must use non-consuming signals
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tool-licensing, probe-design, robustness]
---

Distinguish licensed vs. present state using non-consuming signals only. Import statements or API calls that trigger license checkout are consuming and blur intent; use explicit non-consuming queries for licensing state. Conflating presence with entitlement risks false-positive licensing signals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
