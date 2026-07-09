---
name: crossprovider codex guardrails-first-approach-for-scoped-code-review
description: Guardrails-first approach for scoped code reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [code-review, process, efficiency]
---

For scoped reviews, check repo guidance documents (CONTRIBUTING.md, CLAUDE.md) first to identify guardrails (file size, complexity, style limits), then verify them quickly with simple tools (`wc -l`, function-length AST via Python, grep patterns). This catches many issues before detailed logic review begins.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
