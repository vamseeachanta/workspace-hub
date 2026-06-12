---
name: crossprovider hermes systemd-environmentfile-optional-syntax-bypasses
description: Systemd EnvironmentFile optional syntax bypasses fail-closed gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [systemd-config, safety-gates, parser-bypass]
---

Optional EnvironmentFile declarations using `(ignore_errors=yes)` syntax allow config loading to fail silently, defeating fail-closed semantics. Explicit verification required: reject optional forms, only accept required EnvironmentFile without ignore-errors wrapper.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
