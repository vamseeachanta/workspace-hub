---
name: crossprovider codex readiness-classification-doesn-t-auto-flip-on-de
description: Readiness classification doesn't auto-flip on dependent issue status change
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [state-machine, workflow-gate, llm-wiki-readiness]
---

When a classification rule depends on another issue's status (e.g., 'mark ready once #748 is implemented'), changing only that issue's status does NOT trigger re-evaluation. The classification function must also receive an explicit default-classification change in the same update, or it will return the stored default. Tests must cover both open and implemented snapshots of the dependent issue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
