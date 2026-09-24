---
name: crossprovider codex bounded-sampling-enforcement-must-enumerate-all-
description: Bounded sampling enforcement must enumerate all traversal vectors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [batch-processing, sampling, test-completeness]
---

Assertions that a sample is 'bounded' or 'no recursive crawl' are incomplete unless they explicitly block find, fd, rg, ls -R, os.walk, glob patterns, and custom scripts—not just du/grep. Document the block list in TDD acceptance criteria so validators catch escapes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
