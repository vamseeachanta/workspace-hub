---
name: feedback-dispatch-only-gpu-claw-and-ace-linux-2
description: "From 2026-08-14, dispatch execution work only to gpu-claw and ace-linux-2; ace-linux-1 is the control surface only"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b006eae-10ef-4664-8b7a-316d95790cce
  modified: 2026-08-15T01:47:04.121Z
---

Owner directive, 2026-08-14: **"we only dispatch work to gpu-claw and ace-linux-2
going forward to manage resources."** ace-linux-1 is the control/orchestration
surface — planning, dispatch, review adjudication, git/GitHub operations. Execution
work (test runs, solver runs, provider review CLIs, subagent lanes doing heavy
compute) goes to gpu-claw or ace-linux-2.

**Why:** ace-linux-1's root filesystem hit **99% (4.3 GB free of 229 GB)** on
2026-08-14 while running execution work locally. The shortage had already caused
real damage that day: no worktree could be created, so two parallel planning lanes
shared one checkout, and one lane's commit landed on the other's branch while its
own remote branch stayed at base. See [[feedback-parallel-agents-shared-mutable-tool-path]]
and [[feedback-amend-clobbers-parallel-branch-in-shared-checkout]].

**How to apply:**

Fleet capability, measured 2026-08-14 (not from memory — `nproc`, `free -g`, `df -h`):

| host | cores | RAM | local free disk |
|---|---|---|---|
| ace-linux-1 (control only) | 32 | 31 GB | `/` **23 GB** after cleanup, was 4.3 GB |
| ace-linux-2 | 32 | 31 GB | `/` 258 GB · `/mnt/dde` 847 GB · `/mnt/local-analysis` **825 GB** |
| gpu-claw | 8 | 62 GB | `/` 85 GB |

**The ace-linux-2 caveat that decides how to use it.** Its `/mnt/ace` is
ace-linux-1's disk over NFS — verified by `stat`: same inode (129499157), different
device (75 vs 2049), and `df` reports the mount as `ace-linux-1:/mnt/ace`. So work
dispatched there that writes into `/mnt/ace` still consumes ace-linux-1's disk and
gains nothing on I/O.

Dispatch to ace-linux-2 therefore buys **32 cores of real CPU parallelism plus
825 GB of local scratch**, but only if the work writes to ace-linux-2's *local*
paths (`/mnt/local-analysis`, `/mnt/dde`, `/`) rather than the NFS-mounted
`/mnt/ace`. This refines [[reference-ace-linux-2-is-not-independent-execution-target]],
which is right that the shared repo path is not independent but understates the
box: it is a capable execution target when local scratch is used.

gpu-claw has only 8 cores but 62 GB RAM and holds the OpenFOAM/CFD lane; reach it
as `ssh gpu-claw-ts` (the plain `gpu-claw` alias is pinned to a dead LAN IP).
See [[reference-external-ssh-tailscale-fleet]].

Related: [[feedback-check-parallel-work]], [[feedback-keep-data-at-fingertips]].
