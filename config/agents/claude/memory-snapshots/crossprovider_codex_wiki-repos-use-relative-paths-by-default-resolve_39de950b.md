---
name: crossprovider codex wiki-repos-use-relative-paths-by-default-resolve
description: Wiki repos use relative paths by default; resolve path roots explicitly before operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-handling, wiki, input-validation]
---

Issue/dispatch packets often use wiki-relative paths (e.g., `dnv-st-n001.md`) instead of repo-root paths (`wikis/engineering-standards/wiki/standards/dnv-st-n001.md`). Require explicit path resolution with confirmation before using paths in scripts or operations; do not assume repo-root.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
