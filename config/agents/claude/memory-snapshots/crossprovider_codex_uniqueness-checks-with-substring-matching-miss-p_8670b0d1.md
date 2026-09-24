---
name: crossprovider codex uniqueness-checks-with-substring-matching-miss-p
description: Uniqueness checks with substring matching miss prefix collisions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [correctness, path-handling, ambiguity-checks, string-matching]
---

Substring matching with a uniqueness check (e.g., len(hits) == 1) can silently promote the wrong row when the intended row is absent but a prefix match exists (e.g., target `wikis/x/t.csv` absent, but `wikis/x/t.csv.bak` exists as single match). After parsing, require exact field equality.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
