# Adversarial Plan Review — #2564 (Claude, 2026-04-30)

> **Plan:** `docs/plans/2026-04-30-issue-2564-yaw-moment-sweep-input.md`
> **Reviewer:** Claude (Opus 4.7, autonomous provider lane)
> **Dispatch:** `provider-autofeed-20260430T094906Z`
> **Last plan commit on disk:** `3230ff4e8 plan: add yaw moment sweep issue plan` + uncommitted 145-line diff
> **Issue state:** OPEN, labels include `status:plan-review`; 4 comments (plan link, mnt/ace ref review, wiki promotion, nightly hardening)
> **Stance:** adversarial — defect-hunting, not charitable reading

---

## Verdict

**MINOR.** No content-level blocking defects after retrieval; the prior MAJOR findings from Claude/Codex/Gemini (2026-04-29) are substantively addressed by the revision. **Not approved.** Approval is gated on the user explicitly setting `status:plan-approved` per Acceptance Criterion #5; this lane never self-approves and never moves labels. Implementation must remain blocked until (a) the plan is committed/pushed so remote reviewers can retrieve it (recurrence guard) and (b) the user-in-loop gate fires.

---

## Retrieval

Files verified to exist and to back the plan's claims (parallel `ls -e` + targeted reads):

| Citation in plan | Verified? | Note |
|---|---|---|
| `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py:41` `rudder_normal_force(velocity_m_s, rho_kg_m3, rudder_area_m2, rudder_span_m, rudder_angle_deg, behind_hull=True)` | YES | Signature exact; scalar = `0.5·ρ·v²·A·C_N` with `C_N ∝ sin(δ_rad)` (line 38). Plan's keyword-call mandate is well-grounded. |
| `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` does **not** export `rudder_normal_force` / `rudder_lift_coefficient` | YES | Confirmed — `__all__` lists 28 symbols, neither rudder helper appears. Deep-import is required as planned. |
| `digitalmodel/pyproject.toml:212-215` setuptools discovery `where = ["src"]` | YES | Confirms YAML must live inside `src/digitalmodel/...` for `importlib.resources` to resolve. Plan's relocation to `src/digitalmodel/naval_architecture/data/` is correct. |
| `digitalmodel/pyproject.toml:255` `filterwarnings = ["error", ...]` | PARTIAL | Block exists, but lines 256-258 also `ignore::UserWarning`, `ignore::DeprecationWarning`, `ignore::PendingDeprecationWarning`. See Findings #2. |
| `docs/standards/calc-output-citation.md` 5 required fields (`code_id`, `publisher`, `revision`, `section`, `wiki_path`), fail-closed | YES | Schema and behavior match plan's claim that strict `Citation` is *not* triggered by literature-derived rudder mechanics. Provenance-sidecar split is contract-correct. |
| `digitalmodel/src/digitalmodel/citations/schema.py` pilot reference | YES | Exists; cited as analog rather than imported here, which is appropriate. |
| `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` Citation pilot | YES | Exists; supports plan's framing of citation contract as scoped, not universal. |
| Wiki concepts (`yaw-moment-rudder-sweep.md`, `rudder-force-modeling.md`, `maneuvering-coordinate-conventions.md`, `maneuvering-validation-metrics.md`, `environmental-yaw-moment-coefficients.md`) and comparison artifact | YES | All 6 files exist under `knowledge/wikis/naval-architecture/wiki/`. |
| `docs/plans/2026-04-30-issue-2564-mnt-ace-raw-reference-review.md` | YES | Companion `/mnt/ace` review present. |
| `data/document-index/{index.jsonl,standards-transfer-ledger.yaml,online-resource-registry.yaml,research-literature-report.md}` and `data/design-codes/code-registry.yaml` | YES | All present; plan's "no class-rule code identified" is consistent with the registry surface. |
| Latest review artifacts `scripts/review/results/2026-04-29-plan-2564-{claude,codex,gemini,disagreement}.md` | YES | All four files exist (claude/codex/gemini were 0-byte at the *prior* round per disagreement.md; current round artifacts at `2026-04-30-plan-2564-*` also present in working tree but un-tracked / un-committed). |
| `docs/plans/README.md` row 205 — `2564 | yaw-moment-sweep-input | … | 2026-04-30 | plan-review | T2` | YES | Index row matches plan and current label. |

Numeric/falsifiability spot-checks (mini Python repro of the rudder helper):

| Plan claim | Probe | Result |
|---|---|---|
| `F(+10°, behind=False) > 0` (precondition) | `0.5·1025·25·20·C_N` with δ=+10° | `97 417.4 N > 0` ✓ (but tautological — see Findings #1) |
| `F(+10°) = -F(-10°)` (symmetry) | `±97 417.4`, sum = 0 | ✓ |
| `F(10 m/s) / F(5 m/s) = 4` (speed²) | exact 4.0000 | ✓ |
| `F(0°) = 0` | exact 0.0 | ✓ |
| `M_z = x·F = -45·97 417 ≈ -4.38 MN·m < 0` | matches plan's required test | ✓ |

Issue #2564 governance: comment #1 ("Plan created and moved to `status:plan-review`") + 3 substantive update comments dated 2026-04-30 02:33–04:07 UTC; no `status:plan-approved` marker present locally or on issue. ✓ Gate intact.

---

## Findings

These are **non-blocking** but warrant note before user approval. None individually escalate to MAJOR after the 2026-04-29 patches landed; collectively they remain housekeeping.

1. **Sign-convention precondition probe is mathematically tautological** (carry-over from 2026-04-29 Claude MINOR, partially addressed). The probe `assert rudder_normal_force(..., +10°, behind_hull=False) > 0` cannot fail given the existing formula `F = 0.5·ρ·v²·A·(6.13·AR_eff/(AR_eff+2.25))·sin(δ)` — every factor is positive for δ ∈ (0°, 90°). The probe verifies *positivity of the scalar*, not the `+Y → port` direction the plan stipulates in §Sign Convention Contract. The `+Y` interpretation is a contract, not an empirically discovered property of the existing helper. Acceptable as a documented stipulation, but the precondition adds no real check; consider adding a doc note that the probe is a smoke-test, not a direction verifier, or replace with an assertion against an independently computed reference.

2. **`DeprecationWarning` is actually ignored in `pyproject.toml`, plan over-states the risk.** §Risks bullet "warnings/path code must avoid deprecated APIs" treats DeprecationWarning as fatal, but lines 256-258 of `digitalmodel/pyproject.toml` explicitly `ignore::DeprecationWarning` and `ignore::PendingDeprecationWarning` (and `UserWarning`). Only *other* warning categories (e.g., `RuntimeWarning`, `FutureWarning`) hit the error gate. Direction is safe (over-cautious), but the §Risks language should be tightened to name the categories that actually trip the gate, otherwise it's misdirecting future implementers.

3. **`test_write_chart_files_png_or_html` only checks file non-emptiness, not content.** Acceptable for a first-pass deliverable, but listing it as a chart-contract test is generous. A weak follow-up (out of scope for this plan) would parse the PNG dimensions or assert HTML contains expected series labels. Note this in the test docstring as a deliberate scope cap rather than letting reviewers infer stronger guarantees.

4. **Provenance JSON `force_source_module` hard-codes the Python dotted path** `digitalmodel.naval_architecture.maneuverability.rudder_normal_force`. If the helper is later re-homed (e.g., during the #1849 epic or any rudder-extraction refactor), this string silently drifts and points at a stale module. Consider deriving it via `f"{rudder_normal_force.__module__}.{rudder_normal_force.__name__}"` in the writer so it tracks the actual import.

5. **Lever-arm validation does not address `x_rudder_from_cg_m == 0`.** §Pseudocode says "validate lever arm finite" — a rudder coincident with CG is finite, passes validation, and yields `M_z = 0` for all inputs. Probably never the user's intent. Either reject `x == 0` as a configuration error or document that "rudder at CG ⇒ zero yaw moment" is intentional and tested. Edge case, not a blocker.

6. **Operational gap (procedural, not content):** the plan file shows 145 uncommitted lines on top of `3230ff4e8`. If a fresh cross-AI dispatch fires in this state, remote providers will hit the same 404 / stale-content failure that produced the 2026-04-29 Codex empty artifact (per `feedback_codex_needs_pushed_artifact.md` and the disagreement report). **Closing the push gap is a precondition for the next round of cross-AI review to be load-bearing.** This is not a plan-content defect, but I am surfacing it so the next dispatcher does not repeat the recurrence loop.

---

## Blockers

**None (content).** All three 2026-04-29 MAJOR findings are substantively resolved:

- **Claude MAJOR-1** (multi-provider evidence claim with 0-byte artifacts): plan revision removes the unsupported "5-theme MAJOR for Codex" claim and §Adversarial Review Summary now lists per-provider verdicts that match the populated `disagreement.md` text. ✓
- **Claude MAJOR-2 / Gemini MAJOR-1** (YAML outside src tree, `importlib.resources` cannot reach `digitalmodel/config/...`): YAML relocated to `digitalmodel/src/digitalmodel/naval_architecture/data/yaw_moment_typical_ship.yml` with package-data update mandated; both `test_load_packaged_typical_ship_yaml_with_importlib_resources` and `test_load_user_yaml_from_explicit_path` enumerated. ✓
- **Codex MAJOR-1** (plan not retrievable from canonical repo): the *content* fix is present; the *operational* push must be performed before re-dispatch. See Findings #6.
- **Codex MAJOR-2** (issue governance not updated): Issue #2564 carries `status:plan-review` and 4 plan-related comments. ✓
- **Codex MAJOR-3** (citation contract violation): plan now correctly distinguishes strict standards `Citation` (not triggered) from non-strict provenance metadata sidecar; no fabricated `code_id` for Whicker & Fehlner. ✓
- **Codex MAJOR-4** (acceptance criterion weakened MAJOR gate): revised criterion #3 now requires "no MAJOR findings from at least two substantive reviewers" with a workaround/retry rule for tooling failures rather than the prior "addressed inline with evidence" loophole. ✓
- **Gemini MAJOR-3** (positional-arg call to existing helper): §Pseudocode and §Files-to-Change both mandate keyword-argument call; `test_yaw_moment_uses_keyword_call_to_rudder_normal_force` enumerated to enforce. ✓

**Procedural blocker for next cross-AI dispatch round (not for plan content):** commit + push the 145-line diff so remote providers can retrieve the revised plan. This lane is dispatched as Claude review only and will not push.

---

## Next Action

**Recommended (for the orchestrator, not this lane):**

1. Commit the dirty plan + index update on `main` (or worktree branch) and push, so the 2026-04-30 cross-AI re-review can resolve canonical content.
2. Allow the in-flight `2026-04-30-plan-2564-{codex,gemini,disagreement}.md` reviews (already on disk under `scripts/review/results/`) to land; if they return any MAJOR, treat as superseding.
3. Hold the `status:plan-approved` label until: (a) all three providers' 2026-04-30 verdicts are present and none is MAJOR, AND (b) the user explicitly approves on issue #2564.
4. Findings #1–#5 above are not blocking for approval; address them as MINOR amendments within implementation phase or tracked follow-ups.

This review **does not approve** the plan and **does not change labels**.
