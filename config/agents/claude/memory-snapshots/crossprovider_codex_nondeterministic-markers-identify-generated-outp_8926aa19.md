---
name: crossprovider codex nondeterministic-markers-identify-generated-outp
description: Nondeterministic markers identify generated output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dirty-classification, privacy, generated-output, audit-patterns]
---

Files with local absolute paths, run timestamps, matplotlib object IDs, binary rewrites, or cache refreshes are nearly always generated output, not source to preserve. Use these markers as quick heuristics to separate generated from code changes; sample diffs for markers rather than listing private paths to maintain privacy during audit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
