# Session handoff — fleet dispatch ecosystem: gpu-claw onboarded, smoke GREEN (2026-07-12/13)

**EPIC:** #3497 (ace-linux-1 single dispatch surface; all other machines headless).
Sensitive topology detail (addresses, tunnels, services) lives in the PRIVATE
admin repo's `machine-ecosystem/` and the private deckhand issues — not here.

## Outcome (one line)

The first Linux execution host (gpu-claw, CFD/OpenFOAM) is live on the outbound-only
dispatch lane: fleet heartbeat ×5 machines, and the phase-6 dispatch smoke
**finished rc 0** returning only the contract csv/json — dm#1560 CLOSED.

## What merged today (all human-merged, content-verified)

| Repo | PR | What |
|---|---|---|
| deckhand | #560 | gpu-claw first Linux execution host: openfoam-run-batch policy, systemd agent+watchdog units + installer, 7-phase onboarding runbook, skill producer-vs-execution-host contract |
| deckhand | #561 | host verifier generalized (`--supervisor systemd-user`, `--workflow-family openfoam`); runbook gained the missing gate-7 marker phase |
| deckhand | #562 | agent runs solver with `cwd = solver_root` (policy/env), fixing Linux `uv` project resolution; installer writes `DECKHAND_LICENSED_RUN_SOLVER_ROOT` |
| digitalmodel | #1561 | `openfoam-run-batch` workflow (pool 0.9×cores / mpi modes, atomic checkpoints, results contract, mock mode, MPI `resume: latestTime`) — adversarial review pre-merge killed 2 HIGH bugs (unconditional `processor*` prune destroying output under `reconstruct:false`; 12h-kill retry livelock) |
| digitalmodel | #1563 | missing engine base-config yml + engine-path regression test (the class-fix) |
| llm-wiki-acma | #238 | mock canary input `cases/openfoam-run-batch/input.yml` |
| aceengineer-admin | #39, #40 | machine-ecosystem map (admin tier): collector + 5 machine rows (3 live self-reports) + HTML matrix |

## OPEN / awaiting owner

- **deckhand PR #563** — `watch` leak-check false-positive (`.csv` counted heavy;
  contract allows csv/json). One-line suffix-list alignment. Merge:
  `gh pr merge 563 --squash --delete-branch --repo vamseeachanta/deckhand`
- **deckhand#557** remaining acceptance: reboot test (linger enabled), optional
  stage-2 real solve (mock:false), then **phase-7 access-path retirement** —
  ≥48h soak running since 2026-07-12 15:59Z; overnight the inbound path flapped
  while outbound heartbeats kept flowing (pro-retirement evidence). ⚠️ The VPN
  endpoint is NOT on gpu-claw itself — identify the tunnel topology (see private
  machine map) before removing anything.
- **deckhand#558** — producer/control-plane migration to ace-linux-1 (ace-linux-2
  already runs an execution-disabled standby; promotion = flip + verifier marker).
  Paste-in prompt ready: `/mnt/local-analysis/HANDOVER-onboard-ace-linux-2-execution-host.md`
  (local file on ace-linux-1; updated with today's verified invocations — commit it
  to `docs/deckhand/` as a follow-on).
- **dm#1564** — orcaflex_run_batch has the SAME missing base-config gap (will fail
  the planned ace-win-1 batch canary; fix mirrors dm PR #1563).
- **dm#1565** — batch work dirs land inside the scope checkout; fix before real
  multi-GB CFD runs.
- **deckhand#559** — L3 minimal-agent design (deferred by design).
- **admin#38** — dedicated AI provider accounts per headless machine (owner).
- **wh#3498/#3499** — equality-matrix pointer to the admin map; zero-touch hygiene
  rollout (fleet ff-sync generalization).
- Windows hosts (ace-win-1/2) still need the one-time watchdog re-registration
  (no `code_sha` in their heartbeats; no auto code sync until then).

## Fleet state at exit

All five machines beat into `queue/heartbeat/` (two Windows executors, two Linux
standbys, gpu-claw executor). The three Linux agents track deckhand main
automatically (watchdog, dedicated clones). gpu-claw: `execution_enabled: true` +
verifier marker present; solver-root env set; inert WorkingDirectory drop-in removed;
scope checkout clean.

## Lessons encoded (memory + issues; the two biggest)

1. **Verify against origin, not local checkouts** — two same-day incidents
   (deckhand stale branch; digitalmodel "missing" CFD surface that was on main).
2. **The smoke run is the integration test**: five attempts burned four real,
   distinct defects (gate-7 verifier Windows-bound; missing base-config;
   cwd/uv project resolution; leak-check drift) — each now fixed on main with a
   regression pin, before any production CFD batch or licensed-seat time was at risk.

## Dirty/local exceptions (intentional)

- `/mnt/local-analysis/HANDOVER-onboard-ace-linux-2-execution-host.md` — local
  runbook awaiting commit to deckhand docs (next session).
- Host-local (by design, never committed): gpu-claw policy override + env file +
  verifier marker; ace-linux-1/2 standby policy overrides.
- No unpushed commits in any working clone; session scratchpad clones are disposable.

## Next step (ONE)

Merge deckhand PR #563, then let the soak run — the next session picks up either
the phase-7 retirement checklist (after the reboot test + tunnel-topology check)
or the ace-linux-2 promotion prompt.
