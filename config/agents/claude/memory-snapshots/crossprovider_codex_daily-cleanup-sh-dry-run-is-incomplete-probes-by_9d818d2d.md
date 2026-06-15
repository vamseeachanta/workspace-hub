---
name: crossprovider codex daily-cleanup-sh-dry-run-is-incomplete-probes-by
description: daily-cleanup.sh --dry-run is incomplete; probes bypass the wrapper
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [tool-quirk, dry-run, safety]
---

The script has a run() dry-run wrapper, but some probes invoke network/cleanup operations directly without checking the DRY_RUN flag. Do not assume --dry-run is safe; read-only audits should not reuse this script.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
