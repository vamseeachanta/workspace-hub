---
name: crossprovider codex fallback-uv-python3-m-pytest-for-read-only-cache
description: Fallback uv → python3 -m pytest for read-only cache environments
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [tooling, environment]
---

On machines where `uv` cache paths are read-only, use `python3 -m pytest` instead. This workspace has consistent read-only home cache issues; the fallback is stable and required before any uv-based test harness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
