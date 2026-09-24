---
name: crossprovider codex systemd-environmentfile-must-reject-both-optiona
description: systemd EnvironmentFile must reject both optional and ignore-errors syntax
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [systemd, hardening, security, fail-closed]
---

The Hermes gateway coordinator verifier rejects both `-$ENV_FILE` (optional with leading dash) and `$ENV_FILE (ignore_errors=yes)` patterns. Fail-closed loading is required; optional or lenient EnvironmentFile loading can bypass security constraints. Check using exact match or explicit `(ignore_errors=no)` suffix.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
