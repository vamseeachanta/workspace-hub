---
name: crossprovider codex plan-blob-identity-separates-authorization-scope
description: Plan blob identity separates authorization scope across review cycles
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, auditing, git]
---

Commit blob hashes uniquely bind plan approvals. Old approval markers cannot authorize new scope if the blob hash changes. Use exact blob identity in approval handoff to prevent accidental scope creep.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
