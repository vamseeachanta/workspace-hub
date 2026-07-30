---
name: crossprovider codex loose-parameter-binding-creates-race-windows-bet
description: Loose parameter binding creates race windows between check and use
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [security, concurrency, parameter-validation]
---

When descriptor-level and Git/repository bindings do not strictly validate parameter source, race windows exist between the check (does this registry exist?) and use (load from registry). Bind parameters to canonical sources and validate immutably.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
