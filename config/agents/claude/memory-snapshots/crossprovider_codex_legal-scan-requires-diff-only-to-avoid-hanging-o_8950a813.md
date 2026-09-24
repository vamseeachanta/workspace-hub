---
name: crossprovider codex legal-scan-requires-diff-only-to-avoid-hanging-o
description: Legal scan requires --diff-only to avoid hanging on pre-existing violations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling-quirk, legal-scan, pr-review]
---

Running `legal-sanity-scan.sh` without `--diff-only` on repos with pre-existing `/mnt/ace/` references enumerates indefinitely through thousands of pre-existing hits. Use PR-scoped scans; fall back to `gh pr diff` for read-only verification without local git.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
