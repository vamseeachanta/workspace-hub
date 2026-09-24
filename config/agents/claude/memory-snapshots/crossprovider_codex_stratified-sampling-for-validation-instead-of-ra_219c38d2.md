---
name: crossprovider codex stratified-sampling-for-validation-instead-of-ra
description: Stratified sampling for validation instead of random spot checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validation, sampling]
---

When validating batches, structure samples by corpus and failure mode, not purely random selection. This catches systematic drift (e.g., prompt weakness on one corpus) that random samples can easily miss. Twenty random checks may pass while 90% systematic error exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
