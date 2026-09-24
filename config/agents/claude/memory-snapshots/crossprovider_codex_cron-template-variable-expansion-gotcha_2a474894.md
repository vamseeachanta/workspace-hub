---
name: crossprovider codex cron-template-variable-expansion-gotcha
description: Cron template variable expansion gotcha
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, bash-gotcha, script-design]
---

Variables like `<REPO_ROOT>` in crontab-template.sh entries are not shell-expanded by cron; they remain literal. Scripts must resolve them at runtime (e.g., `cd $REPO_ROOT && ./script.sh` or absolute path lookup). Causes silent failures if overlooked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
