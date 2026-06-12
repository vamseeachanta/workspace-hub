---
name: crossprovider codex policy-docs-must-update-alongside-automation-to-
description: Policy docs must update alongside automation to prevent review churn
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [workflow-consistency, documentation, process-debt]
---

When workflow automation introduces a new requirement (e.g. always assign `computer:`), the canonical policy docs stating the old rule (e.g. 'leave blank for machine-agnostic tasks') must be updated in the same change. Otherwise reviewers will keep 'fixing' items in opposite directions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
