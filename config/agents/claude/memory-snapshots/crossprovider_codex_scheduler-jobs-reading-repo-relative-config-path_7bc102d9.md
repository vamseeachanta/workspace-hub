---
name: crossprovider codex scheduler-jobs-reading-repo-relative-config-path
description: Scheduler jobs reading repo-relative config paths require explicit root resolution
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [scheduler, paths, config, runtime-safety]
---

Relative config paths (e.g., `config/scheduler/scheduler_config.yml`) fail at runtime if the job runs from a non-repo working directory. Scheduler code must resolve paths via an explicit repo-root anchor (e.g., `_scheduler_repo_root`) or use absolute paths from deployment. Plans must name this contract explicitly in config-reading code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
