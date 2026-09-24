---
name: crossprovider codex repo-state-claims-go-unverified-in-plan-evidence
description: Repo-state claims go unverified in plan evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, evidence-verification, repo-state]
---

Plans claim 'file X does not exist' or 'will be created' without checking actual repo state, and empirical verification catches factual errors. Verify all repo-state assertions (file existence, current content, configuration) against the live repository before the evidence section is finalized.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
