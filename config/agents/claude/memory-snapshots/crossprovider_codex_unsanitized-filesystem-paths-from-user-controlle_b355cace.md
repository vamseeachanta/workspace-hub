---
name: crossprovider codex unsanitized-filesystem-paths-from-user-controlle
description: Unsanitized filesystem paths from user-controlled names enable directory traversal
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, path-traversal, api-design]
---

Multiple code review instances found user-supplied names (hull IDs, solver types, mesh names) interpolated directly into filesystem paths without sanitizing `..`, absolute paths, or other traversal characters. Any API accepting user-derived input to construct paths must validate against traversal vectors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
