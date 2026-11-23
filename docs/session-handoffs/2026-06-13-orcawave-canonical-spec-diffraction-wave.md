# Session Handoff — OrcaWave canonical spec → diffraction run (digitalmodel #622 wave)

> **Date:** 2026-06-13 · **Host:** ace-linux-2 · **Repo:** vamseeachanta/digitalmodel
> **Objective:** a canonical high-level `spec.yml` that runs an OrcaWave diffraction analysis end-to-end without errors (epic [#622](https://github.com/vamseeachanta/digitalmodel/issues/622)).
> **Durable memory:** `~/.claude/projects/-mnt-local-analysis/memory/orcawave-canonical-spec-objective.md`

## Status: objective NOT yet met — one acceptance gate open ([#610](https://github.com/vamseeachanta/digitalmodel/issues/610))

The full canonical-spec → OrcaWave pipeline is built, merged, and mock-green (diffraction suite ~1959 passing). The first **licensed** run (codex, Windows, 2026-06-13) failed on a malformed fixture mesh; that defect is fixed and merged; a **second licensed run was re-dispatched in codex** and its evidence is pending on [#610](https://github.com/vamseeachanta/digitalmodel/issues/610). The objective is met only when a green licensed #610 run is posted and hand-verified.

## Shipped this wave (all merged to digitalmodel main)

| Issue | PR | What |
|---|---|---|
| [#712](https://github.com/vamseeachanta/digitalmodel/issues/712) | #720 | Canonical runnable example `examples/hydrodynamics/diffraction/unit_box_rao/` + CI dry-run guard |
| [#713](https://github.com/vamseeachanta/digitalmodel/issues/713) | #727 | `python -m digitalmodel <subcommand>` routing fix |
| [#614](https://github.com/vamseeachanta/digitalmodel/issues/614) | #728 | OrcaWave README rewritten against the real CLI |
| [#500](https://github.com/vamseeachanta/digitalmodel/issues/500) | #730 | Hard-fail mesh preflight in SpecConverter |
| [#605](https://github.com/vamseeachanta/digitalmodel/issues/605) | #731 | Self-contained convert-spec packages (shared `mesh_packaging` module) |
| [#606](https://github.com/vamseeachanta/digitalmodel/issues/606) | #733 | MeshPipeline wired into convert + run (GDF passthrough, .dat/.stl conversion, provenance) |
| [#608](https://github.com/vamseeachanta/digitalmodel/issues/608) | #734 | Mesh quality gates (FAIL blocks / WARNING reports) + fixed 2 quad-panel crashes |
| [#609](https://github.com/vamseeachanta/digitalmodel/issues/609) | #736 | Body-level control surfaces resolved everywhere |
| [#613](https://github.com/vamseeachanta/digitalmodel/issues/613) | #737 | `diffraction orcawave-doctor` readiness command |
| [#501](https://github.com/vamseeachanta/digitalmodel/issues/501) | #738 | QTF options + field points + irregular-freq method (approved r2 plan; 12-fixture byte-identity corpus) |
| [#740](https://github.com/vamseeachanta/digitalmodel/issues/740) | #741 | OrcaWave-valid GDF fixtures + GDF structural preflight + CLI exit-1-on-FAILED |

Triage closed: [#62](https://github.com/vamseeachanta/digitalmodel/issues/62) (superseded by #622), [#607](https://github.com/vamseeachanta/digitalmodel/issues/607) (covered by `diffraction resolve` #623).

## The licensed-run failure and fix (root cause, hand-verified)

- First licensed run: `Error code 63 — Unrecognised header ... line 2`. The unit_box/sample_box fixture GDFs carried **three** leading `#` comment lines; WAMIT GDF permits exactly one header line (line 2 must be `ULEN GRAV`). BEMRosetta's reader tolerantly skips extra comments (masked it on every unlicensed host); its writer is valid (so #606-converted meshes were never at risk). Only hand-authored fixtures were malformed — 5 copies found and fixed repo-wide in #741.
- L00 smoke PASSED on that host → environment + license are fine. L01 OOM is the separate known [#714](https://github.com/vamseeachanta/digitalmodel/issues/714) pattern.
- #741 also added a blocking GDF structural preflight (catches this class at dry-run on any host) and fixed `run-orcawave`/`run-aqwa` exiting 0 on a FAILED result.

## Next actions (in order)

1. **Re-run the licensed #610 gate** (codex, in flight as of session exit). Runbook is on [#610](https://github.com/vamseeachanta/digitalmodel/issues/610): sync main → `diffraction orcawave-doctor --require-solver` → `pytest tests/solver/test_licensed_e2e_arbitrary_mesh.py -v` → `diffraction run-orcawave examples/hydrodynamics/diffraction/unit_box_rao/spec.yml -o output_610\`. **Hand-verify the codex evidence** before acting (standing codex rule). If green → close #610 + confirm the objective on #622.
2. [#612](https://github.com/vamseeachanta/digitalmodel/issues/612) convergence/sensitivity workflow — `status:plan-review`, needs **user plan approval** before build (never self-approve).
3. [#714](https://github.com/vamseeachanta/digitalmodel/issues/714) L01 OOM + AQWA correlation — needs `licensed-win-1`, lane:codex.
4. Longer-horizon per #622 roadmap: #464/#465 (Capytaine), #282/#270/#269 (reporting/demo), #170/#141 (benchmarks), AQWA generalization.

## Repo / clean-state

- **digitalmodel** main clone (`/mnt/local-analysis/digitalmodel`): on `main`, no session residue. (Clone HEAD lags GitHub main — bot-owned; do not pull, shared-clone hazard.) All session work was done in `/tmp/wt-*` worktrees, now removed. `/tmp/dm-calc` is the bot's calc worktree — left untouched.
- **No external actions taken** beyond GitHub PRs/issue comments on digitalmodel and this handoff.
- Lessons captured to memory this wave: shared-clone branch-switching mid-command; Pydantic deprecated-alias revalidation needs `Field(exclude=True)` + `fields_set.discard`; `git add -A` sweep contamination (benchmark-html churn) — use pathspec commits.
