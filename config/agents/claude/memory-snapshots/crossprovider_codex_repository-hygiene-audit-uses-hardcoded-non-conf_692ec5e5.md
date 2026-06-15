---
name: crossprovider codex repository-hygiene-audit-uses-hardcoded-non-conf
description: Repository hygiene audit uses hardcoded, non-configurable timeouts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, configuration]
---

repo-ecosystem-hygiene-audit.sh:37-39 defaults probe/repo/total timeouts to 10/45/480 seconds with no environment variable or config-driven override. May be inadequate for slower repositories or high-latency network environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
