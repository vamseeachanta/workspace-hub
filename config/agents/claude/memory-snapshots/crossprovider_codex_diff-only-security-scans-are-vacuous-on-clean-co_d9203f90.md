---
name: crossprovider codex diff-only-security-scans-are-vacuous-on-clean-co
description: Diff-only security scans are vacuous on clean committed branches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-scanning, ci-testing, tooling-quirks]
---

Tools like `legal-sanity-scan.sh --diff-only` on a clean committed branch find zero changed files and report false success, testing nothing against HEAD. PR bodies citing such evidence are weak unless the full scan is also run. Verify scan semantics or use full repo scans for validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
