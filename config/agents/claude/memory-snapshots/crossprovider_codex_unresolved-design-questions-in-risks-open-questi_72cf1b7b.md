---
name: crossprovider codex unresolved-design-questions-in-risks-open-questi
description: Unresolved design questions in Risks/Open Questions that affect AC behavior block approval
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-gate, acceptance-criteria, design-decision]
---

Questions like 'Should we post GitHub comments or only log?' deferred to Risks sections are approval blockers if they change acceptance criteria or deliverable behavior. Implementation cannot safely choose correctness-critical branches. Resolve these before approval; defer only true open risks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
