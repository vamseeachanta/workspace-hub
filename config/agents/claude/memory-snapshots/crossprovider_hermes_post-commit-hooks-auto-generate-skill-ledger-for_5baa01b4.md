---
name: crossprovider hermes post-commit-hooks-auto-generate-skill-ledger-for
description: Post-commit hooks auto-generate skill ledger for reference tracking
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills, ledger, learning]
---

Workspace-hub post-commit hooks append skill-patches.jsonl entries for learned skill reference files created during session (e.g., `references/public-graph-manifest-validation.md`). Durable ledger enables future sessions to discover patterns without re-running full validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
