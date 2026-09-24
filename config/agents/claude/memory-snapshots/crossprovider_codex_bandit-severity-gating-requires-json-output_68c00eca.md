---
name: crossprovider codex bandit-severity-gating-requires-json-output
description: Bandit severity gating requires JSON output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bandit, severity-gating, tool-quirks]
---

The `-ll` flag filters LOW findings before output, so it cannot both warn on LOW and block MEDIUM+. Use `-f json` with code-based threshold logic to properly separate severity levels and implement layered gating.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
