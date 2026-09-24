---
name: crossprovider codex single-source-of-truth-for-multi-repo-inventorie
description: Single source of truth for multi-repo inventories prevents hardcoding drift
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config-management, multi-repo-automation, source-of-truth]
---

When tools need to iterate over repos (audits, checks, backups), define the canonical list once in a config file (e.g., harness-config.yaml) and consume it in all scripts. Hardcoding repo lists across multiple scripts creates silent drift: check-all.sh had 5 repos while harness-config.yaml had 4, causing WRK-1082 to miss OGManufacturing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
