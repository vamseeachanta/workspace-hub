# Compute program: plan and status

Tracking issue: #4034. Last updated: 2026-10-09 (evening, US Central).

This is the single plan and status file for the compute program: a balanced set
of licensed-solver and open-source solver workstreams, each ending in a result
that can be shown to a client.

This repository is public. Machines are named by registry role label only
(`config/workstations/registry.yaml`). Host paths, licence details, receipts and
anything client-specific stay on the private side.

## Portfolio

| # | Workstream | Deliverable | Runs on | State |
|---|---|---|---|---|
| 1 | Fleet solver baseline (digitalmodel#2300 follow-on) | Cross-machine timing and reproducibility report for OrcaFlex, OrcaWave, AQWA, MAPDL, OpenFOAM | OpenFOAM leg: dev-primary, dev-secondary. Licensed leg: licensed-win-1 | OpenFOAM leg done on dev-primary. Licensed leg not run. |
| 2 | Licensed vs open-source diffraction | One box barge through OrcaWave, AQWA and Capytaine; heave added mass and heave RAO compared | Capytaine: dev-primary. Licensed: from workstream 1 | Capytaine leg done. Waiting on the licensed leg. |
| 3 | OpenFOAM known-answer case study (digitalmodel#1161) | Client-facing summary of the known-answer cases, re-run independently at a pinned commit | dev-primary | Six cases re-running. |
| 4 | Matched AQWA/OrcaWave 13-hull benchmark (digitalmodel#2140) | Report draft reviewed and issued | Agent work, no compute | Not started. Draft is in the private data repository. |
| 5 | Drilling-riser coupling-station timing probe (digitalmodel#2297) | Measured cost of the 0.1 m coupling segments, required before any batch | The single Orcina seat, licensed-win-1 | Not started. Needs the seat and the private case matrix. |

Left out for now: KCS calm-water resistance (digitalmodel#1173; all four
acceptance criteria currently fail and each extra point costs about a day of
compute) and the MAPDL thick-cylinder canary (digitalmodel#2121; waiting on
owner approvals).

## Results so far

### Workstream 1: OpenFOAM baseline on dev-primary

Pack version 1, digitalmodel `4f7bfc0c`, OpenFOAM v2312, motorBike tutorial,
100 iterations, 353,578 cells, 3 timed repeats after 1 warm-up, host idle.

| MPI ranks | Median solve time | Cd across repeats | Result |
|---|---|---|---|
| 8 (first run) | 34.9 s | 0.41905, 0.41915, 0.41873 | consistent |
| 8 (second run) | 34.9 s | 0.41927, 0.41865, 0.41922 | spread just over the 1e-3 tolerance |
| 16 | 33.1 s | 0.41844, 0.41875, 0.41871 | consistent |

Findings:

- Going from 8 to 16 ranks saves about 5 % on this case on this host. The case
  is too small to scale past 8 ranks here.
- Cd repeats to about 1e-3 between identical runs, which is the pack's
  tolerance. One of two 8-rank runs fell just outside it. Either the tolerance
  or the iteration count needs revisiting before this is used as a pass/fail
  gate.
- The pack's "all cores" variant asks for logical cores and Open MPI refuses it
  on a hyperthreaded host. Filed as digitalmodel#2320; the 16-rank figure above
  was taken with an explicit rank count.

### Workstream 2: Capytaine leg of the barge comparison

Same 100 x 20 x 8 m barge, 1,460 panels, 20 frequencies, 200 m depth and mass
properties as the pack's OrcaWave and AQWA cases. Capytaine 3.0.0, 15 s solve.

| Frequency (rad/s) | Heave added mass (te) | Heave RAO at 0 deg |
|---|---|---|
| 0.34 | 30,043 | 0.957 |
| 0.83 | 15,172 | 0.209 |
| 1.32 | 18,150 (17,669 with interior lid) | 0.0067 (0.0059 with lid) |

The third sample frequency sits close to the barge's first irregular frequency;
the lid changes heave added mass there by 2.7 %. The licensed solvers need the
same treatment stated before the three are compared. No licensed numbers are
in hand yet, so there is no comparison to report.

### Workstream 3

Six cases started on dev-primary (cylinder Re=100, laminar flat plate,
turbulent flat plate, dam break, wave tank, NACA 0012 polar). Results pending.

## What is running where

| Role | Now | Next |
|---|---|---|
| dev-primary | Workstream 3 re-runs (six serial OpenFOAM cases) | Remaining known-answer cases; report builds |
| dev-secondary | Another session's CFD chain holds all physical cores. Not touched. | OpenFOAM baseline once that chain ends |
| licensed-win-1 | Other sessions' AQWA and riser jobs. Nothing added by this program. | Licensed baseline leg in a quiet window (see blockers) |
| licensed-win-2 | No solver work: short of memory, and its run-queue checkout is under repair by the sync session | None planned |

## Blockers and decisions needed

1. **Licensed baseline leg.** The host was busy and the pack refuses to
   baseline a busy host. Staging a job there that waits for a quiet window was
   not permitted from the coordinating session. It needs either an owner-run
   command or an explicit permission.
2. **Agent coding work on the licensed host.** Launching a headless agent there
   was not permitted from the coordinating session. A worktree and prompt for
   digitalmodel#2320 plus the cross-machine report generator are staged.
3. **Run queue.** Only one licensed runner is healthy, it is serial behind one
   seat, and multi-case OrcaFlex sweeps are not on the allowlist. Workstream 5
   cannot go through the queue as it stands.

## Next steps

1. Collect workstream 3 results and publish the case-study summary.
2. Run the licensed baseline leg in a quiet window; then publish the
   cross-machine baseline report and the three-solver barge comparison.
3. Fix digitalmodel#2320 and add the report generator deferred by #2300.
4. Run the OpenFOAM baseline on dev-secondary when its current chain finishes.
5. Review and issue the 13-hull report (workstream 4).
