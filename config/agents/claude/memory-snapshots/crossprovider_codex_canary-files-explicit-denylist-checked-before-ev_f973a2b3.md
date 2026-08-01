---
name: crossprovider codex canary-files-explicit-denylist-checked-before-ev
description: Canary files: explicit denylist checked before every path enumeration
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [production, ransomware-defense, powershell, safety, canary-files]
---

On production hosts with ransomware canaries (D:\0invoice-*, D:\01a-*.log, C:\Users\0invoice-*.docx), hardcode the patterns in a $CanaryDenylist and call Test-IsCanary before ANY path is opened/enumerated/reported. Never use -Recurse. No destructive cmdlets. Allowlist discipline: names/booleans/ports only, never tokens/contents.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
