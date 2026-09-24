---
name: crossprovider codex plans-referencing-unverified-cli-contracts-creat
description: Plans referencing unverified CLI contracts create hidden blockers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contract-verification, cli-patterns, plan-rigor]
---

CLI invocations in plans (e.g., `orcawave.exe -check-license`) without a concrete file path or docs proving the contract create deployment risk. External tools may not support the assumed interface. Plans must cite a source file or explicitly mark as follow-up verification work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
