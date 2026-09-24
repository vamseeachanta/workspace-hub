---
name: crossprovider codex dry-run-wrapper-penetration-in-daily-cleanup-sh
description: Dry-run wrapper penetration in daily-cleanup.sh
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling-quirk, dry-run-limitations, bash-scripting]
---

The daily-cleanup.sh script contains probes that bypass the run() dry-run wrapper and perform actual filesystem operations even when dry-run mode is enabled. This makes it unsafe to reuse for read-only audits; new read-only probes must be purpose-built rather than adapting existing cleanup commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
