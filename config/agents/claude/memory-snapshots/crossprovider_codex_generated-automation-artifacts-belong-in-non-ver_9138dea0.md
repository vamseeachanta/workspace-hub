---
name: crossprovider codex generated-automation-artifacts-belong-in-non-ver
description: Generated automation artifacts belong in non-versioned directories with .gitignore rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-hygiene, automation-artifacts, scheduled-jobs]
---

Timestamped reports from scheduled audits (lockfile scans, CVE reports) should go to .gitignore'd directories like `reports/` or `logs/`, not versioned `config/`. These artifacts change weekly/daily and create continuous git noise. Use a symlink to `latest` if downstream CI needs a stable reference.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
