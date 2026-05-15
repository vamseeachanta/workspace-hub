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
| Hermes gateway running | ✓ (PID varies, runs `hermes_cli.main gateway run --replace`) |
| kanban-create accepted via SSH | ✓ verified |
| **kanban worker spawn** | ✗ **blocked** — auto-blocks at spawn with `\`hermes\` executable not found on PATH` |

**Why:** Cross-machine dispatch is the parallelism path: ace-linux-1 holds the canonical dispatch ledger / GH-mutation surface, ace-linux-2 absorbs OSS-engineering and parallel-AI workloads. Per dual-quota delegation model in [[goal-catalog]] #2695, ace-linux-2 capacity is one of the additive quota pools. Wasting a 5-min cross-machine dispatch attempt on auto-block burns time.

The PATH gap is real but minor: `~/.local/bin/hermes` symlink → `~/.hermes/hermes-agent/venv/bin/hermes` EXISTS, but `~/.local/bin` isn't on the gateway-subprocess PATH (verified: `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin`). Fix tracked at #2712 — recommend `sudo ln -s ~/.hermes/hermes-agent/venv/bin/hermes /usr/local/bin/hermes` for durability.

**How to apply:**

1. Before dispatching to ace-linux-2, check #2712 status. If still open, defer to ace-linux-1 — don't waste a dispatch attempt.
2. After #2712 closes, dispatch pattern works: `ssh ace-linux-2 '~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main kanban create ...'` — use the `venv` (no dot) path on ace-linux-2.
3. ace-linux-2's kanban.db is INDEPENDENT of ace-linux-1's — no cross-machine task sync. Tasks dispatched there don't appear in `hermes kanban list` here. Track both via GH issue comments instead (the user-visible surface).
4. Per inventory: route OSS-engineering work (digitalmodel CI, mesh prep, freecad/gmsh/openfoam/blender, gdsfactory, GPU-suitable embeddings) to ace-linux-2. Keep dispatch-ledger-sensitive work (GH-mutation-heavy, Hermes config changes, kanban orchestration) on ace-linux-1.

Cross-references:
- [[feedback_cross_machine_execution]] — per-machine tasks via shared git repo
- [[feedback_hermes_active_preflight_check]] — Hermes-active preflight for git contention
- [[project_hermes_installation]] — Hermes v0.4.0+ install state
- #2696 Hermes routing-layer audit (would have caught this gap)
- #2548 machine-inventory (parent doc deliverable)
- #2712 PATH gap fix (this issue surfaced it)
