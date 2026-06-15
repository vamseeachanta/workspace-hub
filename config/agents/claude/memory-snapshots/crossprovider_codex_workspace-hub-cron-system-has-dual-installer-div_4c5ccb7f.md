---
name: crossprovider codex workspace-hub-cron-system-has-dual-installer-div
description: Workspace-hub cron system has dual-installer divergence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, architecture, technical-debt]
---

Two separate cron installers (legacy setup-cron.sh and transactional cron_transaction.py) have diverging implementations: machine token resolution differs (cron_apply.py:213-216 uses canonical dev-primary key vs setup-cron.sh uses hostname/alias), environment variable expansion differs (setup-cron.sh has $WORKSPACE_HUB/$LOG logic, cron_transaction.py lacks it), and schedule/command spacing differs (two spaces vs one). Any cron work must account for both paths or refactor to a single source of truth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
