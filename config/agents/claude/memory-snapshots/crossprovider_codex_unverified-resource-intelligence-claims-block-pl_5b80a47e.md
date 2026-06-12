---
name: crossprovider codex unverified-resource-intelligence-claims-block-pl
description: Unverified resource-intelligence claims block plan approval
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, adversarial-review, resource-intelligence]
---

Plans repeatedly assert live-state facts (issue statuses, file existence, prior artifacts) in Resource Intelligence Summary without embedded, independently verifiable evidence. This is a P1 blocker. The standard requires concrete proof beyond self-asserted prose—either git commit output, issue API snapshots, or file-content inspection embedded in the plan artifact itself. Vague claims like 'found via `gh issue view`' without the transcript are unverified.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
