---
name: crossprovider gemini audit-trails-must-fail-closed-not-fail-open
description: Audit trails must fail-closed, not fail-open
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [audit, compliance, security, design-pattern]
---

Fail-open integration patterns (|| true guards, optional logging) undermine audit trail reliability. If the logging mechanism can be silently disabled or skipped, the audit trail is compromised. Audit and compliance systems must fail-closed: absence of a log entry is an error, not a silent skip.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
