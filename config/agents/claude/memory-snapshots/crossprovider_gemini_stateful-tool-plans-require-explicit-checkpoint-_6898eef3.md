---
name: crossprovider gemini stateful-tool-plans-require-explicit-checkpoint-
description: Stateful tool plans require explicit checkpoint contract
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [stateful-tools, checkpoint-contract, resume-semantics]
---

Pipelines with resume/incremental semantics must define checkpoint state-file schema, atomicity guarantees (write temp, fsync, atomic rename), and resume semantics (skip-completed vs reprocess-on-edition-bump) in a dedicated §Checkpoint Contract section before pseudocode. Tests like `test_resume_noop_on_completed_matching_edition` verify the contract, not just happy-path.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
