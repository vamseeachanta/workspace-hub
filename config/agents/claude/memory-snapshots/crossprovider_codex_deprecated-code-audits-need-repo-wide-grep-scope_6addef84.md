---
name: crossprovider codex deprecated-code-audits-need-repo-wide-grep-scope
description: Deprecated-code audits need repo-wide grep scope
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [refactoring, deprecation, scope-creep]
---

Narrow audit scopes (e.g., "replace examples in docs/domains/orcawave/README.md") miss instances of stale references. Module-rename audits require grep across all docs, tests, and comments; adding new examples without removing old ones leaves inconsistent guidance.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
