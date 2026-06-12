---
name: crossprovider hermes issue-closeout-requires-full-ceremony-implement-
description: Issue closeout requires full ceremony: implement→test→legal→review→commit→push→comment→label→close
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, issue-lifecycle, approval-gate]
---

Skipping any step leaves issue in ambiguous state. Adversarial review must clear all MAJOR findings before commit. Legal scan must pass. After push to origin, comment on issue linking artifacts, then label (status change), then close. Partial sequences hide work-in-progress or failed closures.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
