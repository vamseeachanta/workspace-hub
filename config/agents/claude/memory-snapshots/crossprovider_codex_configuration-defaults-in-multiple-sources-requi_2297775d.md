---
name: crossprovider codex configuration-defaults-in-multiple-sources-requi
description: Configuration defaults in multiple sources require coordinated updates and sync verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [configuration-management, generated-code, sync-scripts]
---

When a configuration default appears in multiple places (source templates in config/agents/, sync scripts, generated home-dir configs, repo-local copies), changes to one source won't propagate until the sync script runs and completes. All source locations must be updated together, and verification must check both home-dir and repo-local destination files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
