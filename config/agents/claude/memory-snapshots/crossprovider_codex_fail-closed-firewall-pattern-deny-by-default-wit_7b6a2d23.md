---
name: crossprovider codex fail-closed-firewall-pattern-deny-by-default-wit
description: Fail-closed firewall pattern: deny-by-default with explicit allow paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [firewall-pattern, fail-closed, authorization-gates, test-coverage]
---

Build authorization gates that default to DENIED with a reason code (e.g., `MISSING_62_EVIDENCE_CONTRACT`, `blocked_by_issue=70`) rather than defaulting to ALLOWED. Only explicit positive cases with reviewed evidence are allowed. Tests must cover both allow and deny paths, and fixtures may test validator shape without authorizing actual operations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
