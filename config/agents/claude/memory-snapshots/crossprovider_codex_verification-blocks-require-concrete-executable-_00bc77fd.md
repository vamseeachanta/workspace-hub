---
name: crossprovider codex verification-blocks-require-concrete-executable-
description: Verification blocks require concrete executable references, not pseudocode
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, testing, rigor]
---

Replace vague verification comments like 'run a scoped leakage scan' with exact test function names (e.g., `test_abstract_output_leakage_assertions`) or executable commands. Reviewers and implementers cannot work from generic directives; make the verification action actionable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
