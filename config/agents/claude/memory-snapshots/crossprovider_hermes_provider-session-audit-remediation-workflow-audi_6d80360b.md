---
name: crossprovider hermes provider-session-audit-remediation-workflow-audi
description: Provider session audit remediation workflow: audit → issue → approve → execute
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-audit, issue-workflow, approval-gate]
---

Audit provider sessions for missing-repo patterns (Claude/Codex/Hermes/Gemini) → categorize into remediation rules → create scoped GitHub issues with durable plans → post for approval → execute only approved work with saved review artifacts. Example: Codex nested-repo-context-drift (#2655) routed to tier-1 repos.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
