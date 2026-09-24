---
name: crossprovider codex adversarial-privacy-review-must-check-both-posit
description: Adversarial privacy review must check both positive and negative leakage paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-review, privacy-contract, equivalent-leakage]
---

A plan forbidding one column while allowing another field carrying equivalent identity (raw filenames, path fragments, hashes) fails privacy contract. Tests must cover all potential identity-bearing fields, not just the explicitly prohibited one.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
