---
name: crossprovider codex behavioral-verification-needs-runtime-probes-not
description: Behavioral verification needs runtime probes, not config text grep
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [behavior-verification, config-staleness, runtime-correctness]
---

A system can appear to satisfy behavioral requirements (e.g., workflow gates present) by grepping for keyword phrases in config files, but if that config is stale or misconfigured, actual runtime behavior differs. Behavior verification must probe the active runtime path (symlink state, mounted files) or execute a sanity check, not just check config text presence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
