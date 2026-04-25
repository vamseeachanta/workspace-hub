# Execution Handoff — OrcaFlex #504 buoys builder refactor (slices 2-8)

> **Prior session:** 2026-04-24/25 closed #511 OrcaFlex campaign spec (PR #533 merged at digitalmodel SHA `481f17af`), kicked off #504 with locked design decision + Slice 1 committed.
> **Plan:** `workspace-hub/docs/plans/2026-04-24-issue-504-orcaflex-buoys-builder-refactor.md`
> **Issue:** vamseeachanta/digitalmodel#504 (OPEN, `status:plan-approved`)
> **Branch:** `issue-504-buoys-builder-refactor` on digitalmodel, pushed to origin, 1 commit ahead of `origin/main` (post-#533 merge)

---

## Current state at handoff

| Item | Status |
|---|---|
| Plan | `status:plan-approved`, full Resource Intel + Pseudocode + 23-test TDD list documented |
| Branch | `digitalmodel:issue-504-buoys-builder-refactor` pushed at first slice commit |
| Slice 1 | ✅ committed — `_buoy_geometry.py` + test_buoy_geometry.py (2 passing tests) |
| Slices 2-8 | Pending |
| Approach decision | **B (orchestrator shim) — LOCKED**, recorded in Slice 1 commit body |

## Approach B decision rationale (locked, no re-litigation)

`BuoysBuilder` stays registered at `("08_buoys.yml", order=80)` and becomes a ~60-line orchestrator. Four private sub-builders (`RollerBuilder`, `TugBuilder`, `BuoyancyBuilder`, `EndBuoyBuilder`) are plain `BaseBuilder` subclasses NOT registered in `BuilderRegistry` — they are invoked only through the orchestrator.

**Why B, not A:**

- Public `BuoysBuilder` symbol preserved → zero break for `test_slay_builders.py`, `__init__.py` re-exports, any external import
- `08_buoys.yml` filename unchanged → zero include-manifest change, zero golden-file split, zero downstream-consumer break
- `BuoysBuilder.get_support_geometry(...)` legacy test call sites (`test_buoys_builder.py:171/190/203/216`) stay green via a `@staticmethod` forwarding shim
- Zero registry convention change — `_registry` dict semantics unchanged
- Output emitted byte-for-byte unchanged → trivial golden-file invariant

**A's alleged flexibility benefit (per-sub-builder enable/disable) is not used by any code path today.** Buying flexibility nobody requests at the cost of a registry convention change + manifest change + fixture split + public API break is a bad trade. Decision is final; do not reopen.

## Slice plan (8 atomic, TDD-driven)

| # | Slice | Files (creates / modifies) | Test class |
|---|---|---|---|
| 1 | `_buoy_geometry.py` extracted constants | C: `_buoy_geometry.py`, `test_buoy_geometry.py` | `TestBuoyGeometryConstants` ✅ done |
| 2 | `RollerBuilder` (incl. `get_support_geometry` @staticmethod) | C: `roller_builder.py`, `test_roller_builder.py` | `TestRollerBuilder*` (7 tests per plan) |
| 3 | `TugBuilder` | C: `tug_builder.py`, `test_tug_builder.py` | `TestTugBuilder` (3 tests per plan) |
| 4 | `BuoyancyBuilder` | C: `buoyancy_builder.py`, `test_buoyancy_builder.py` | `TestBuoyancyBuilder` (3 tests per plan) |
| 5 | `EndBuoyBuilder` (incl. mid-pipe marker) | C: `end_buoy_builder.py`, `test_end_buoy_builder.py` | `TestEndBuoyBuilder` (4 tests per plan) |
| 6 | `BuoysBuilder` orchestrator rewrite + `get_support_geometry` shim | M: `buoys_builder.py` (rewrite to ~60 lines), M: `test_buoys_builder.py` (retain `TestBuoysBuilderShouldGenerate`, drop migrated classes) | shim verification + integration |
| 7 | `__init__.py` exports | M: `builders/__init__.py`, `modular_generator/__init__.py` | import smoke tests |
| 8 | Integration + golden file regression | M: existing tests, golden-file diff | full builders suite + golden YAML byte-identity |

Each slice ends with an atomic commit `refactor(#504): <slice intent>` referencing the issue. Pattern matches #511's TDD execution that just shipped (PR #533 merged) — see commits `bcc9ff9a..1d96aa63` for the cadence.

## Pre-work checklist for fresh session

- [ ] Read this handoff in full
- [ ] Read the plan at `workspace-hub/docs/plans/2026-04-24-issue-504-orcaflex-buoys-builder-refactor.md` — especially §TDD Test List (lines 217-247) and §Risks (TRADEOFF resolution at line 286)
- [ ] Confirm branch tip: `git -C digitalmodel log --oneline origin/issue-504-buoys-builder-refactor -3` should show Slice 1 commit at HEAD, parent = `481f17af` (post-#533 merge on `origin/main`)
- [ ] Confirm baseline passes: `uv run --project digitalmodel pytest digitalmodel/tests/solvers/orcaflex/modular_generator/builders/ -q` — should be all green (last #511 baseline showed 615+ passes in modular_generator suite, 3 pre-existing failures elsewhere)
- [ ] Read `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/buoys_builder.py` — only 610 lines, full read is fine
- [ ] Read `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/registry.py` — confirm `_registry` dict semantics; do NOT modify (Approach B preserves it)
- [ ] Read `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/context.py` lines 38-44 — typed `BuilderContext` fields (`buoy_names_6d`, `buoy_names_3d`, `all_buoy_names`, `end_buoy_name`, `bm_buoy_name`, `roller_buoy_names`) — sub-builders own subsets, orchestrator aggregates `all_buoy_names`

## Acceptance criteria (carried from plan)

- [ ] All slice tests pass (sub-builder tests + integration)
- [ ] `uv run --project digitalmodel pytest digitalmodel/tests/solvers/orcaflex/modular_generator/builders/` — all green
- [ ] `uv run --project digitalmodel pytest digitalmodel/tests/solvers/orcaflex/` regression — diff vs post-#511 baseline (997 passed / 10 failed / 154 skipped / 3 errors); failure set MUST be identical
- [ ] **Golden-file byte-identity**: `digitalmodel/tests/output/test_cli_base/08_buoys.yml` and `_08_buoys_data.yml` byte-identical pre vs post refactor (regenerate fresh, diff against checked-in copy)
- [ ] Output ordering preserved: emitted `6DBuoys` list still reads `rollers → tugs → BM → end_buoy` (positional indices match)
- [ ] `lines_builder.py:44` reads non-None `end_buoy_name` from context in integration run
- [ ] `grep -rn "BuoysBuilder\|get_support_geometry" digitalmodel/` — every hit either uses new API or goes through shim
- [ ] Atomic commits, one per slice, referencing #504
- [ ] PR opened against digitalmodel main, evidence comment posted on #504, label transition `status:plan-approved → status:working`, then `status:done` only at user merge

## Environmental hazards (carried from #511 session)

- **Auto-sync silent push** — `feedback_autosync_silent_pusher`. Auto-sync may push commits between your stage and explicit-push moments. Closer test+impl commits keep the window short. Verify with `git -C digitalmodel rev-parse HEAD origin/issue-504-buoys-builder-refactor` after each commit.
- **Auto-sync history split** — `feedback_autosync_silent_pusher` variant: if you have unstaged tests during a long pause (e.g. running pytest), auto-sync may capture them in a `chore(sync)` commit before your impl commit. Mitigation: stage + commit in one turn.
- **Multi-session uv lock contention** — single-session work is the safe default. Before starting heavy pytest runs, scan `ps aux | grep "uv run"` for parallel sessions; if found, wait or coordinate.
- **First `uv run pytest` of a session** recompiles bytecode (~1:40s the first time, longer if env was perturbed). Budget for it.
- **`tests/solvers/orcaflex/` full suite** takes ~16-17 min wall time (last run was 1005s). Use `tests/solvers/orcaflex/modular_generator/builders/` for fast iteration; full suite only at end of slice 8 verification.
- **`tests/solver/` directory is OrcFxAPI-gated** via `conftest.py` auto-mark. New sub-builder tests belong under `tests/solvers/orcaflex/modular_generator/builders/` (note plural `solvers/`, not `solver/`).

## Reference: #511 protocol echoes

Same protocols #511 used and that worked:

1. **TDD MANDATORY**: failing tests first per slice, then minimum impl.
2. **Atomic commits per slice** — one commit per logical change, message references `#504`.
3. **Label transition `status:plan-approved → status:working`** at first impl commit (Slice 1 already committed but label not yet transitioned — fresh session should transition at start).
4. **NEVER `status:done`** without user sign-off per `feedback_never_offer_to_self_label_plan_approved`.
5. **Plan-defect escalation**: if implementation reveals plan is wrong, STOP and surface to user (don't silently re-plan). #511 hit this once (Path 1 / Pydantic compat-shim discovery) — surfaced cleanly, user approved revision in chat, Slice 2 proceeded.
6. **Code-review pass before push**: spawn `pr-review-toolkit:code-reviewer` against the slice diff before opening PR. #511 caught 1 MAJOR + 2 MINOR this way (commit `1d96aa63`).

## Reference: deferred follow-ups for parent #504

None at this point. If sub-builder work surfaces follow-ups (e.g. registry convention enhancement, per-sub-builder toggle support), file as separate issues — keep #504 narrowly scoped to "split mega-builder into 4 SRP builders, byte-identical output."

## Branch tip + base SHAs

- `origin/main` of digitalmodel: `481f17af` (post-#533 merge of #511)
- `origin/issue-504-buoys-builder-refactor`: Slice 1 commit (extract `_buoy_geometry.py`)
- workspace-hub `main`: includes plan at `docs/plans/2026-04-24-issue-504-orcaflex-buoys-builder-refactor.md`, this handoff
