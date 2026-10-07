---
name: feedback-track-fleet-lanes-from-control-surface
description: Track dispatched work in a disk registry plus a host sweep; never poll a remote lane by process name
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b006eae-10ef-4664-8b7a-316d95790cce
  modified: 2026-08-16T00:34:04.124Z
---

When ace-linux-1 acts as control surface dispatching work to gpu-claw and ace-linux-2
([[feedback-dispatch-only-gpu-claw-and-ace-linux-2]]), the control surface's job is to
hold the **registry**, not the work. Two layers, because they fail differently:

1. **Harness task list** (`TaskCreate`/`TaskUpdate`/`TaskList`) — in-session visibility,
   the user can see it. Dies with the session.
2. **Disk registry + sweep** — `~/.claude/fleet-lanes.tsv` (lane, host, workdir, marker,
   kill) reconciled by `workspace-hub/scripts/fleet/lane-sweep.sh`. Survives context
   compaction and session death, which is when tracking actually breaks.

**Why:** on 2026-08-15 a poll loop launched on gpu-claw ran **13.5 hours** past its job,
because it waited on `pgrep -f "stage45_driver"` — a pattern that matches the ssh command
line carrying it. It reported "completed" only when killed by hand. Nothing errored; it
was invisible until a manual `ps` sweep. Same session also produced a stale
`plan-review-fanout.sh` burning tokens against the wrong repo, and two planning lanes
sharing one checkout whose commits crossed.

**How to apply — four rules, each from a real incident:**

- **Never poll a remote lane by process name.** `pgrep -f "X"` matches the ssh command
  containing `X`. Three incidents in one session, one a 13.5 h zombie. Poll for a
  **marker file** instead, or a terminal string in a log. Corollary: `pkill -f "X"` from
  a control-surface ssh kills your own session — kill by PID.
- **Every dispatched lane writes a terminal marker**, success *and* failure, so absence
  is unambiguous. Silence must never be readable as either outcome
  ([[feedback-absence-of-signal-reads-as-success]]).
- **One lane = one directory.** Two lanes in a shared checkout crossed commits; one
  reported "pushed" while its commit sat on the other's branch and its own remote was
  untouched ([[feedback-parallel-agents-shared-mutable-tool-path]]).
- **Sweep before dispatching, not after losing something.** `lane-sweep.sh` flags compute
  on the control surface (a policy violation), live work per host, and long-lived
  `until ! pgrep` loops as suspected zombies.

**Verify a lane's claim, don't accept it.** A subagent reporting "pushed" is a claim about
an artifact's location: check `git log origin/<branch>`, not the push output
([[feedback-subagent-write-phantom]]).

Keep the task list to **lanes and outstanding user decisions**, not every open issue —
an overcrowded list is as useless as none.
