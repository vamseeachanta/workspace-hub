---
name: crossprovider hermes remote-result-file-sync-friction-on-cross-machin
description: Remote result file sync friction on cross-machine orchestration
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cross-machine, result-sync, architectural]
---

ace-linux-2 lane results write to `/mnt/local-analysis/ace2-worker-logs/`; not auto-synced to ace-linux-1 control surface. Lane monitors must explicitly SSH-read or SCP them. Architectural constraint, not a bug; impacts visibility.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
