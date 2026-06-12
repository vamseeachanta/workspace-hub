---
name: crossprovider codex config-sharing-across-repos-needs-explicit-path-
description: Config-sharing across repos needs explicit path resolution
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [multi-repo, config, hooks]
---

Shared configs at workspace root (e.g., `.gitleaks.toml`) won't auto-apply to per-repo hooks running from each repo's root dir. Either pass explicit `--config` paths, place per-repo shims, or use canonical registry + discovery to resolve paths deterministically.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
