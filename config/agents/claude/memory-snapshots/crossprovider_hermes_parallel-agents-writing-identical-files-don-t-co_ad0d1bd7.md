---
name: crossprovider hermes parallel-agents-writing-identical-files-don-t-co
description: Parallel agents writing identical files don't conflict — git status stays clean
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, parallel-agents, contention]
---

When two hermes agents independently generate and write the same file (e.g., ocr_parser.py, staleness_scanner.py), `git status` shows no changes and `git diff` is empty because content is identical. This avoids merge conflicts but requires vigilance: `git status -s` shows 'M' (modified) even when nothing changed. Enables write-only parallel pattern: each agent writes unique files, main session reads post-run to verify.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
