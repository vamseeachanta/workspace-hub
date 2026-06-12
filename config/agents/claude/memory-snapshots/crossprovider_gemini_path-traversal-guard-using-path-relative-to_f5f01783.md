---
name: crossprovider gemini path-traversal-guard-using-path-relative-to
description: Path-traversal guard using Path.relative_to()
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [security, path-traversal, input-validation]
---

Guard untrusted path references in YAML/frontmatter with `Path.resolve()` followed by `relative_to(workspace_root)` in a try/except ValueError block. Returns None if the resolved path escapes the workspace (e.g., `../../etc/passwd`). Prevents directory-traversal attacks via user-controlled path fields.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
