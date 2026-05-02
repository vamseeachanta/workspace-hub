# Wave A Session-Close Handoff — 2026-04-24/25

> **Session span:** 2026-04-24 → 2026-04-25
> **Scope:** Wave A OrcaFlex queue from `docs/handoffs/2026-04-24-orcaflex-wave-a-issue-511-handoff.md`
> **Outcome:** #510 ✅ closed earlier · #511 ✅ closed (PR #533 merged) · #504 🟡 kicked off (1/8 slices done)
> **Author:** main session, Opus 4.7 1M context

---

## TL;DR for next session

1. **Read this doc + `workspace-hub/docs/plans/2026-04-24-issue-504-orcaflex-buoys-builder-refactor.md`** — those are the only required inputs to resume.
2. **Run pre-work checklist** (§Resume Checklist below) — verifies branch tip + baseline + locked decisions.
3. **Implement #504 slices 2-8** following the plan's TDD test list (lines 217-247 of the plan). Approach B is locked; do not re-litigate.
4. **No other Wave A work is queued.** After #504, ask user for next priority.

---

## What landed this session

### #510 — OrcaFlex test-drift repair (T1)

| Field | Value |
|---|---|
| Issue | vamseeachanta/digitalmodel#510 |
| State | CLOSED, `status:done` |
| PR | vamseeachanta/digitalmodel#532 (MERGED earlier this session at `b24857e9`) |
| Branch | `issue-510-fix-test-drift @ 19055541` (merged) |
| Test delta | Repaired 4 test files; out-of-scope failures filed to follow-up issues |
| Follow-ups filed | #529 (convert_batch stats bug), #530 (fixture scoping), #531 (umbrella for 9 pre-existing failures) |

### #511 — OrcaFlex campaign spec generation (T2)

| Field | Value |
|---|---|
| Issue | vamseeachanta/digitalmodel#511 |
| State | CLOSED, `status:done` |
| PR | vamseeachanta/digitalmodel#533 (MERGED at `481f17af`, 2026-04-25T10:21:57Z) |
| Branch | `issue-511-campaign-spec-generation @ 1d96aa63` (merged) |
| Slices | 8 atomic + 1 review-fix commit |
| Test delta | +31 net passes; **0 new failures** vs #510 baseline (10F / 997P / 154S / 3E) |
| Code review | `pr-review-toolkit:code-reviewer` 1 MAJOR + 2 MINOR all fixed before push |

#### #511 design decisions locked (durable)

- **A1** — `Literal["full_factorial"]` only; LHS/OAAT not in v1 (no LHS sampler dep added)
- **B1** — `water_depths` is optional; `_validate_axes` model_validator enforces "at least one populated axis" (replaces former `Field(..., min_length=1)`)
- **C1** — `manifest.yml` emitted at output_dir top level in `spec_only=True` mode

#### #511 Path 1 deviation (TDD-surfaced, durable)

`Waves` Pydantic model uses `@model_validator` + `@property` compatibility shim. Input shape `{height: 1.0}` is auto-wrapped into `{trains: [{height: 1.0}]}` during validation; `model_dump()` produces only canonical shape. Setting `environment.waves.height` on the dumped dict silently no-ops (Pydantic v2 default `extra="ignore"`).

**Resolution shipped:** users write **canonical dumped-shape paths** like `environment.waves.trains.0.height`. `_set_nested_safe` gained bounds-checked integer-segment support (`trains.0` → `list[0]`). Full path slug is the auto-fallback when no alias is set.

This generalizes to ANY model with a Pydantic compat shim, not a one-off `Waves` workaround.

#### #511 deferred follow-ups (non-blocking)

Filed on digitalmodel:
- **#534** — `_apply_overrides` direct-call StopIteration guard (defect ID m2)
- **#535** — `apply_dotted_override` should chain ValidationError with dotted-path context (m3)
- **#536** — per-iteration `model_validate` perf for large sweep matrices (m5)
- **#537** — `manifest.yml` not written when all runs skipped — clarify docstring + behavior (m7)

### #504 — OrcaFlex buoys builder refactor (T2, IN PROGRESS)

| Field | Value |
|---|---|
| Issue | vamseeachanta/digitalmodel#504 |
| State | OPEN, `status:plan-approved` (label NOT yet transitioned to `status:working` — fresh session does that at first impl commit per protocol) |
| Branch | `digitalmodel:issue-504-buoys-builder-refactor` pushed to origin, **1 commit ahead of `origin/main`-post-#533** |
| Plan | `workspace-hub/docs/plans/2026-04-24-issue-504-orcaflex-buoys-builder-refactor.md` |
| Slices done | 1 of 8 |
| Decision | **Approach B locked** (orchestrator shim, byte-identical output) — see §504 Approach B Lock below |

#### #504 Slice 1 done

Commit on digitalmodel branch: `refactor(#504): extract DEFAULT_WIREFRAME_VERTICES/EDGES into _buoy_geometry.py`

Files created:
- `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/_buoy_geometry.py` — 8-vertex/12-edge cube wireframe constants extracted **verbatim** from `buoys_builder.py:18-42`
- `digitalmodel/tests/solvers/orcaflex/modular_generator/builders/test_buoy_geometry.py` — `TestBuoyGeometryConstants` (2 passing tests verifying byte-identity)

Note: original constants in `buoys_builder.py` REMAIN unchanged this slice. Slices 2-6 will rewrite `buoys_builder.py` to use the extracted module + delegate to sub-builders. Backward compat preserved during slice-by-slice migration.

#### #504 Approach B Lock (final, do not reopen)

The plan's `[TRADEOFF FOR USER]` at line 286 was unresolved. Locked **Approach B** this session:

- `BuoysBuilder` stays registered at `("08_buoys.yml", order=80)` and becomes a ~60-line orchestrator
- 4 private sub-builders (`RollerBuilder`, `TugBuilder`, `BuoyancyBuilder`, `EndBuoyBuilder`) are plain `BaseBuilder` subclasses **NOT registered** in `BuilderRegistry` — invoked only through the orchestrator
- `BuoysBuilder.get_support_geometry(...)` legacy test call sites (`test_buoys_builder.py:171/190/203/216`) preserved via a `@staticmethod` forwarding shim

**Why B, not A:** preserves public `BuoysBuilder` symbol, no `08_buoys.yml` filename change, no `BuilderRegistry` convention change, no golden-file split, no manifest update. A's only benefit (per-sub-builder enable/disable) has zero callers today. Decision is final.

Rationale recorded in Slice 1 commit body. If a future need surfaces for per-sub-builder toggling, file a separate enhancement issue rather than re-doing #504.

#### #504 slice plan (carry-forward)

| # | Slice | Files (creates / modifies) | Test class focus |
|---|---|---|---|
| 1 | `_buoy_geometry.py` extracted constants | C: `_buoy_geometry.py`, `test_buoy_geometry.py` | `TestBuoyGeometryConstants` ✅ done |
| 2 | `RollerBuilder` (incl. `get_support_geometry` @staticmethod) | C: `roller_builder.py`, `test_roller_builder.py` | 7 tests (per plan §TDD Test List) |
| 3 | `TugBuilder` | C: `tug_builder.py`, `test_tug_builder.py` | 3 tests |
| 4 | `BuoyancyBuilder` | C: `buoyancy_builder.py`, `test_buoyancy_builder.py` | 3 tests |
| 5 | `EndBuoyBuilder` (incl. mid-pipe marker — only 3DBuoy producer) | C: `end_buoy_builder.py`, `test_end_buoy_builder.py` | 4 tests |
| 6 | `BuoysBuilder` orchestrator rewrite + `get_support_geometry` shim | M: `buoys_builder.py` (rewrite to ~60 lines), M: `test_buoys_builder.py` (retain `TestBuoysBuilderShouldGenerate`, drop migrated classes) | shim verification + integration |
| 7 | `__init__.py` exports | M: `builders/__init__.py`, `modular_generator/__init__.py` | import smoke tests |
| 8 | Integration + golden file regression | M: `test_slay_builders.py`, `test_builder_context.py` checks; golden YAML diff | full builders suite + byte-identical `08_buoys.yml` / `_08_buoys_data.yml` |

Each slice ends with an atomic commit `refactor(#504): <slice intent>` referencing the issue. Pattern matches #511's TDD execution that just shipped — see commits `bcc9ff9a..1d96aa63` for the cadence.

#### #504 acceptance criteria (carry-forward from plan §Acceptance Criteria)

- [ ] All slice tests pass: `uv run --project digitalmodel pytest digitalmodel/tests/solvers/orcaflex/modular_generator/builders/ -v`
- [ ] No regression: `uv run --project digitalmodel pytest digitalmodel/tests/solvers/orcaflex/ -v` — failure set MUST be identical to #510 baseline (10F / 997P / 154S / 3E now that #511 has merged)
- [ ] **Golden-file byte-identity**: `digitalmodel/tests/output/test_cli_base/08_buoys.yml` and `_08_buoys_data.yml` byte-identical pre vs post refactor — regenerate fresh, diff against checked-in copy
- [ ] Output ordering preserved: emitted `6DBuoys` list reads `rollers → tugs → BM → end_buoy` (positional indices match)
- [ ] `lines_builder.py:44` reads non-None `end_buoy_name` from context in integration run
- [ ] `grep -rn "BuoysBuilder\|get_support_geometry" digitalmodel/` — every hit either uses new API or goes through shim (no orphan references)
- [ ] PR opened against digitalmodel main, evidence comment posted on #504, label transition `status:plan-approved → status:working` at first impl commit, then `status:done` only at user merge

---

## Resume Checklist (for fresh session resuming #504)

- [ ] Read this handoff in full
- [ ] Read `workspace-hub/docs/plans/2026-04-24-issue-504-orcaflex-buoys-builder-refactor.md` — especially §TDD Test List (lines 217-247) and §Risks (TRADEOFF resolution at line 286, **already locked Approach B**, do not re-litigate)
- [ ] Confirm digitalmodel branch tip:
   ```
   git -C /mnt/local-analysis/workspace-hub/digitalmodel fetch origin
   git -C /mnt/local-analysis/workspace-hub/digitalmodel log --oneline origin/issue-504-buoys-builder-refactor -3
   ```
   First line should be the Slice 1 commit (`refactor(#504): extract DEFAULT_WIREFRAME_VERTICES/EDGES into _buoy_geometry.py`); parent should be `481f17af` (post-#533 merge on digitalmodel main)
- [ ] Confirm baseline passes:
   ```
   uv run --project /mnt/local-analysis/workspace-hub/digitalmodel pytest /mnt/local-analysis/workspace-hub/digitalmodel/tests/solvers/orcaflex/modular_generator/builders/ -q
   ```
   Should be all green (Slice 1 added 2 passing tests; rest of builders/ suite was green pre-#511 and #511 added more)
- [ ] Read `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/buoys_builder.py` — only 610 lines, full read is fine
- [ ] Read `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/registry.py` — confirm `_registry` dict semantics; do NOT modify (Approach B preserves it)
- [ ] Read `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/builders/context.py` lines 38-44 — typed `BuilderContext` fields (`buoy_names_6d`, `buoy_names_3d`, `all_buoy_names`, `end_buoy_name`, `bm_buoy_name`, `roller_buoy_names`); sub-builders own subsets, orchestrator aggregates `all_buoy_names`
- [ ] Read 2-3 sibling builders (`environment_builder.py`, `vessel_builder.py`, `winch_builder.py`) to confirm the DELTA pattern your sub-builders match
- [ ] At first impl commit (Slice 2 RED), transition label: `gh issue edit 504 --repo vamseeachanta/digitalmodel --remove-label "status:plan-approved" --add-label "status:working"`

---

## Operational protocols (from #511 session, carry-forward)

These were validated end-to-end on #511 and apply to #504 unchanged.

1. **TDD MANDATORY** — failing tests first per slice, then minimum impl. Watch the test fail before writing code. Watch it pass before next slice.
2. **Atomic commits per slice** — one commit per logical change, message references `#504`. Body documents intent + test count delta.
3. **Stage + commit in one turn whenever feasible** — closes the auto-sync window that scooped Slice 4's RED tests in #511 (`feedback_autosync_silent_pusher`).
4. **NEVER `status:done` without user sign-off** per `feedback_never_offer_to_self_label_plan_approved`. Even with "no user approvals required," that gate is at PR merge time, not implementation completion.
5. **Plan-defect escalation**: if implementation reveals plan is wrong, STOP and surface to user (don't silently re-plan). #511 Path 1 was found this way; user-approved revision in chat unblocked Slice 2.
6. **Code-review pass before push**: spawn `pr-review-toolkit:code-reviewer` against the slice diff before opening PR. #511 caught 1 MAJOR + 2 MINOR via this path (commit `1d96aa63`).
7. **Verify each code review finding** per `superpowers:receiving-code-review` — confirm with `grep`/`Read` before fixing. Don't blindly accept all findings; reviewer can be wrong.
8. **#510 baseline as ground truth** — the #510 PR commit body is a frozen attestation of pre-existing failures (`feedback_attestation_enables_contradiction_detection`). Diff against it; don't re-discover known issues as if new.

---

## Environmental hazards (carry-forward, validated on #511)

- **Auto-sync silent push** — `feedback_autosync_silent_pusher`. Auto-sync may push commits between your stage and explicit-push moments. Verify with `git rev-parse HEAD origin/issue-504-buoys-builder-refactor` after each commit.
- **Auto-sync history split** — variant of above: long pause between RED stage and GREEN commit gave auto-sync a window to capture tests in a `chore(sync)` commit. Mitigation: commit RED tests + GREEN impl in same turn whenever possible.
- **Multi-session uv lock contention** — single-session work is the safe default. Before starting heavy pytest runs, scan `ps aux | grep "uv run"` for parallel sessions; if found, wait or coordinate. #511 hit this once (~5 min block).
- **First `uv run pytest` of a session** recompiles bytecode (~1:40s the first time, longer if env was perturbed). Budget for it. Subsequent runs in same session are ~5s for schema/, ~45s for full builders/.
- **`tests/solvers/orcaflex/` full suite** takes ~16-17 min wall time (last run was 1005s, 60-thread orcaflex-univer subprocess). Use `tests/solvers/orcaflex/modular_generator/builders/` for fast iteration; full suite only at end of slice 8 verification.
- **`tests/solver/` directory is OrcFxAPI-gated** via `conftest.py` auto-mark. New sub-builder tests belong under `tests/solvers/orcaflex/modular_generator/builders/` (note plural `solvers/`, not `solver/`).
- **Workspace-hub branch drift** — this session encountered an unannounced branch switch from `main` → `plan/issue-2364-batch-pack-1` mid-turn. The earlier `0ff8cb033` #504 handoff commit landed on the wrong branch and is invisible from main. Always check `git -C workspace-hub branch --show-current` before making workspace-hub commits, especially around docs/plans/ and docs/handoffs/.

---

## SHA reference card

| Where | SHA | What |
|---|---|---|
| digitalmodel main (post-Wave A) | `481f17af` | Merge of #533 (#511 implementation) |
| digitalmodel main (pre-Wave A) | `b24857e9` | Merge of #532 (#510 test-drift repair) |
| digitalmodel `issue-504-buoys-builder-refactor` HEAD | (Slice 1 commit) | _buoy_geometry.py extracted |
| #511 commit chain | `bcc9ff9a..1d96aa63` | 9 #511 commits + 1 auto-sync interleaved |
| workspace-hub `plan/issue-2364-batch-pack-1` | `0ff8cb033` | Earlier #504-only handoff doc (different branch, file not on main) |

---

## What's NOT in scope for #504

- Registry convention change (Approach A) — explicitly rejected
- Per-sub-builder external toggle/enable/disable — would require Approach A; not requested by any caller
- Adding LHS or OAAT support to ParameterSweep — that's an enhancement to #511's work, file as separate issue if needed
- Changing `08_buoys.yml` filename or layout — golden-file byte-identity is mandatory
- Fixing the 10 pre-existing failures from #510 baseline — those are tracked in #531 umbrella + sibling follow-ups; do NOT touch them in #504

---

## After #504 lands

Possible next priorities (none currently scheduled — ask user):

- Address #534-#537 deferred minor findings from #511 (each is small + isolated)
- New work from elsewhere in the OrcaFlex/OrcaWave queue (per `docs/handoffs/2026-04-24-orcaflex-orcawave-batch-execution-handoff.md` if still active)
- User-driven new direction
