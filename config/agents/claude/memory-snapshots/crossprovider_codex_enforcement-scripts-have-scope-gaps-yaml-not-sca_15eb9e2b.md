---
name: crossprovider codex enforcement-scripts-have-scope-gaps-yaml-not-sca
description: Enforcement scripts have scope gaps (YAML not scanned)
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [ci-cd, enforcement, script-maintenance]
---

check-no-abs-paths.sh scans *.py and *.sh but skips *.yml fixtures. Absolute paths in test YAML configs (e.g., /mnt/local-analysis/...) bypass the enforcer, creating a false sense of safety. Broadening script scope to include *.yml requires watching for false positives in comments/docs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
