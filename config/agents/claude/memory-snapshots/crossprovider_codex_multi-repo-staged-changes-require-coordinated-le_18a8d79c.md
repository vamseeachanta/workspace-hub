---
name: crossprovider codex multi-repo-staged-changes-require-coordinated-le
description: Multi-repo staged changes require coordinated legal scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, legal-compliance, multi-repo]
---

When a single issue spans multiple repos (e.g., digitalmodel, llm-wiki-mkt-a, llm-wiki in #2760), coordinate staged changes so all repos can run `legal-sanity-scan.sh --diff-only` independently and all must pass before approval. Each repo's diff is scanned separately; a single repo's failure blocks the entire roll.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
