# Overnight OrcaFlex/OrcaWave Planning Batch — Morning Report

> **Run date:** 2026-04-24 (session: pts/3, PID 1807944)
> **Batch design:** `docs/plans/2026-04-24-orcaflex-orcawave-overnight-batch-design.md`
> **Batch commit:** `035579032` — ⚠️ **NOT YET PUSHED** to origin (see "Pending Push" below)
> **Repo targeted:** `vamseeachanta/digitalmodel`
> **Artifacts produced this run:** 10 plans + 10 adversarial reviews + 1 batch-design amendment + this report + 10 intel files in `/tmp/` (local-only)

## Top-Line Verdict Table

| Issue | Title | Plan | Review | Complexity | Verdict | Defects | Recommended triage |
|---|---|---|---|---|---|---|---|
| #515 | YAML semantic-equivalence (parent) | `docs/plans/2026-04-24-issue-515-semantic-equivalence-yaml-strict.md` | `scripts/review/results/2026-04-24-plan-515-adversarial.md` | T2 | **MINOR** | 10 | Revise (hallucinated counts + type) → approve |
| #282 | OrcaWave reporting standardization | `docs/plans/2026-04-24-issue-282-orcawave-reporting-standardization.md` | `scripts/review/results/2026-04-24-plan-282-adversarial.md` | T3 | **MINOR** | 6 | Revise (strategy/pseudocode mismatch, cylinder/sphere regression) |
| #279 | OrcaFlex reporting standardization | `docs/plans/2026-04-24-issue-279-orcaflex-reporting-standardization.md` | `scripts/review/results/2026-04-24-plan-279-adversarial.md` | T2 | **MAJOR** | 3+5 | **Re-plan** — fabricated test + missed mandate + missed deliverable |
| #510 | Fix 20 pre-existing test failures | `docs/plans/2026-04-24-issue-510-fix-20-test-failures.md` | `scripts/review/results/2026-04-24-plan-510-adversarial.md` | T1 | **MINOR** | 6 | Revise (missing `shapes_builder` ramp coverage) → approve |
| #500 | OrcaWave mesh preflight + auto-copy | `docs/plans/2026-04-24-issue-500-orcawave-mesh-preflight-auto-copy.md` | `scripts/review/results/2026-04-24-plan-500-adversarial.md` | T2 | **MINOR** | 11 | Revise (suffix-policy desync hazard) |
| #501 | OrcaWave QTF/fieldpoints/irreg-freq | `docs/plans/2026-04-24-issue-501-orcawave-qtf-fieldpoints-irregfreq.md` | `scripts/review/results/2026-04-24-plan-501-adversarial.md` | T2 | **MAJOR** | 10 | **Re-plan** — silent user-override drop; breaks L03 byte-identity gate |
| #504 | OrcaFlex buoys builder refactor | `docs/plans/2026-04-24-issue-504-orcaflex-buoys-builder-refactor.md` | `scripts/review/results/2026-04-24-plan-504-adversarial.md` | T2 | **MINOR** | 7 | Revise (`all_buoy_names` aggregation contract + pseudocode contradiction) |
| #503 | OrcaFlex/OrcaWave help ingestion | `docs/plans/2026-04-24-issue-503-orcaflex-orcawave-help-ingestion.md` | `scripts/review/results/2026-04-24-plan-503-adversarial.md` | T3 | **MINOR** | 10 | Revise (promote Q3/#2034 to pre-implementation gate) |
| #511 | OrcaFlex campaign spec generation | `docs/plans/2026-04-24-issue-511-orcaflex-campaign-spec-generation.md` | `scripts/review/results/2026-04-24-plan-511-adversarial.md` | T2 | **MINOR** | 10 | Revise (signature scoping + Pydantic setter coverage) |
| #486 | Subsea connectors/jumpers (API 17R) | `docs/plans/2026-04-24-issue-486-subsea-connectors-jumpers-api17r.md` | `scripts/review/results/2026-04-24-plan-486-adversarial.md` | T3 | **MINOR** | 10 | **User decision first:** Path A (procure 17R) or Path B (ledgered adjacents). All hard gates PASS. |

**Verdict distribution:** 2 MAJOR (#279, #501), 8 MINOR, 0 APPROVE.
**Total defects across all 10 reviews:** ~87 (avg 8.7 per plan).

## Recommended Review Order

Suggested ordering for your morning triage (not a prescription — no plans are self-approved):

1. **Quick wins (T1/T2, MINOR, no user decision needed):** #510, #515 → these can be revised in minutes and sent for approval
2. **User-decision first (blocked on your choice, not on plan quality):** #486 (standard path), #503 (licensing gate + consolidation approach)
3. **MAJOR needing re-plan:** #279 (fabricated test is cheap to fix; mandate/deliverable gaps need deeper rewrite), #501 (conditional-logic gap needs pseudocode rewrite)
4. **MINOR with tradeoff defaults already picked:** #282, #500, #504, #511 (review the picked defaults, overrule if needed)

## Cross-Issue Dependency Notes

- **#500 ↔ #501:** both touch OrcaWave config surface. #500 is runner-layer; #501 is config-schema. If both are approved, ensure #501's `bool→enum` landing precedes #500's validate() tightening to avoid a test-drift window.
- **#279 ↔ #282:** both implement per-structure-type reporting. They share no files but should align on template-dispatch mechanism (#282 recommends Strategy pattern; #279 doesn't explicitly commit to one). Morning triage should confirm consistency.
- **#503 ↔ #2124/#2125 (foreign sessions):** a parallel session wrote plans for `#2124 Orcina resources examples training` and `#2125 Orcina auto-refresh` during our Wave 1 window. These thematically overlap #503's help-ingestion scope. **Action needed:** decide whether #503 absorbs or coordinates with those plans before any implementation begins.

## Deferred-Cluster Readiness

**#515 (parent) plan is MINOR-verdict, ready for revision → approval.** Once #515 lands an approved approach (broad ratify-existing-taxonomy vs. narrow meta-contract), the deferred cluster (#517, #518, #519) becomes plannable in a follow-up batch. The decision path affects each:

- If **Path A (broad):** #515 absorbs most of #517's taxonomy work; #518/#519 become smaller. Next batch may need only 2 pods.
- If **Path B (narrow):** #517/#518/#519 stay full-size as originally scoped. Next batch = 3 pods + possibly a fourth for a shared test scaffold.

## Design-Spec Corrections (from Wave 1 findings)

My batch-design spec (committed earlier) mislabeled multiple issues as greenfield. Wave 1 explorers surfaced **8 of 10 "already partially exists" findings**, which the Wave 2 Planners reframed into DELTA-style plans. Corrections:

| Issue | Design-spec label | Reality (per explorer intel) |
|---|---|---|
| #511 | "Greenfield generator" | `CampaignSpec`/`Matrix`/`Generator` already exist; this is an extension |
| #279 | "New reporting framework" | 2823 LOC of reporting infrastructure already in `solvers/orcaflex/reporting/`; 5/6 renderers exist; vessel renderer is the gap |
| #504 | "Split mega-builder" | True, BUT `BuilderRegistry._registry` has key-collision hazard not mentioned in issue body |
| #500 | "Add validation to runner" | `_copy_mesh_files` + `_validate_mesh_references` already exist in `orcawave_runner.py:460-549`; gap is tightening, not adding |
| #501 | "Expand three features" | `control_surface` already 90% plumbed — only `bool → enum` missing for selectability |
| #282 | "Build per-hull reports" | `HULL_TYPE_NOTES` already keys 8 hull types; gap is template-dispatch layer |
| #515 | "Close semantic-equivalence gaps" | `SEMANTIC_DIFF_TAXONOMY.md` already drafted (413 lines, labeled "#517 work") |
| #503 | "Ingest help" | TWO existing ingestion scripts already compete; plan must consolidate, not add a third |

Only **#510 and #486** were correctly scoped in the batch-design spec (#510 = test drift; #486 = genuinely greenfield + ledger-gap blocker).

**Process recommendation for future batches:** add a pre-dispatch "grep for existing implementation" pass to catch these framings before agent dispatch.

## Adversarial-Review Summary by Defect Category

Aggregated across all 10 reviews (n=87 defects):

- **Hallucinated evidence:** 3 plans hallucinated specific facts (#279 fabricated test; #515 wrong _SKIP_GENERAL_KEYS count of 34 vs. actual 22; #515 wrong type of Significance as Enum). Pattern: plans cite specific numbers/types inferred from context; evidence contract (`#2208`) catches these when reviewers grep.
- **Plan-internal contradictions:** 2 plans had pseudocode disagreeing with their own artifact lists (#282 dict-of-callables vs. Strategy pattern; #511 `_apply_overrides` signature missing `matrix.sweeps`). Wave-2 prompt improvement: require Planner self-check of pseudocode-to-signature consistency.
- **Silent-regression / silent-corruption hazards:** 3 plans introduced changes that silently break existing behavior (#282 would drop cylinder/sphere hull types; #500 suffix-policy desyncs `BodyMeshFileName`; #501 silently drops user QTF overrides under non-QTF solve_type).
- **Missing TDD coverage:** 2 plans had acceptance criteria without corresponding tests (#279 missing golden HTML examples; #504 missing `all_buoy_names` aggregation test).
- **Unfalsifiable ACs:** 1 plan (#486) has "validates against schema" with schema undefined; and literal "§" placeholders for standard clauses (path-B).
- **Scope drift:** 0 — no reviewer found out-of-scope changes. Scope discipline was strong.
- **Self-labeling:** 0 — no plan claimed `status:plan-approved` (the one hit in #504 was the template's legitimate status-sequence enumeration).
- **Past-tense drift:** 0 — no plans described proposed work as already-done.

## Failed Lanes

**Wave 1 (Explorers):** 2 stall failures on the "standardize analysis reporting" pair.
- **#279 first attempt** — stalled 600s with 0 bytes written. **Root cause:** 81KB issue body triggered an expensive open-ended recon that hung the stream watchdog.
- **#282 first attempt** — stalled 600s at "I'll investigate..." with 0 bytes. **Root cause:** unclear; possibly expensive repo-wide grep that hit timeout.

**Both retried successfully** with a **skeleton-first + pre-extracted-body + bounded-grep** protocol (write a TBD-skeleton in first 5 turns, then fill in). **Protocol validated 2-for-2.**

**Wave 2 (Planners):** 0 failures. All 10 completed within 2-5 min each.

**Wave 3 (Reviewers):** 0 failures. All 10 completed within 1.5-4 min each.

## Infrastructure Observations

### Pending Push — USER DECISION NEEDED

Commit `035579032` contains all batch artifacts but is **NOT pushed to origin**. Per CLAUDE.md global guidelines, I do not push without explicit user authorization.

**To push:**
```bash
cd /mnt/local-analysis/workspace-hub
git push origin main
```

**Not pushing is OK too** — issue comments reference paths (not blob URLs), and those will work after you push.

### 3-Provider Fanout Outcome — Partial Failure, Tooling Maintenance Required

After the user pushed `main` to origin (per Codex-needs-pushed-artifact constraint), the 3-provider fanout (`scripts/review/plan-review-fanout.sh`) was dispatched for all 10 plans. Outcome:

| Provider | Result | Root cause |
|---|---|---|
| **Claude** 2nd pass | 6/10 full reviews (all **MAJOR**), 3 partial, 1 zero-byte (#510) | Expected; one turn budget ran thin |
| **Codex** | 10/10 failed with canonical "UNAVAILABLE" stub | Fanout script uses `codex exec --no-interactive`; current Codex CLI rejects that flag (`error: unexpected argument '--no-interactive' found`) |
| **Gemini** | 10/10 failed with canonical "UNAVAILABLE" stub | Gemini CLI refuses to run in untrusted workspace; needs `GEMINI_CLI_TRUST_WORKSPACE=true` or `--skip-trust` — neither is set in the fanout script |

All 30 files (real + stubs) committed as `7f54958a3` for provenance. The stubs are the fanout script's documented-failure template, not hallucinated content.

**Claude second-pass signal** is interesting: **#515, #282, #500, #504, #486** all received **MAJOR** on second read despite Wave 3 rating them MINOR. Interpretation: the plans have more latent defects than Wave 3 surfaced; morning triage should treat these five as candidates for MAJOR-tier revision alongside the original MAJORs (#279, #501). The Claude 2nd-pass review files at `scripts/review/results/2026-04-24-plan-{N}-claude.md` enumerate specific defects.

**Fanout maintenance needed (separate issue worth opening):**
1. Remove `--no-interactive` flag from Codex invocation in `scripts/review/plan-review-fanout.sh` (current Codex CLI no longer supports it)
2. Add `GEMINI_CLI_TRUST_WORKSPACE=true` to the Gemini invocation environment, or add `--skip-trust` to the Gemini command

These failures **do not affect** Wave 3 single-provider Claude adversarial reviews committed at `69f3b1c02` — those remain the primary verdict source for morning approval triage.

### Label Namespace Gap — Resolved After User Authorization

`vamseeachanta/digitalmodel` did not have a `status:plan-review` label (only `status:pending`, `blocked`, `done`, `working`, `closed`, and `plan-approved`). After user explicitly authorized `status:plan-review` marking, I created the label and applied it to all 10 issues.

### Label Namespace Gap — Discovered Mid-Batch

`vamseeachanta/digitalmodel` does not have a `status:plan-review` label (only `status:pending`, `blocked`, `done`, `working`, `closed`, and `plan-approved`). All 10 label-application attempts failed with `'status:plan-review' not found`. Comments were posted anyway — verdict info is fully visible on each issue.

**Recommendation:** if the workspace-hub issue-planning-mode workflow is intended to apply cross-repo, create `status:plan-review` in digitalmodel:
```bash
gh label create "status:plan-review" --repo vamseeachanta/digitalmodel --description "Awaiting user approval" --color c5def5
```

### Git Lock Contention — Recurring

Multiple `.git/index.lock` events during the batch, some from `pts/6` (your other claude session's stuck `git status` at ELAPSED 7:49), some from concurrent reviewer-agent `git status` calls. **Impact:** Wave 3 amendment commit failed silently once (exit 0 but `fatal: unable to write new index file` — exit-code masking by `tail` pipe). Eventually landed cleanly in the atomic 21-file commit after manual stale-lock removal.

**Lesson for future batches:** commits running in background must use `set -o pipefail` AND check `$PIPESTATUS` explicitly, not rely on the pipeline's final exit code.

### Retry Protocol Validated

The **skeleton-first + pre-extracted-files + bounded-grep** retry pattern worked 2-for-2 (Explorer #279 and #282 both recovered after the original attempts stalled). Worth promoting to a standard retry protocol for watchdog-killed recon agents in future batches.

### Cross-Session Artifacts Detected

Between 04:41-04:50 (during my Wave 1), another claude session wrote these plans unrelated to my batch:

- `docs/plans/2026-04-24-issue-2103-aqwa-bemrosetta-ingestion.md`
- `docs/plans/2026-04-24-issue-2124-orcina-resources-examples-training.md`
- `docs/plans/2026-04-24-issue-2125-orcina-auto-refresh.md`

And one `#2227` plan edit also showed up staged at commit time. **I explicitly excluded all four from my commit** by using specific paths. They remain unstaged/uncommitted in your working tree for your review.

## Next Actions (Recommended, Not Prescribed)

1. **Review this report.** Decide push/don't-push for commit `035579032`.
2. **Triage the 2 MAJOR plans** (#279, #501) — decide revise-in-place vs. re-plan-from-scratch.
3. **Provide user decisions** for #486 (API 17R procure vs. pivot) and #503 (licensing gate + consolidation approach).
4. **Triage 8 MINOR plans** — review picked tradeoff defaults, overrule if needed.
5. **Decide cross-session coordination** for #503 vs. #2124/#2125.
6. **Optional:** create `status:plan-review` label in digitalmodel if you want the workflow mirrored there.
7. **Optional:** run the full 3-provider cross-review fanout (`scripts/review/plan-review-fanout.sh <plan>`) on plans you're close to approving, for independent Codex+Gemini signal.

## What's NOT in This Batch

- **No plan is self-approved.** Per `feedback_never_offer_to_self_label_plan_approved`, the `status:plan-approved` gate is user-only.
- **No code changes.** This was a planning-only batch.
- **Deferred issues:** #517, #518, #519 (coupled to #515's approach); #507 (child of #503).
