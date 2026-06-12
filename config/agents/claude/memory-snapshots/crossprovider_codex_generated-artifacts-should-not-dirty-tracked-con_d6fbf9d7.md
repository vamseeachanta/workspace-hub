---
name: crossprovider codex generated-artifacts-should-not-dirty-tracked-con
description: Generated artifacts should not dirty tracked config directories — use .gitignore
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-hygiene, harness-design]
---

Weekly/cron-generated reports (CVE scans, audit logs) should be written to gitignored directories (e.g., `reports/`), not into `config/`. This prevents accumulating uncommitted artifacts from breaking CI and keeps generated output separate from tracked source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
