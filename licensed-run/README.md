# licensed-run — ace-win-2 go-live helpers

Reusable scripts for bringing the Deckhand licensed-run lane live on **ace-win-2**
(the Windows / OrcaFlex-licensed host) for one private client scope
(workflow `orcaflex-strength-post`). The scope id and its private checkout are
not named here; they come from the environment (see below).

Authoritative runbook: `deckhand/docs/deckhand/licensed-run-go-live-ace-win-2.md`.

## Scripts (committable)
- `validate_sim.py` — load a `.sim` via OrcFxAPI and confirm it's a solved model with a Line + the strength variables. `python validate_sim.py <path.sim>`.
- `build_strength_sim.py` — real licensed solve of an Orcina riser model → `strength_loadcase.sim` (statics + short dynamics). `python build_strength_sim.py [src.dat] [dst.sim]`.
- `setup_verify.bat` — regenerate the host-local policy override (`execution_enabled: true`) into `runtime\` and run verify-first (writes the marker on 9/9 PASS).
- `agent_once.bat` — single test poll of the licensed-run agent.
- `agent_poll.bat` — continuous poller (heartbeat loop), logs to `runtime\agent_poll.log`.

## runtime\ (gitignored — host-local state, never committed)
- `policy.host-local.yml` — copy of `deckhand` policy with `execution_enabled: true` (host-local override; NOT committed to the shared deckhand repo).
- `licensed-run.verified.json` — the verify marker (agent runs only when this + `execution_enabled` are both present).
- `agent_poll.log` — poller heartbeat + run output.

## Environment the operator sets (private; never committed)
- `LICENSED_RUN_SCOPE` — the Deckhand scope id the agent serves.
- `LICENSED_RUN_SCOPE_REPO` — absolute path of that scope's private checkout.

Every script that needs either stops with `exit /b 2` when it is unset
(`build_strength_sim.py` stops unless a target path is given).

## Environment the scripts set
- `VIRTUAL_ENV=C:\ws\digitalmodel\.venv` — the env carrying `digitalmodel` + `assetutilities` + the OrcaFlex 11.6 `OrcFxAPI` binding (added via a `.pth`). `uv run` honours it.
- `DECKHAND_LICENSED_RUN_VERIFY_MARKER` → `runtime\licensed-run.verified.json` — REQUIRED, or the agent can't find the marker and denies all runs.

## Run order
1. `setup_verify.bat` → expect `PASS` (9/9) + marker written.
2. `agent_poll.bat` → leave the window open; it polls every 15s.

The OrcaFlex `.sim` and heavy outputs stay on this host (gitignored in the scope
repo); only metadata results land in the queue repo.
