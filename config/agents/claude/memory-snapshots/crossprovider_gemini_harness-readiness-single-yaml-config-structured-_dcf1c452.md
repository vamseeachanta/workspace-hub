---
name: crossprovider gemini harness-readiness-single-yaml-config-structured-
description: Harness readiness: single YAML config + structured status output
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [configuration, monitoring, structured-output]
---

harness-config.yaml is single source of truth (required_plugins, hook_blocking_patterns, per-workstation paths, baselines). Checks emit structured YAML (not prose stdout) with per-check pass/fail + timestamp. Enables cross-machine diff and remediate scripts to parse reliably.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
