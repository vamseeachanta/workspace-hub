# Lane C3 — plan-review hardener (ace-linux-1, Claude)

> **Window:** 2026-04-28 21:49 → 2026-04-29 09:49 local (12h continuation lane)
> **Mode:** planning/review only — no implementation, no GitHub mutations
> **Provider:** Claude
> **Companion artifact:** [`plan-review-command-pack.md`](plan-review-command-pack.md)

---

## 0. Live state snapshot (verified 2026-04-28 22:00 CDT via `gh issue view`)

| Issue | State | Labels (key) | Plan on disk? | Plan on `main`? | Worktree-correct? |
|---|---|---|---|---|---|
| #2510 | OPEN | `status:plan-review`, `priority:medium`, `cat:engineering`, `cat:tooling`, `domain:semiconductor`, `domain:chip-design` | yes — `docs/plans/2026-04-26-issue-2510-python-layout-cad-automation-demo.md` | yes (commits `f8a96de2c` r13 patch + 12 prior) | yes |
| #2490 | OPEN | `status:plan-review`, `priority:medium`, `cat:infrastructure`, `enhancement` | yes — `docs/plans/2026-04-27-issue-2490-coverage-gate-fix.md` | yes (commit `f14872956`) | yes |
| #2509 | OPEN | `priority:high`, `cat:engineering`, `cat:tooling`, `cat:research`, `domain:semiconductor`, `domain:chip-design` | yes (per `git ls-files`) — `docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md` | yes (per index row, status `draft`) | indexed in `docs/plans/README.md` |
| #2507 | OPEN | `priority:high`, `enhancement`, `cat:engineering`, `cat:research`, `cat:career`, `domain:semiconductor`, `domain:chip-design` | yes — umbrella plan `docs/plans/2026-04-27-issue-2507-semiconductor-cad-fem-career-lane.md` | yes (status `draft`) | yes |
| #2513 | OPEN | `priority:medium`, `enhancement`, `cat:engineering`, `cat:research`, `domain:marine` | NO | n/a | n/a |
| #2516 | OPEN | `priority:medium`, `enhancement`, `cat:engineering`, `domain:pipeline`, `domain:marine` | NO | n/a | n/a |
| #2474 | OPEN | `priority:high`, `enhancement`, `cat:engineering`, `domain:marine`, `machine:dev-primary` | yes — `docs/plans/2026-04-26-issue-2474-orcaflex-reverse-parser.md` | yes (commit `7aa5ffe05`) | one Claude r1 review at `scripts/review/results/2026-04-26-plan-2474-claude-r1.md` (MAJOR) |
| #2473 | OPEN | `priority:high`, `enhancement`, `cat:engineering`, `domain:marine`, `machine:dev-primary` | NO | n/a | n/a |
| #2472 | OPEN | `priority:high`, `enhancement`, `cat:engineering`, `domain:marine`, `machine:dev-primary` | NO | n/a | n/a |
| #2454 | OPEN | `priority:high`, `enhancement`, `cat:engineering`, `domain:marine`, `machine:dev-primary` | yes (local) — `docs/plans/2026-04-23-issue-2454-c03-fpso-semantic-proof.md` | NO — committed to local branch `nightly/2454-2457-planwave` (HEAD `13e7ecc56`) **never pushed**; not on `main` | iter-2 MAJOR; review artifacts at `scripts/review/results/2026-04-23-plan-2454-claude{,-iter-2}.md` |

Verified discrepancies vs. lane prompt's `status:plan-review` framing:
- Only **#2510** and **#2490** carry the live `status:plan-review` label. The remaining eight issues are **draft / unlabeled / pre-review**, so adversarial review is run-not-yet-binding for them.
- The lane prompt explicitly authorizes drafting for unapproved engineering issues — that path is taken below for #2509, #2473, #2472, #2516, #2513, and #2454-recovery, **without** label mutations or plan-approved markers.
- #2509 already has a plan on `main` (overnight wave-2, status `draft`); plan skeleton is therefore an enhancement note, not a from-scratch draft.

---

## 1. Adversarial review — #2510 (Python layout/CAD automation demo)

### 1.1 Round-trip review-loop verdict

The plan is queued for r14 after thirteen prior cross-review rounds. Per the **plan's own** Sustained-MAJOR Governance rule (line 367) and per repo memory `feedback_codex_sustained_major_loop`, the next wave is the **last**, not r15+. Continuing past r14 is a documented anti-pattern.

### 1.2 Cold-context findings (defect-hunting stance)

| ID | Severity | Location | Defect |
|---|---|---|---|
| **A1** | **MAJOR** | `Adversarial Review Summary` table, lines 321-326 | The r13 row is **duplicated** with internally inconsistent reasons: line 321 says Claude r13 was "0-byte Claude artifact" while line 324 says Claude r13 "stalled during r13 fanout"; lines 322 vs 325 give two different framings of Codex r13; lines 323 vs 326 give two different framings of Gemini r13. A reviewer cannot tell which entry is authoritative. State-sync drift. |
| **A2** | **MAJOR** | `GDS Round-Trip Contract`, line 190 | Per-layer count rule allows the implementer to choose between exact-equality and "documented bounded range" by re-classifying a layer as "non-rectangular/reader-fracturable". No rule fixes which layers are which, and no rule bounds how wide a "bounded range" may be. The verification gate becomes adversarially defeatable: silently widen the range, the test passes, real divergence ships. |
| **A3** | **MAJOR (governance)** | Whole plan vs. `Sustained-MAJOR Governance`, line 367 | Plan is at r13/r14 with the rule explicitly stating "If the next wave returns only review-state/tooling MAJORs and no substantive CAD/test blockers, park the issue with a GitHub blocker/minority-report summary or ask the user whether to accept the residual risk; do not keep silently grinding through unlimited prose-only reviews." r12 and r13 returned predominantly state-sync/retrieval-defect MAJORs. The rule has been violated in spirit by queueing r14. |
| A4 | MINOR | `GDS Round-Trip Contract`, line 188 | Layer-key encoding gives implementer a choice between `{"layer": <int>, "datatype": <int>}` and string `L<L>_D<D>`. The `test_metadata_extracts_...` test only requires "deterministic metadata keys" — does not pin one encoding. A round-trip across implementations could silently flip representation. |
| A5 | MINOR | `Pseudocode`, lines 220-225 | Failure path of `import_exchange_artifact` is specified ("exit non-zero, do not produce passing manifest/report") but the order of operations (`write_metadata_initial → render_report → finalize`) leaves an unwound report on disk if the round-trip fails after report rendering. Pseudocode does not call out cleanup or "before report" reordering. |
| A6 | MINOR | `Files to Change`, line 255 | Listing review artifact paths as plan-required "Files to Change" conflates planning-workflow side-effects with implementation deliverables; the implementation row should describe the demo, not the planning artifacts. |
| A7 | TRIVIAL | `Header`, line 7 | The original Apr 26 plan-file dates the early review-artifact paths, but Header line 20 says canonicals are date-dynamic via `${TODAY}`. Two different date conventions for the same artifact stream. |

### 1.3 Recommended changes for plan-approved gating

Patches required before r14 (each is a concrete edit, not another review round):

1. **Collapse the duplicated r13 rows** to a single canonical row per provider in the Adversarial Review Summary table; keep the latest (line 324-326) framing since it carries the local-verification clause.
2. **Pin per-layer round-trip semantics deterministically.** The plan must enumerate which named layers (`substrate`, `die`, `bump_array`, `route_keepout`) use exact-count equality and which use a bounded range. For any bounded range, declare a hard cap (e.g., "expected count + 5%"). No implementer-time re-classification.
3. **Pin one JSON layer-key encoding** in the plan and in the round-trip test. Recommend integer-fields-only: `{"layer": <int>, "datatype": <int>, "name": <str>, "polygon_count": <int>}`.
4. **Pseudocode reordering.** Move `import_exchange_artifact` to run **before** `render_report` so a failed round-trip blocks report generation rather than orphaning a written report.
5. **Move review-artifact paths from `Files to Change` to a separate `Planning Artifacts` table** to keep implementation scope clean.
6. **Sustained-MAJOR resolution path.** Either:
   - (a) Park the issue with a one-comment summary that lists the consensus residual risks (A1, A2 above), the patches applied since r10, and explicit "I am parking r14" — request user decision; **OR**
   - (b) Run r14 once with a clear pre-condition: if r14 returns only state-sync MAJORs (and no substantive new CAD/test defect), the plan is auto-promoted to user-approval-pending regardless. The pre-condition is recorded **in the plan itself before fanout**, not after.

### 1.4 Verdict

**MAJOR** — substantive defects A1 and A2 are real plan blockers; A3 is a process blocker that the plan acknowledges but is not following. The plan should be patched per §1.3 (especially items 1, 2, 3) **before** r14 is run, otherwise r14 will produce another state-sync-flavored MAJOR loop with no progress.

Adversarial-stance note: I deliberately did **not** treat Gemini r13's `**/*semiconductor*` "missing files" claims as substantive — they are confirmed retrieval-defect false positives per `feedback_gemini_sandbox_overlay_blindness` (`git ls-files` confirms `data/semiconductor/...`, `docs/plans/2026-04-26-issue-2508-...`, `docs/roadmaps/chip-design-cad-fem-career-roadmap.md`, etc. all exist on `main`).

---

## 2. Adversarial review — #2490 (digitalmodel coverage gate)

### 2.1 Plan posture

T1 single-line config change. Plan is fresh (commit `f14872956`, 2026-04-27), posted as #2490 plan-review comment. **No cross-review run yet.** The plan header says `Status: draft` while the GitHub label is `status:plan-review` — state desync.

### 2.2 Cold-context findings

| ID | Severity | Location | Defect |
|---|---|---|---|
| **B1** | **MAJOR** | `Adversarial Review Summary`, line 222-223 + `Header`, line 7 | Plan declares "T1 complexity; user approval gate first; adversarial review deferred." Per `.claude/skills/coordination/issue-planning-mode/SKILL.md`, **all** issues require adversarial review before `status:plan-approved`. T1 does not waive the gate. The `status:plan-review` label is already applied — that label requires review evidence to advance. Either run the cross-review or downgrade the label back to `status:plan-draft`. |
| **B2** | **MAJOR** | `Acceptance Criteria`, line 216-217 + `Risks`, line 229-235 | AC4 ("≥1 success run") is gated on `actual_coverage ≥ 80%` (Risk 1 acknowledges this). The plan does not probe the current coverage value. If real coverage is 60-80%, the fix turns `GateStatus.ERROR` into `GateStatus.WARNING`-escalated-to-`FAILURE`. Same red-build outcome, different reason. AC4 is therefore unverifiable without a pre-fix coverage probe. **Remediation:** either run `cd digitalmodel && uv run python -m pytest --cov=src --cov-report=json -q tests/ | tail -20` once during planning to capture the current coverage value, OR rephrase AC4 as "coverage gate becomes data-driven (PASS/WARN/FAIL), not ERROR" and split the green-build outcome into a follow-up issue. |
| **B3** | **MAJOR** | `Approach`, line 150 | The fix line `--cov=src --cov-report=json` may not match digitalmodel's import path. `digitalmodel/src/digitalmodel/` is the source root; pytest-cov's `--cov` argument is the **package name or path**, not always interchangeable with `src/`. `[tool.coverage.run] source = ["src"]` works at the coverage-tool layer but `--cov=src` to pytest-cov resolves against `sys.path`, which after `pip install -e .` is `digitalmodel/`, not `digitalmodel/src/`. Recommended: use `--cov=digitalmodel` (the importable package) or omit `--cov=` and rely on the pyproject `[tool.coverage.run] source` list. |
| B4 | MINOR | `Header`, line 3 vs. live label | Plan header says `Status: draft`, GH label says `status:plan-review`. State drift. Pick one. |
| B5 | MINOR | `Files to Change` | Cross-repo fact missing: digitalmodel is a **separate git submodule** per `.claude/memory/context.md`. Plan does not call out: `cd digitalmodel && git add .claude/quality-gates.yaml && git commit && git push` workflow. Implementer who copies "Files to Change" verbatim could land the change on the parent repo path and miss the submodule. |
| B6 | TRIVIAL | `Risks`, line 240 | "pytest-cov will exit with code 2 if coverage < 80%" — verify; pytest-cov exit codes vary by version (`pytest-cov<5` does not always escalate). |

### 2.3 Recommended changes for plan-approved gating

1. **Run the missing cross-review.** `scripts/review/plan-review-fanout.sh` against this plan. T1 is not exempt.
2. **Probe current coverage now.** One command: `cd digitalmodel && uv run --with pytest-cov python -m pytest --cov=digitalmodel --cov-report=term-missing -q tests/ 2>&1 | tail -5` (in dry-run / collection mode if full run is slow). Record the result in the plan.
3. **Fix the `--cov` argument.** Change `--cov=src --cov-report=json` to `--cov=digitalmodel --cov-report=json` to match the importable package. Re-verify against the digitalmodel pyproject `[tool.coverage.run]` block.
4. **Add cross-repo execution row.** "After config change, `cd digitalmodel && git checkout -b chore/coverage-gate-fix-2490 && git add .claude/quality-gates.yaml && git commit -m '...' && git push origin chore/coverage-gate-fix-2490 && gh pr create -R vamseeachanta/digitalmodel ...'". Workspace-hub does **not** carry the change.
5. **Reword AC4** to "coverage gate is data-driven; not `GateStatus.ERROR`" and move the green-build outcome to a conditional/follow-up. Don't promise green when the fix is a structural ERROR-→-FAILURE transition.

### 2.4 Verdict

**MAJOR** — B1 is a process blocker, B2 is a verification blocker (AC unverifiable as written), B3 may make the fix a no-op. Plan needs §2.3 patches and a cross-review run before approval.

---

## 3. #2474 — OrcaFlex reverse-parser plan (draft, single Claude r1 review)

### 3.1 Status

Draft committed `7aa5ffe05` (2026-04-26) by worker-1. Single Claude r1 review at `scripts/review/results/2026-04-26-plan-2474-claude-r1.md`, verdict **MAJOR** (8 findings: F1-F3 MAJOR, F4-F8 MINOR). No Codex/Gemini cross-reviews yet. Issue is **not** labeled `status:plan-review`.

### 3.2 Open r1 blockers requiring plan patches before plan-review

The r1 findings are concrete and correct — none look like sandbox/retrieval false positives. Patch list:

| ID | Patch |
|---|---|
| **F1** | Rewrite TDD pseudocode to reflect that `ModularModelGenerator(spec_file).generate(output_dir)` writes a **directory** of include files, not a single YAML payload. Either (a) walk the include chain via a new `parse_directory(master_yml)` API, or (b) re-monolith with `format_converter/modular_to_single.py` and reverse-parse the single. Pick one in the plan. |
| **F2** | Drop the schema-version pinning test, **or** explicitly scope it to native OrcaFlex exports (which are out of scope for this issue). The forward generator has no "OrcaFlexVersion" header to pin against — the test would test nothing. |
| **F3** | Add a **mandatory** real-export negative test: feed `OrcaFlexInputParser` a real OrcaFlex `single.yml` (one of the existing samples in `digitalmodel/docs/domains/orcaflex/library/`) and assert the parser produces a non-empty `unmapped_native_keys` set. Without this, the round-trip is tautological — same author writes and reads, empty diff guaranteed by closure. This is THE core defect the plan must defend against; fixture-bound proofs alone do not establish "semantic equivalence". |
| F4 | Fix Artifact Map line 88 self-reference filename (`-proof.md` → no suffix). |
| F5 | Reword "(#520)" reference as "digitalmodel issue #520 (commit `63c1cbdd`)". |
| F6 | Add taxonomy enum + `len(reason) >= 30` + CODEOWNERS gate to the ignored-fields registry. |
| F7 | Raise float `atol` from `0` to `1e-12`; add UTF-8 BOM and CRLF tests. |
| F8 | Multi-body decision: either include one multi-body fixture or explicitly defer to a follow-up issue with link. |

### 3.3 Next-step recommendation

Plan **does not** need new Claude review evidence. It needs:
1. Author patches F1-F8 inline.
2. Run `scripts/review/plan-review-fanout.sh` for a fresh r2 with **all three providers** (Claude/Codex/Gemini).
3. Only then label `status:plan-review`.
4. The dispatch policy `feedback_gemini_sandbox_overlay_blindness` (always verify Gemini false-missing claims via `git ls-files` before treating as blocker) applies.

### 3.4 Verdict (plan as committed)

**MAJOR** — three real structural blockers (F1, F2, F3) require pre-review patches. F3 in particular is the kind of round-trip-tautology defect that no amount of additional reviewers will surface again because they would all hit the same closure. Patch first, then fanout.

---

## 4. #2454 — turret-moored FPSO plan (stranded on local branch)

### 4.1 Critical state finding

The plan committed at `13e7ecc56` is on local branch `nightly/2454-2457-planwave` and has **never been pushed**. `git branch --remote` returns no `nightly/2454-2457-planwave` ref. The plan is invisible to GitHub reviewers, Codex MCP, and any operator who didn't hand-checkout that branch. The 2026-04-23 #2454 comment from worker-1 explicitly notes the push was blocked by the workspace pre-push hook (`yaml` ModuleNotFoundError in `scripts/quality/check_config_drift.py`).

This is a recovery problem, not a planning problem.

### 4.2 Recovery options

| Option | Steps | Trade-off |
|---|---|---|
| **A: Sanctioned-bypass push** | (1) Verify `.claude/skills/workspace-hub/worktree-pre-push-bypass-for-tier1-checks/SKILL.md` is the right path. (2) `git push -o "ci.skip=true" origin nightly/2454-2457-planwave` with `GIT_PRE_PUSH_SKIP=1` per the skill. (3) Open a PR, mark "draft + plan-only". | Honors the existing pre-push policy escape hatch. Requires user approval to set the env var. |
| **B: Cherry-pick to fresh branch** | (1) `git checkout main && git pull`. (2) `git cherry-pick 13e7ecc56`. (3) Push and open PR. | Avoids the original push-block; loses the iter-1/iter-2 review-artifact context if those commits are not also picked. |
| **C: Rebase + push** | (1) `git checkout nightly/2454-2457-planwave && git rebase origin/main`. (2) Investigate the `yaml` ModuleNotFoundError and fix `scripts/quality/check_config_drift.py` first. (3) Push. | Cleanest long-run option but requires fixing the pre-push hook root cause (likely `uv run` vs naked `python` invocation). |

**Recommended:** Option B (cherry-pick) for ace1 since it carries fewest unknowns; the sanctioned bypass (Option A) is what the worker originally tried and was blocked on.

### 4.3 Plan-content blockers (iter-2 MAJOR, three findings still open)

Per the worker-1 2026-04-23 comment on #2454, the iter-2 MAJOR findings are concrete:

| ID | Patch |
|---|---|
| iter-2 M1 | Replace `compare()` with `validate(mono, mod) -> list[SectionResult]`, then wrap in `ValidationResult` before `to_json()`. |
| iter-2 M2 | Rewrite three assertions to traverse `sec["diffs"]`, `sec["objects"][*]["diffs"]`, AND `sec["categories"][*]["diffs"]`. List/nested sections were missed. |
| iter-2 M3 | Replace `GroupsBuilder(spec).should_generate()` with `spec.metadata.structure == "generic"` inline check (constructor needs two positional args). |
| iter-2 plus | Normalize frozen-diff JSON (strip timestamp, absolute paths) for equality. |

These are substantive plan-content patches, not state-sync drift.

### 4.4 Verdict

**MAJOR** — recovery (push) **and** content patches both required. Recommend ace2/dev-primary takes this as a focused 2h block: cherry-pick the plan to a fresh branch + apply iter-3 patches inline + run a fresh single-author r3 review per `feedback_permission_gate_blocks_cross_review`. Do not attempt cross-review fanout until plan is pushed and visible to Codex.

---

## 5. Plan skeletons for unplanned engineering issues

### 5.1 #2509 — OpenLane/OpenROAD RTL-to-GDS demo

**Existing state:** plan exists in repo (`docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md`, status `draft`, T3) per `docs/plans/README.md` row 327. Issue body has zero comments — no `Planning started` comment posted to the issue. Plan is not yet adversarially reviewed.

**Scope refinement note (intended as issue comment, not committed):**

```
Plan exists at docs/plans/2026-04-26-issue-2509-openlane-rtl-to-gds-demo.md (draft, T3).

Verified critical state at planning time:
- Local host has ZERO EDA tools: docker, podman, openlane, openroad, yosys, iverilog, magic, netgen all MISSING (verified `which` probes during wave-2 overnight planning).
- Plan pivots to documentation-first replay design that exits 0 when tools absent, anchored on issue AC1 'replay committed sample artifacts' allowance.
- Sibling chain: #2508 closed (KB + job-skill matrix); #2511 plan-approved (establishes scripts/semiconductor/ + tests/semiconductor/ + data/semiconductor/<feature>/ layout this plan adopts).

Pre-review user-decision blockers (must resolve before fanout):
1. Defer to KB-recommended order #2508 → #2511 → #2510 → #2509 → #2512?
2. Binary `.gds`/`.def` commit policy: <2.5MB inline vs Git LFS vs external-download-with-hash?

Next step: resolve user-decisions (1) and (2), patch plan, run cross-review fanout, then label status:plan-review. Implementation blocked.
```

**Plan readiness verdict:** **PRE-REVIEW.** Two user-decisions block fanout. T3 complexity, parallel to #2510. Strongly correlated with #2510 GTM (same career-lane bundle).

### 5.2 #2473 — OrcaWave-to-OrcaFlex hydrodynamic handoff semantic proof

**Plan skeleton (draft for issue refinement comment):**

```
## Plan skeleton (draft — pre-review)

### Resource Intelligence (from #2474 inventory + handoff)
- Existing: `digitalmodel/src/digitalmodel/marine_ops/marine_analysis/parsers/orcaflex_yml_parser.py` is **RAO-scoped only** (handles VesselTypes/Draughts/DisplacementRAOs, 335 lines).
- Existing: `OrcaWaveInputParser` at `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py:387` — RAO-extraction baseline, NOT OrcaFlex-emit.
- Existing: `rao_data_to_diffraction_results()` and the RAODatabase bridge (cited in handoff).
- Closed precedents #1592, #1597, #1605, #1765, #1766, #1768 — already cover OrcaWave→OrcaFlex export pipeline plumbing. **Coordination: do not duplicate; build provenance/equivalence proof on top.**

### Deliverable
End-to-end semantic proof harness: `OrcaWave outputs → RAO/added-mass/damping → RAODatabase → OrcaFlex vessel hydrodynamic input` preserves units, headings, frequencies, phase/sign convention, body axes, damping/added-mass matrices, and source-file provenance.

### Scope boundaries
- IN: YAML-only proof. RAO frequency/heading preservation. Rotational unit convention. Phase/sign convention. Damping matrix provenance. Body-frame metadata. Source-file traceability.
- OUT: Licensed solver execution (covered by separate `licensed-machine` proof issue per handoff). Rebuilding closed #1592/#1605 pipeline.

### Equivalence criteria (preliminary)
1. Frequency vector exact equality (no resampling).
2. Heading vector exact equality (degree-encoded, not radian/wraparound drift).
3. Phase convention: agree on `e^{i\omega t}` vs `e^{-i\omega t}` and assert at the boundary.
4. Body axis: vessel `x`/`y`/`z` axes agree between source diffraction and target OrcaFlex vessel input.
5. Source-file provenance field present in every emitted RAO record.

### TDD outline
- `test_rao_extraction_preserves_frequency_grid`
- `test_rao_extraction_preserves_heading_grid`
- `test_phase_sign_convention_explicit_at_boundary`
- `test_added_mass_matrix_full_6x6_provenance`
- `test_damping_matrix_provenance_field_non_empty`
- `test_orcaflex_vessel_yaml_emit_preserves_body_axes`
- `test_provenance_round_trip_source_file_traceable`

### Risks
- **Tautology risk** (per #2474 r1 F3): if same code writes RAOs and reads them back, no real proof. Add at least one fixture from a real OrcaWave run, not synthetically generated.
- **Closed-precedent drift:** #1592/#1605 may have shipped without explicit phase/sign assertions; this proof harness is a retroactive guarantee.

### Adversarial defenses
- Multi-provider cross-review at fanout time.
- Phase/sign convention asserted at YAML boundary, not implicit in code.

### Complexity: T3
```

**Plan readiness verdict:** **NOT YET DRAFTED ON DISK.** Use this skeleton as the seed for a worker who picks up #2473.

### 5.3 #2472 — CALM/SPM buoy OrcaFlex semantic proof

**Plan skeleton (draft):**

```
## Plan skeleton (draft — pre-review)

### Resource Intelligence
- Existing: `ModularModelGenerator(spec_file).generate(output_dir)` per init.py:69 — same generator that powered PR #528 closed wave (#2455/#2456/#2457).
- Existing fixture candidate: identify a CALM/SPM-style fixture under `digitalmodel/docs/domains/orcaflex/library/model_library/`. If none, this issue's first deliverable is the **fixture itself**.
- Related #21: AQWA vs OrcaFlex SPM benchmark — out of scope unless plan-approved.

### Deliverable
A canonical `spec.yml → ProjectInputSpec → ModularModelGenerator → native OrcaFlex YAML` semantic-proof for a CALM/SPM buoy fixture (single buoy + mooring legs + tanker interaction boundary).

### Scope boundaries
- IN: object identity (buoy, legs, anchors, fairleads). Mooring/anchor/fairlead intent. LineType references. Environmental case intent. Vessel/tanker interaction boundary surface (without dynamics).
- OUT: Licensed OrcaFlex solver execution. AQWA cross-comparison. Multi-buoy/loading-buoy variants beyond a single canonical CALM topology.

### Files to change (rough)
- New fixture: `digitalmodel/docs/domains/orcaflex/library/model_library/calm_buoy/spec.yml` + `monolithic/<NAME>.yml` + `modular/...`.
- New test: `digitalmodel/tests/solvers/orcaflex/modular_generator/test_calm_buoy_semantic_proof.py`.
- Reuse `scripts/semantic_validate.py` (validate API per #2454 plan inventory).

### TDD outline
- `test_calm_buoy_modular_no_significant_diffs`
- `test_calm_buoy_mooring_leg_object_identity_preserved`
- `test_calm_buoy_lineType_references_resolve`
- `test_calm_buoy_environment_case_intent_preserved`
- `test_calm_buoy_vessel_interaction_boundary_surface_present`

### Risks
- **Fixture novelty:** if no CALM/SPM fixture exists, this plan must include fixture authoring. That doubles the surface.
- **Tautology:** same risk family as #2473 / #2474 F3; require at least one real-export-style negative.
- **Vessel/tanker scope creep:** keep boundary explicit — `vessel:` block presence + reference, not dynamics.

### Complexity: T3 (probably T2 if a fixture already exists; T3 if fixture authoring required)
```

**Plan readiness verdict:** **NOT YET DRAFTED.**

### 5.4 #2516 — Flexible pipe / dynamic riser cross-section mechanics follow-up

**Plan skeleton (draft):**

```
## Plan skeleton (draft — pre-review)

### Resource Intelligence
- Parent: #2513 (offshore wind / oil & gas cross-section catalogue) — gates this issue. Without #2513's source-backed taxonomy, the layer mechanics surface is unbounded.
- Existing knowledge: `knowledge/wikis/marine-engineering/wiki/concepts/subsea-cable-umbilical-cross-sections.md`, `comparisons/offshore-wind-oil-gas-cross-section-assessment.md`.
- Standards landscape: API 17J/17B, API 17E, DNV-ST-F101, DNV-RP-F106/F102 — flexible-pipe-specific.

### Deliverable
Bounded follow-up plan defining (a) which flexible-pipe cross-section properties belong in metadata vs. mechanics modules, (b) source-backed taxonomy of layers (carcass, liner, pressure sheath, pressure armour, tensile armour, outer sheath, anti-wear, insulation), (c) OrcaFlex flexible-riser export property requirements, (d) TDD fixtures.

### Scope boundaries
- IN: Layer taxonomy. Metadata vs. mechanics boundary. OrcaFlex export property surface. Bend-radius/collapse/torsion/fatigue annotation contract.
- OUT: Implementation of mechanics solvers. Annulus monitoring (separate concern).

### Dependency
- BLOCKING: #2513 source catalogue must reach 12+ entries with stable schema before this plan can be reviewed.

### Complexity: T3
```

**Plan readiness verdict:** **PARENT-BLOCKED** by #2513.

### 5.5 #2513 — Offshore wind / oil & gas cross-section source catalogue

**Plan skeleton (draft):**

```
## Plan skeleton (draft — pre-review)

### Resource Intelligence
- Existing seed: `knowledge/wikis/marine-engineering/wiki/concepts/subsea-cable-umbilical-cross-sections.md`, `sources/offshore-cable-umbilical-cross-section-recon-2026-04-26.md`, `comparisons/offshore-wind-oil-gas-cross-section-assessment.md`.
- Source anchors (per issue body): Floating Offshore Wind Farm Guide, Prysmian 66kV PDF, SUT Subsea Umbilical PDF, Prysmian Power/Optical Umbilicals PDF, DNV-ST-F101, Vallourec line pipe coating, Octal concrete weight coating.

### Deliverable
- YAML catalogue (e.g. `data/marine/cross-section-source-catalogue.yaml`) with provenance, asset family, layer/component taxonomy, numeric range, license/access status.
- Standards map for API 17E/17J/17B, DNV-ST-F101, DNV-RP-F106/F102, IEC/CIGRE submarine cable, offshore wind cable guidance.
- Gap list separating open vs. paywalled sources.
- Wiki page updates with higher-quality exemplar data.

### Scope boundaries
- IN: 12+ source/exemplar entries across offshore wind cable, O&G umbilical, rigid pipeline, flexible pipe/riser. Each entry: URL/local path, source type, asset family, key layers, usable numeric fields, license status.
- OUT: Quoting paywalled standard text. Implementing geometry/section-property tools (#2516 owns that).

### TDD outline
- `test_catalogue_minimum_12_entries`
- `test_catalogue_each_entry_has_provenance_url`
- `test_catalogue_no_paywalled_text_copied`
- `test_catalogue_dedup_against_wiki_concepts_page`
- `test_catalogue_yaml_schema_validates`
- `test_standards_map_complete_per_required_standards`

### Standards-derived constants
- If any layer thickness / strength / pressure rating is lifted directly from API/DNV, calc-citation contract per `.claude/rules/calc-citation-contract.md` applies.

### Complexity: T2
```

**Plan readiness verdict:** **NOT YET DRAFTED.** Knowledge-catalogue scope; lower implementation complexity than #2516.

### 5.6 #2507 — Semiconductor career lane (umbrella)

**No plan needed at the umbrella level.** Per `docs/plans/README.md` row 342, an umbrella plan exists at `docs/plans/2026-04-27-issue-2507-semiconductor-cad-fem-career-lane.md` (draft, T2) whose only deliverable is the lane-status doc + a guardrail test enforcing execution order #2508 → #2511 → #2510 → #2509 → #2512. This plan is intentionally lightweight; the real implementation work lives in the children.

---

## 6. GTM and implementation-readiness ranking

Boundary-pushing dimension = how directly does this issue convert existing strengths into a new revenue/credentialing surface? Implementation-readiness = how close is this to a button-press once approved?

| Rank | Issue | GTM weight | Readiness | Notes |
|---|---|---|---|---|
| 1 | **#2510** Python layout/CAD demo | **HIGH** — first credential artifact for semiconductor lane (#2507 umbrella). Portfolio-grade. | **MEDIUM** — plan is r13/r14 cycling; needs §1.3 patches + governance escalation, then 1-day implementation. | Most direct GTM payoff per dollar. Stop the review-loop and either park or auto-approve at r14. |
| 2 | **#2509** OpenLane RTL-to-GDS demo | **HIGH** — second credential artifact; pairs with #2510 as a layout/EDA flow. | **MEDIUM-LOW** — plan exists but two user decisions block fanout (KB order, binary commit policy). | Resolve the two decisions first. Then T3 implementation with documentation-first fallback already designed. |
| 3 | **#2474** OrcaFlex reverse-parser | **MEDIUM-HIGH** — engineering trust signal in core domain (offshore/marine). Existing customers care. | **MEDIUM** — single-author r1 MAJOR; F1-F3 patches required before fanout. | r1 F3 (round-trip tautology) is THE substantive defect; patch it first. |
| 4 | **#2473** OrcaWave→OrcaFlex hydro handoff | **MEDIUM-HIGH** — closes the most-cited gap from the 2026-04-23 handoff. | **LOW** — no plan on disk; needs first draft. | Use §5.2 skeleton as seed. T3. |
| 5 | **#2454** turret-FPSO semantic proof | **MEDIUM** — flagship generic-track readiness flag. | **LOW** — plan stranded on local branch; iter-2 MAJOR with three real defects. | §4.2 Option B (cherry-pick) is recovery path. Then iter-3 content patches per §4.3. |
| 6 | **#2472** CALM/SPM buoy proof | **MEDIUM** — fills another fixture-family gap. | **LOW** — no plan; may require fixture authoring. | T3. Use §5.3 skeleton. |
| 7 | **#2490** digitalmodel coverage gate | **LOW (direct)**, **MEDIUM (indirect)** — unblocks `Quality Gates` workflow which feeds engineering credibility. | **HIGH** — T1 single-line config change. Once §2.3 patches applied + cross-review run, ready for approval. | Be honest about the green-build outcome (B2). Don't promise what `--cov-report=json` alone won't deliver. |
| 8 | **#2516** flexible-pipe mechanics | **LOW-MEDIUM** — niche but high-margin. | **BLOCKED** by #2513. | Sequential dependency. |
| 9 | **#2513** cross-section source catalogue | **LOW (direct)** — unblocks #2516. | **LOW** — no plan; T2 catalogue work. | Use §5.5 skeleton. |
| 10 | **#2507** semiconductor career-lane umbrella | **HIGH (indirect)** — orchestrates all semiconductor work. | **N/A** — umbrella; status doc only. | Don't try to "implement"; track child completions. |

### 6.1 12h continuation lane recommendation (action plan, no mutations)

For an unattended worker ranking by ROI:
1. **Hour 1-3:** patch #2510 plan per §1.3 items 1-5 (collapse duplicate r13 rows, pin layer encoding, fix pseudocode order, move review artifacts out of Files-to-Change). Critical: do not run r14 before patches land. Then either escalate (sustained-MAJOR park) or run r14 once with the auto-promote pre-condition recorded.
2. **Hour 3-5:** patch #2474 plan per §3.2 F1-F3, then fanout cross-review.
3. **Hour 5-6:** patch #2490 plan per §2.3, run probe + cross-review.
4. **Hour 6-9:** draft #2473 plan from §5.2 skeleton + #2472 plan from §5.3 skeleton (parallel-safe — different fixture surfaces).
5. **Hour 9-11:** #2454 recovery — Option B cherry-pick + iter-3 content patches per §4.3.
6. **Hour 11-12:** roll-up commit-pack + write summary status comments (do not post; write as command pack).

**No GitHub mutations.** Every recommendation is in this file or in the `plan-review-command-pack.md`.

---

## 7. Cross-cutting observations (engineering evidence boundaries)

Three patterns across all plans worth surfacing for ace1 control surface:

1. **Round-trip-tautology pattern (#2474 F3, #2473, #2472):** every "semantic proof" plan in this batch is at risk of writing the spec, reading it back, and calling the empty diff "proof". The mitigation pattern (real-export negative test) should become a **template policy** for any future canonical-spec proof issue.
2. **Sustained-MAJOR loop pattern (#2510):** the documented governance rule (`feedback_codex_sustained_major_loop`, plan §367) is being violated in spirit. The lane prompt is right to flag plan-review issues for hardening; the harder problem is enforcing the rule programmatically (e.g., a hook that fires on r4+ with majority-state-sync MAJORs and suggests park).
3. **Cross-repo silence (#2490 B5):** plans modifying digitalmodel rarely call out the submodule push workflow. This is implicit knowledge per `.claude/memory/context.md` but not enforced in plan templates. A `Cross-repo execution contract` row in the plan template would catch this.

---

## 8. Files written by this lane

| Path | Owner | Mutation? |
|---|---|---|
| `/mnt/local-analysis/workspace-hub/docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/ace1-plan-review-hardener.md` | this lane | new file (write-only) |
| `docs/plans/overnight-prompts/2026-04-28-12h-continuation/results/plan-review-command-pack.md` | this lane | new file (write-only) |

No other writes. No commits. No GitHub mutations. No label changes.

---

## 9. Lane self-attestation

- Live issue state re-checked at 2026-04-28 22:00 CDT via `gh issue view`.
- Gemini r13 false-missing claims explicitly cross-checked against `git ls-files` per `feedback_gemini_sandbox_overlay_blindness`; classified retrieval defect, not blocker.
- Sustained-MAJOR rule violation flagged for #2510 per `feedback_codex_sustained_major_loop`.
- No code changes proposed for any issue lacking `status:plan-approved` per lane prompt rule 1.
- Worktree status: `git status -uno` clean except pre-existing `.claude/state/*` and `config/ai-tools/*` and `logs/orchestrator/*` untracked/modified files; this lane added two new untracked files in the explicitly authorized results directory.
- No force pushes, no resets, no destructive cleanup.
- Provenance: every concrete blocker cites a file path + line number or a verifiable artifact path.

End of ace1 result file.
