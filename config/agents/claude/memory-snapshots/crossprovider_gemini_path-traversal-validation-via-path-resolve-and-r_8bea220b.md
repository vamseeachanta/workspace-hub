---
name: crossprovider gemini path-traversal-validation-via-path-resolve-and-r
description: Path traversal validation via Path.resolve() and relative_to()
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, path-handling, input-validation, generalizable-pattern]
---

Validate that a user-provided path reference stays within a workspace root using `candidate.resolve().relative_to(root.resolve())` in a try/except ValueError block. Catches directory escape patterns (`../../../etc/passwd`) without regex and is more reliable than string-based checks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
