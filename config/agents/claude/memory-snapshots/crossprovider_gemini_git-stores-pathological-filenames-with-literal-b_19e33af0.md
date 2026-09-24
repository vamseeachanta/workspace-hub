---
name: crossprovider gemini git-stores-pathological-filenames-with-literal-b
description: Git stores pathological filenames with literal backslashes
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git, windows-portability, path-hygiene]
---

Git can commit filenames containing literal backslash characters (e.g., `tests\path\file.csv`), creating duplicate blob entries with identical SHA. This causes Windows checkout failures (exit 128, 'invalid path') while *nix treats them as valid filenames. Audit with `git ls-tree -r` for backslash entries.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
