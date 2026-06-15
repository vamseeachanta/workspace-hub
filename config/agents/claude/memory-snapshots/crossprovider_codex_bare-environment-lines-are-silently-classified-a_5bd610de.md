---
name: crossprovider codex bare-environment-lines-are-silently-classified-a
description: Bare environment lines are silently classified as 'ignore'
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, classification]
---

cron_transaction.py:28-29,191-192 classifies bare VAR=value lines (like WORKSPACE_HUB=) as env/header lines and returns them as 'ignore' rather than erroring. This design allows legacy uncatalogued environment variables to persist in managed crontabs, creating an audit/clarity risk — lines appear preserved but are uncatalogued.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
