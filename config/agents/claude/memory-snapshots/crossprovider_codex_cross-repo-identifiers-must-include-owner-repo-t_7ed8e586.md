---
name: crossprovider codex cross-repo-identifiers-must-include-owner-repo-t
description: Cross-repo identifiers must include OWNER/REPO to avoid hard-coded repo inference
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [api-design, multi-repo, specification]
---

Issue numbers like `#2945` are ambiguous across repos. Always use `OWNER/REPO#N` format in CLI contracts and data structures so implementation cannot infer the repo from context.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
