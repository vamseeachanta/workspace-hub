---
name: crossprovider codex gitleaks-version-compatibility-with-staged-scan-
description: Gitleaks version compatibility with staged-scan syntax
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gitleaks, tooling, secrets, version]
---

Installed gitleaks binary may not support --source flag for staged scanning. Fallback syntax is gitleaks git --staged ... (without --source), which may be version-dependent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
