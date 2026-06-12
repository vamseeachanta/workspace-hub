---
name: crossprovider hermes workspace-cleanup-classify-files-as-disposable-v
description: Workspace cleanup: classify files as disposable vs durable before committing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workspace-hygiene, cleanup-workflow, file-classification]
---

In dirty checkouts, classify before cleanup: dispose of `.claude/state/*`, failed-run logs (e.g., `logs/quality/memory-health-*` with `/bin/sh: 1: uv: not found`), and untracked temporary dirs; preserve skill patches, ledgers, reports, and scripts. Commit durable artifacts separately, verify preflight checks and secret scans, then push.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
