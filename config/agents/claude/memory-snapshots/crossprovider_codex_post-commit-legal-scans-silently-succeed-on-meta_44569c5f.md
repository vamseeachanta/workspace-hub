---
name: crossprovider codex post-commit-legal-scans-silently-succeed-on-meta
description: Post-commit legal scans silently succeed on metadata-only changesets
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-gotcha, legal-scan, ci-safety]
---

`--diff-only` legal scans return success when only structural metadata (registry entries, config) changes, with no code content. Fallback to full-scan or focused contract tests when diff is expected sparse or code-free.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
