---
name: crossprovider codex privileged-os-maintenance-from-user-cron-require
description: Privileged OS maintenance from user cron requires separate root-owned bundle
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [privilege-boundaries, cron-architecture, root-execution-safety]
---

Cannot escalate individual cleaner commands via sudo from user crontab. Requires dedicated `/etc/cron.d` entry, root-owned executable bundle with fixed arguments, verified rollback, and isolated execution. User checkout remains writable/unprivileged; runtime helpers deployed and maintained separately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
