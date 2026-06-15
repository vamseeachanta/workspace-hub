---
name: crossprovider codex minified-json-contracts-defeat-review-precision
description: Minified JSON contracts defeat review precision
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [artifact-design, qa-workflow, code-review]
---

When artifact JSONs are minified to a single line, all file:line citations in review findings collapse to line 1, preventing pinpoint bug reports. Keep contract/manifest JSONs human-readable with line breaks so reviewers can trace findings to specific rows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
