---
name: crossprovider codex recursive-filesystem-checks-frequently-use-only-
description: Recursive filesystem checks frequently use only `.iterdir()` — miss nested files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem-traversal, nested-safety, containment-risk]
---

Directory traversal often stops at immediate children. Nested files like `nested/leak.xlsx` bypass filters checking suffixes or banned content. Use recursive directory walking or explicit recursive enumeration for safety gates on filesystem artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
