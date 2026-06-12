---
name: crossprovider hermes plan-assumptions-must-verify-against-live-repo-s
description: Plan assumptions must verify against live repo state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-validation, repo-structure, assumption-verification]
---

Plans assuming repo structure (wiki doc_key coverage, file-path signals for repo fanout, submodule layout) must be verified against actual live commits and directory structure before design acceptance. Live-state queries (git ls-files, find -maxdepth) catch grounding gaps.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
