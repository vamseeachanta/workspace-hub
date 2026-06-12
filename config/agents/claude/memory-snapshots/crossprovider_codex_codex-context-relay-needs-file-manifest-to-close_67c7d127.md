---
name: crossprovider codex codex-context-relay-needs-file-manifest-to-close
description: Codex context relay needs file manifest to close soundness holes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cross-provider, review, soundness, verification]
---

When Claude selects excerpts for Codex, Codex cannot detect omissions that invalidate analysis. Requires manifest: provided file paths, line ranges, commit SHA, truncation policy, omitted relevant files. Code reviews should include full diff + relevant full files, not handpicked snippets.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
