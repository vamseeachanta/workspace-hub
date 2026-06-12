---
name: crossprovider hermes overnight-batch-dispatch-ace-linux-1-control-pla
description: Overnight batch dispatch: ace-linux-1 control plane, ace-linux-2 overflow
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orchestration, multi-machine, tmux-patterns]
---

Long-running batches use tmux sessions; ace-linux-1 is control plane for decisions/GitHub mutations, ace-linux-2 is overflow worker capacity only after auth/tool checks. Log locally to `/mnt/local-analysis/workspace-hub/logs/night-runs/`, remotely to `/mnt/local-analysis/ace2-worker-logs/`. Respect stop targets (e.g., 09:45 CDT) — don't launch new processes after cutoff.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
