---
name: crossprovider codex cron-and-systemd-services-are-decisive-for-repo-
description: Cron and systemd services are decisive for repo KEEP classification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, fleet-audit, cron, systemd, process-dependencies]
---

A git clone with clean tree and no untracked files can still be load-bearing if it is referenced by active crontab entries or systemd services. Before classifying a repo for deletion, enumerate active cron jobs and systemd user services on the machine and check whether their paths or execution depends on that clone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
