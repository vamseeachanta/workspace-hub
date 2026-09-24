---
name: crossprovider codex enforcement-plans-must-self-scan-their-own-artif
description: Enforcement plans must self-scan their own artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, scanner-design, testing]
---

When a plan introduces a new scanner or enforcement gate, the TDD/acceptance criteria must include a test proving the scanner passes its own plan file, config artifacts, implementation files, test files, review artifacts, and sidecars. Enforcement that exempts itself is a backdoor.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
