---
name: crossprovider codex public-issue-comments-require-explicit-safe-comm
description: Public issue comments require explicit safe-comment gates; artifact scanning alone is insufficient
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, public-tracker-safety, acceptance-criteria]
---

Testing that generated JSONL/JSON/HTML reports don't leak private data does not verify that public issue comments will be safe. Live #748 acceptance explicitly forbids raw labels, paths, filenames, and client identifiers in comments. Establish explicit comment templates or no-comment/raw-safe gates in the same TDD/acceptance block as the artifact validation, not as a separate audit step.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
