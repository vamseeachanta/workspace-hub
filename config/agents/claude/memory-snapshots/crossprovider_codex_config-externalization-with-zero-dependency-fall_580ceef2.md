---
name: crossprovider codex config-externalization-with-zero-dependency-fall
description: Config externalization with zero-dependency fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config-management, cron-safety, optional-deps, fallback-pattern]
---

When code runs in constrained environments (cron, missing optional deps), implement _load_config() that tries to import yaml and read config file but returns hardcoded DEFAULTS dict on any exception (ImportError, FileNotFoundError, parse errors). Cache in module global. CLI flags override config values. Ensures behavior-identical operation whether config file exists or not.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
