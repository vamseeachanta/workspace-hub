---
name: ace-linux-2-dispatch-capability
description: "ace-linux-2 cross-machine dispatch readiness — capability matrix, venv path difference vs ace-linux-1, and PATH gap blocking worker spawn (tracked at"
metadata: 
  node_type: memory
  type: project
  originSessionId: d4fe73ec-6517-4e58-a943-20b6e6bd30f0
---

ace-linux-2 (dev-secondary, overflow worker per [[machine-inventory]] `docs/ops/machine-inventory.md`) is *almost* dispatch-ready from ace-linux-1 (canonical control plane). Capability matrix verified 2026-05-14T23:27 CT:

| Check | State |
|---|---|
| SSH from ace-linux-1 | ✓ works |
| Workspace clone at `/mnt/local-analysis/workspace-hub` | ✓ present, on `main` |
| digitalmodel repo present | ✓ |
| Hermes installed | ✓ at `~/.hermes/hermes-agent/venv/bin/python` (note: `venv`, NOT `.venv` — DIFFERENT from ace-linux-1's `.venv/bin/python` path) |
| Hermes gateway running | ✓ as systemd user unit `hermes-gateway.service` (parent = `systemd --user`, ppid=1627) |
| kanban-create accepted via SSH | ✓ verified |
| **kanban worker spawn** | ✓ verified 2026-05-15 — live `subprocess.Popen` replication using gateway's `/proc/<pid>/environ` succeeds. #2712 closed as can't-repro. |

**Why:** Cross-machine dispatch is the parallelism path: ace-linux-1 holds the canonical dispatch ledger / GH-mutation surface, ace-linux-2 absorbs OSS-engineering and parallel-AI workloads. Per dual-quota delegation model in [[goal-catalog]] #2695, ace-linux-2 capacity is one of the additive quota pools.

The original 2026-05-14 `hermes executable not found on PATH` failure DID NOT REPRODUCE on 2026-05-15. Root cause in #2712 issue body was wrong: it conflated SSH-non-login-session PATH (which lacks `~/.local/bin`) with the gateway-subprocess PATH (which inherits `dict(os.environ)` from the systemd user unit and DOES include `~/.hermes/hermes-agent/venv/bin` + `~/.local/bin`). See [[feedback_rca_conflated_ssh_vs_subprocess_path]] for the generalizable defect class. Code reference: `hermes_cli/kanban_db.py:3779` does `env = dict(os.environ)` before the `Popen(cmd, env=env, ...)` at line 3848 — worker inherits gateway PATH, full stop.

**How to apply:**

1. Cross-machine dispatch to ace-linux-2 currently WORKS. Verified empirically 2026-05-15 with closing comment + code citation on #2712.
2. Dispatch pattern: `ssh ace-linux-2 '~/.local/bin/hermes kanban create ...'` (the SSH-session lacks `~/.local/bin` in PATH, so use the absolute path for SSH invocations). The worker subprocess spawned by the gateway works fine because the gateway env has hermes in PATH.
3. ace-linux-2's kanban.db is INDEPENDENT of ace-linux-1's — no cross-machine task sync. Tasks dispatched there don't appear in `hermes kanban list` here. Track both via GH issue comments instead (the user-visible surface).
4. Per inventory: route OSS-engineering work (digitalmodel CI, mesh prep, freecad/gmsh/openfoam/blender, gdsfactory, GPU-suitable embeddings) to ace-linux-2. Keep dispatch-ledger-sensitive work (GH-mutation-heavy, Hermes config changes, kanban orchestration) on ace-linux-1.
5. **If a future spawn failure recurs**: capture `/proc/<gateway-pid>/environ` immediately (it's ground truth for what the worker actually sees). Don't infer from `echo $PATH` in an SSH session — that's a different env.

Cross-references:
- [[feedback_cross_machine_execution]] — per-machine tasks via shared git repo
- [[feedback_hermes_active_preflight_check]] — Hermes-active preflight for git contention
- [[project_hermes_installation]] — Hermes v0.4.0+ install state
- #2696 Hermes routing-layer audit (would have caught this gap)
- #2548 machine-inventory (parent doc deliverable)
- #2712 PATH gap fix (this issue surfaced it)
