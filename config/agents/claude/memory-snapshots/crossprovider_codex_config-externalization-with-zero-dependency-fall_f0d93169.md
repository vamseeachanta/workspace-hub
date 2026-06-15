---
name: crossprovider codex config-externalization-with-zero-dependency-fall
description: Config externalization with zero-dependency fallback for cron scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [config-externalization, cron-safety, zero-dependency-fallback, test-coverage]
---

Pattern: add a module-level _load_config() that tries to import yaml and read a config file, but on ANY exception (ImportError, FileNotFoundError, parse error) returns a hardcoded DEFAULTS dict with identical values. Cache the result at module import time. CLI flags (--dpi, --n) override the loaded/fallback config. This enables configuration externalization in resource-constrained cron environments that may lack PyYAML. Behavior must be byte-identical when YAML is absent vs. when it's present with default values.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
