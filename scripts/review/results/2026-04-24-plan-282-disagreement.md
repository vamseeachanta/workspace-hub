# Disagreement report — plan #282 (2026-04-24)

## Verdicts

| Provider | Verdict |
|---|---|
| adversarial | The plan is well-researched, evidence-grounded, and honestly flags open questions. However it suffers from **six MINOR defects** centered on (1) unresolved tradeoff decisions left as `[TRADEOFF FOR USER]` rather than a recommended default the planner commits to, (2) an acceptance-criteria omission against the issue body, (3) one TDD gap, (4) an ambiguous alias-map decision, and (5) a scope-boundary risk with the benchmark plotter modules. Nothing rises to MAJOR: no self-labeling, no past-tense drift, no hallucinated paths, no scope-drift into #279. The plan is approvable once the tradeoffs collapse to single choices and the acceptance criteria are reconciled with the issue body. |
| claude | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=2: error: unexpected argument '--no-interactive' found    tip: to pass '--no-interactive' as a value, use '-- --no-interactive'  Usage: codex exec [OPTIONS] [PROMPT]        codex exec [OPTIONS] <COMMAND>) |
| gemini | UNAVAILABLE (gemini CLI failed, rc=55: [31mGemini CLI is not running in a trusted directory. To proceed, either use `--skip-trust`, set the `GEMINI_CLI_TRUST_WORKSPACE=true` environment variable, or trust this directory in interactive mod) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### adversarial

(no findings unique to this provider)

### claude

- **Process gate bypassed — issue labeled `status:plan-approved` before any cross-review produced signal.** `gh issue view 282` shows label `status:plan-approved`, yet `scripts/review/results/2026-04-24-plan-282-claude.md` is 0 bytes with a `.err` sibling, codex review returned `UNAVAILABLE (rc=2)`, gemini returned `UNAVAILABLE (rc=55)`. Plan body line 248-252 still shows `_pending_` for all three providers. Per CLAUDE.md planning workflow ("Adversarial Review → `status:plan-review` → USER APPROVES → `status:plan-approved`"), this label cannot be set before reviews complete. Matches memory anti-pattern `feedback_never_offer_to_self_label_plan_approved.md`. **Block implementation until reviews re-run with non-empty signal or the label is reverted + user re-approves.**
- **Pseudocode invokes fictional `hull_library.catalog` API.** Plan line 157-159 calls `hull_library.catalog.get_profile(hull_profile_id)` and `hull_library.catalog.find_by_hull_type(report_data.hull_type)`. Actual `catalog.py` (14352 bytes) exposes `list_hulls`, `get_hull(hull_id)`, `register_hull`, `generate_mesh`, `compute_motions`, `compute_accelerations` — **neither `get_profile` nor `find_by_hull_type` exists**. The entire adapter contract is designed against an imaginary API. Either specify that WRK-115 must first add these methods (and cite the WRK-115 plan), or rewrite the adapter against the real surface.
- **Gap #5 is factually wrong — peak-period annotation already renders.** Plan line 46 and Risk bullet claim "Roll-damping peak-period annotation not verified... peak-period marker presence not confirmed by intel." Grep of `report_builders_responses.py` shows lines 145-183 already render `"Peak Roll RAO: T={rd.peak_roll_rao_period:.2f}s"` using `rd.peak_roll_rao_period`. TDD test `test_roll_damping_peak_period_annotation` (line 223) would therefore test existing behavior, not a gap. Remove from gap list or reclassify as regression-guard test.
- **"Gap proof" grep citation on line 76 is false.** Plan states `grep -l "from digitalmodel.hydrodynamics.hull_library" digitalmodel/src/digitalmodel/hydrodynamics/diffraction/` returns "no matches". Live grep returns matches in `parametric_spec_generator.py` (4 imports: mesh_generator, mesh_scaler, profile_schema, parametric_hull) and `orcawave_to_orcaflex.py` (rao_extractor). The narrower "catalog specifically is not imported by diffraction" is true, but the literal citation is fabricated evidence. Fix the grep pattern (`hull_library.catalog`) or the conclusion.
- **Tanker-alias resolution is broken inside `_get_hull_type_note`.** Plan proposes `tanker` → `ship` alias for dispatch (line 118) and "HULL_TYPE_NOTES keys unchanged" (acceptance criterion line 238). But `report_builders_header.py:94` — `if not hull_type or hull_type not in HULL_TYPE_NOTES` — does NOT route through `resolve_hull_type`. If dispatch hands the builder canonical `"ship"`, the builder returns empty notes (no `ship` key). Plan must either: (a) insert alias resolution INSIDE `_get_hull_type_note`, or (b) pass the original pre-resolved name to the builder while using canonical only for strategy selection. Neither is specified.
- **Acceptance criterion 5 creates dead-code ship.** Line 234: "Hull library adapter is no-op when `hull_profile_id` is None (unblocks dispatch independent of WRK-115)." Combined with Finding #2 (API doesn't exist), the non-no-op path cannot be exercised at all. No acceptance criterion requires end-to-end validation with a real profile. Plan ships untested dead code and defers contract work to "later WRK-115 lights up the path" (line 286) — but WRK-115 is not cited by issue number or plan path.
- **Two of six hull strategies lack dispatch tests.** Line 206-224 lists dispatch tests for `barge`, `spar`, `lngc`, and alias `tanker`. No dispatch tests for `fpso` or `semi_sub`, despite both being in the canonical set (line 116). `test_registry_has_all_six` checks registry presence only, not behavior.
- **Four of six strategies lack fixture-based example output.** Acceptance criterion line 235 requires only barge (L02) + ship (L03) example reports. `L04_spar_benchmark` fixture exists (confirmed in `digitalmodel/docs/domains/orcawave/`) and is not leveraged. FPSO, semi_sub, LNGC have no fixture referenced. Four of six strategies merge with pseudo-code-only validation.
- **Three design-critical open questions flagged "Default choice absent user input."** Lines 290-294:
- (a) Whether `ship` replaces `tanker` in `HULL_TYPE_NOTES` or coexists as alias.
- (b) Single vs 5-file suite HTML output.
- (c) Lookup key `hull_type` vs `hull_profile_id`.
-    Plan assumes defaults silently. But issue is already `status:plan-approved`, meaning implementation would proceed against unresolved design decisions. Either decisions must be made explicit before implementation, or approval must be revoked.
- **Plan self-state and issue-state disagree.** Plan header line 3 says `Status: draft`. Plan body line 248-252 lists reviewer verdicts as `_pending_`. Issue label is `status:plan-approved`. "Status: draft" + "plan-approved" is incoherent; matches memory `feedback_plan_past_tense_artifact_claims.md` (plan describing unachieved state as achieved) and `feedback_attestation_enables_contradiction_detection.md` (plan-vs-live-state drift).
- **Complexity rating T3 likely too low.** "Deliverable" line 108 and "Complexity" line 300 describe: 9 new files + `hull_library_adapter.py` + 4 test modules + strategy pattern with Protocol + taxonomy aliasing + two builder modifications + ship-level HTML verification across 6 hull types. Even granting "heavy lifting exists," the integration surface (strategy ↔ builder signatures, alias propagation into `_get_hull_type_note`, Pydantic schema extension via `catalog_metadata`) is T4-adjacent. Justify T3 by cutting scope (e.g., ship only `barge` + `ship` dispatch with a stub registry; defer spar/fpso/semi_sub/lngc) or upgrade to T4.
- **Codex CLI failure is a known batch-wide regression, not plan-specific.** Codex review output cites `unexpected argument '--no-interactive'` — matches memory `feedback_codex_cli_0_124_upstream_regression.md` (installed 2026-04-23, blocks all `codex exec` on 90-byte plans, #2479). The plan's single-author fallback policy (`feedback_permission_gate_blocks_cross_review.md`) is not documented in this plan. If this plan proceeds under that policy, the plan must cite it explicitly and the `Adversarial Review Summary` must reflect the downgrade — not show all providers as `_pending_`.

### codex

(no findings unique to this provider)

### gemini

(no findings unique to this provider)

