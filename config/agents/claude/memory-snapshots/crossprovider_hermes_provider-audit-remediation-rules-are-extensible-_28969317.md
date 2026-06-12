---
name: crossprovider hermes provider-audit-remediation-rules-are-extensible-
description: Provider audit remediation rules are extensible patterns
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, remediation, patterns]
---

The provider_session_ecosystem_audit.py uses remediation rule families to address recurring audit signals: LLM-wiki spinout drift, session-local worktree drift, nested repo context drift. These are extensible; new signal classes can be added as rule families rather than ad-hoc patches.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
