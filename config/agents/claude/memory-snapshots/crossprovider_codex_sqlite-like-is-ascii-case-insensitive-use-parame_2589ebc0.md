---
name: crossprovider codex sqlite-like-is-ascii-case-insensitive-use-parame
description: SQLite LIKE is ASCII case-insensitive; use parameterized boundary checks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [sqlite, path-predicates, case-sensitivity]
---

SQLite LIKE is case-insensitive by default. Root path predicates using LIKE (`LIKE root || '%'`) match case variants when exact case-sensitive boundaries are required (e.g., `/Approved` matches `/approved/secret`). Use parameterized equality plus substring boundary: `path = root OR substr(path, 1, length(root)+1) = root || '/'`. Test mixed-case siblings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
