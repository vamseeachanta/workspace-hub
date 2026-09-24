---
name: crossprovider codex sha-level-binding-required-for-approval-evidence
description: SHA-level binding required for approval evidence in bypass-recovery governance
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-audit, bypass-recovery, evidence-binding]
---

Issue-level approval signals (GitHub labels, marker file timestamps) don't prove a later approval applies to the specific bypassed commit, especially when an issue has multiple revisions. Approval-audit models need explicit SHA binding or precedence rules for timestamp sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
