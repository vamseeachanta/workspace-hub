---
name: crossprovider codex canonical-contract-validation-before-local-parsi
description: Canonical contract validation before local parsing
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [validation, ordering, contracts]
---

For systems merging canonical → local → staged, validate the canonical contract *before* opening the local file. If malformed local input blocks validation, an invalid canonical can hide undetected. Session 7–8 shows the reordering is required to surface both classes of errors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
