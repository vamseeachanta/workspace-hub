---
name: crossprovider codex local-marker-files-are-not-authoritative-complia
description: Local marker files are not authoritative compliance evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [auditing, compliance, evidence-model, governance]
---

In workflow audits, local marker files (e.g., `.planning/plan-approved/<issue>.md`) must be reconciled against GitHub's authoritative timeline state (issue labels, timestamps, events) rather than treated as sufficient on their own. Local state can diverge from remote state and provides no chronological proof of sequencing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
