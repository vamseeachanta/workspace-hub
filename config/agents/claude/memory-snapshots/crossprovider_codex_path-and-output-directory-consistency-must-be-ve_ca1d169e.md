---
name: crossprovider codex path-and-output-directory-consistency-must-be-ve
description: Path and output directory consistency must be verified across all steps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-review, path-consistency, file-generation]
---

Infrastructure plans with file generation often have internal path contradictions: 'output/installation/' in generation step but 'output/ballymore_mf_plet/' in validation step. Verify output paths are consistent across generation, loading, and acceptance criteria. Path mismatches can cause failures unrelated to model validity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
