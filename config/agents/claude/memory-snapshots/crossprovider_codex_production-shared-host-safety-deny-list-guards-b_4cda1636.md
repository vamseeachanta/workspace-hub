---
name: crossprovider codex production-shared-host-safety-deny-list-guards-b
description: Production shared-host safety: deny-list guards before path enumeration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [powershell-safety, production-code, multi-user-systems]
---

On multi-user production systems with canary files, pattern Test-IsCanary(path) before ANY enumeration or reporting of paths. Load-bearing on shared filesystems; must check explicitly before Get-ChildItem, Test-Path, or similar.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
