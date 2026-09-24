---
name: crossprovider codex cross-platform-plans-must-validate-prerequisites
description: Cross-platform plans must validate prerequisites before partial setup, not defer
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [windows, cross-platform, prerequisites, setup-order]
---

Windows setup plans cannot defer Git Bash validation to v1.1 if they claim native PowerShell parity. Hardcoded paths like `C:\Program Files\Git\bin\bash.exe` in existing scripts prove the dependency is real. Plans must include Step 0 validation and installation before any dependent setup happens.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
