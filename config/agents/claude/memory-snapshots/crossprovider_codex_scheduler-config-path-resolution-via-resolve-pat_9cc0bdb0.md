---
name: crossprovider codex scheduler-config-path-resolution-via-resolve-pat
description: Scheduler config path resolution via _resolve_path() and _scheduler_repo_root
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduler, config, path-resolution]
---

The scheduler job class provides _resolve_path(path, fallback_root=_scheduler_repo_root) to resolve config paths as repo-relative when a root is injected, or absolute if already absolute. No central schema validation needed; unknown YAML keys pass through to the job constructor. Use this pattern for any new config paths that need repo-relative resolution in scheduler jobs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
