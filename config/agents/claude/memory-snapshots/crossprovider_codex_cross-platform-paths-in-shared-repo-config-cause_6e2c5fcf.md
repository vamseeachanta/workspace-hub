---
name: crossprovider codex cross-platform-paths-in-shared-repo-config-cause
description: Cross-platform paths in shared repo config cause warnings
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [path-resolution, cross-platform, config-portability]
---

.codex/config.toml hardcoding Windows paths (D:/workspace-hub) causes malformed agent role warnings on Unix systems when paths are incorrectly rebased. Cross-platform configs need path normalization or templated substitution via resolve_ws_hub_path()-style functions, not hard strings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
