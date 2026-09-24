---
name: crossprovider codex index-vs-working-tree-mixing-creates-toctou-in-r
description: Index vs working-tree mixing creates TOCTOU in release validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [toctou, git, filesystem, index]
---

validate_aggregate() resolving TAXONOMY_PATH from working tree while verify_release() reads aggregate from Git index creates a verify-to-use race. Binding validation to Git-blob readers (index or HEAD) eliminates the TOCTOU.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
