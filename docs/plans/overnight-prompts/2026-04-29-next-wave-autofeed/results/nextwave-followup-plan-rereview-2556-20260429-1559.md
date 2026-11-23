# Next-wave follow-up plan re-review — issue #2556 (vessel-contractor brochure + send tracker)

> **Lane kind:** Plan-rereview (cold-context, read-only). NOT a patch lane; NOT an approval lane.
> **Worker:** Claude (Opus 4.7) interactive autofeed, ace-linux-1 control plane.
> **Date / timestamp:** 2026-04-29 15:59 CT.
> **Inputs read:** plan body, prior gtm-review-2556-2557 result, prior 13:56 patch result, three nextwave review artifacts (claude/codex/gemini), brochure outline, capability-chart storyboard, plan template.
> **Result artifact path (the single file written by this lane):** `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2556-20260429-1559.md`

---

## Verdict

**APPROVE_FOR_USER_REVIEW** (with one optional MINOR cleanup noted in §New-regression hunt item N1).

The 13:56 plan-patch lane resolved all three blocking findings from Claude r1 (#1 gap-proof factual error, #3 #2555 ordering, #6 duplicate-source disposition) and all four MINOR findings (#2 proof-count provenance, #4 retrieval-completeness, #5 demo-path exactness, #7 runtime-enforcement boundary) at the plan-document level. No false multi-provider-consensus claim is made; the plan honestly stays at `status:draft` and explicitly forbids promotion past `status:plan-review` until two independent gates clear (operator runs cross-review fanout from un-sandboxed terminal, and #2555 closes with chart artifacts under `docs/reports/gtm/charts/`).

The plan is ready for the user to review. It is **not** ready for `status:plan-approved` and the patch lane correctly did not propose it.

---

## Live state (read-only)

`gh issue view 2556 --json state,labels,updatedAt` returned:

```
{"state":"OPEN",
 "labels":[{"name":"priority:high"},{"name":"cat:business"},{"name":"cat:strategy"},{"name":"domain:gtm"}],
 "updatedAt":"2026-04-29T15:26:17Z"}
```

No `status:plan-review` or `status:plan-approved` label is present — confirms the prior 13:56 patch lane's claim that no GitHub mutation occurred. Last `updatedAt` of 15:26Z is consistent with the prior wave's `gh issue comment` draft step (drafts written, not posted).

---

## Per-finding re-check (each Claude r1 finding vs. patched plan)

| # | Original Claude r1 finding | Severity | Status after r2 patch | Evidence in patched plan |
|---|---|---|---|---|
| 1 | Gap-proof claim — `vessel-installation-contractors/` directory empty (no `email-templates.md`) | **MAJOR / blocking** | **RESOLVED** | Plan §Resource Intelligence "Existing repo code" line 29 now `Found:` the existing 5,157-byte `email-templates.md` (2026-04-02); §"Evidence → File existence" line 80 lists it as `EXISTS` with the retire-path annotation; §"Gap proofs" line 90 rewrites the `ls` proof. Filesystem `ls -la` confirms the file at 5,157 bytes, mtime 2026-04-02 — plan now matches reality. |
| 2 | 1,292-cases proof claim ships with no provenance check | MINOR | **RESOLVED-BY-GATE** | New TDD row `brochure_proof_count_provenance` at line 220 requires each per-demo number (Demo 1: 680 / 2: 72 / 3: 180 / 4: 60 / 5: 300) trace via `grep` to `digitalmodel/examples/demos/gtm/demo_0X_*.py` or its README. Verification deferred to brochure-source build time; plan-level gate now exists. |
| 3 | `outline_chart_slots_match_2555` unverifiable until #2555 ships chart artifacts | **MAJOR / blocking** | **RESOLVED-BY-GATE** | Front-matter line 7 declares `Depends on: #2555` with explicit "this plan cannot promote past `status:plan-review` until #2555 lands real chart artifacts under `docs/reports/gtm/charts/`". TDD list (lines 218–219) splits into `_storyboard` (passable today against the existing storyboard at `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md`) + `_artifacts` (hard-blocked behind #2555 closure). Filesystem confirms `docs/reports/gtm/charts/` does NOT exist — the gate is real. |
| 4 | `installation-analysis-method-note.md` cited in outline §3.3 but missing from plan's Documents-consulted | MINOR | **RESOLVED** | §Resource Intelligence "Documents consulted" line 47 now lists the file with size + date; §"File existence" line 81 confirms `EXISTS` (17,720 bytes, 2026-04-22). `ls -la` confirms. |
| 5 | Demo-path strings in outline §3.4 cite bare `demo_01`/`demo_02` shorthand | MINOR | **RESOLVED-AT-PLAN-LEVEL** (outline body fix deferred) | New TDD row `brochure_demo_path_full_filenames` at line 221 enumerates the five canonical filenames (`demo_01_dnv_freespan_viv.py`, `demo_02_wall_thickness_multicode.py`, `demo_03_deepwater_mudmat_installation.py`, `demo_04_shallow_water_pipelay.py`, `demo_05_deepwater_rigid_jumper_installation.py`) as the pass condition. **Outline body itself NOT edited** — the patch result explicitly states this is intentional boundary compliance for the patch lane. The plan's TDD now forces correction of the outline before publication. Outline file `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` lines 64–68 still cite `demo_01`/`demo_02`/etc. (verified by direct read), but this is now a forced-failure at gate time, not a silent ship. Acceptable for a plan-only patch; user-review-time gate is the right surface to track this. |
| 6 | Disposition of canonical-folder `email-templates.md` undeclared | **MAJOR / blocking** | **RESOLVED** | New first row in §Files to Change (line 188): `Modify (retire+redirect)` — body replaced with deprecation header pointing at `docs/gtm/email-outreach-templates.md` as the single source-of-truth; preserves history per #1669 Phase 1 reference; explicit "Do NOT delete". §Resource Intelligence and §Risks both reference this disposition. Duplicate-source trap is closed at plan level. |
| 7 | `send_tracker_state_enum` / `_legal_gate` deferred to "future issue" but ACs treat them as in-scope | MINOR | **RESOLVED** | Acceptance Criteria line 232 explicitly rephrased: "runtime enforcement of the `send_state` enum and the `last_legal_scan_utc` legal gate is documentation-surface only in this plan; binding runtime enforcement is out of scope and tracked under §Risks 'runtime-enforcement follow-up'." §Risks line 282 adds the must-file follow-up: "Before any human-initiated outbound send executes against a populated tracker, a sibling issue must be filed to (a) write a tracker-validator script that fails closed when state-machine or legal-gate invariants are violated, (b) wire it into pre-commit and into a hypothetical `gh-action: gtm-send-validator`, and (c) define the precommit hook path." Boundary is now explicit, not implicit. |

**Summary:** all 7 r1 findings RESOLVED at plan level (3 blocking, 4 MINOR). Three of the resolutions (#2, #3, #5) are gate-form rather than direct-edit-form — meaning the plan declares a TDD/dependency check that will fail at the next iteration if not addressed, rather than silently shipping. This is correct for a plan-only patch lane.

---

## New-regression hunt (per the prompt's six explicit angles)

| Angle | Finding | Severity |
|---|---|---|
| Existing email-templates.md disposition | **CLEAN.** §Files to Change row 1 (line 188): "Modify (retire+redirect)" with one-screen deprecation header pointing at `docs/gtm/email-outreach-templates.md`. Explicit "Do NOT delete" preserves #1669 Phase 1 history reference. No regression. | None |
| #2555 dependency wording | **CLEAN.** Front-matter line 7 declares hard ordering ("this plan cannot promote past `status:plan-review` until #2555 lands real chart artifacts"); soft input from #2554 separately scoped. §Risks line 280 reiterates with a mitigation. TDD list splits the previously-conflated check into `_storyboard` (passable today) + `_artifacts` (hard-blocked). No regression. | None |
| Demo path exactness | **CLEAN AT PLAN LEVEL; OUTLINE STILL HAS THE OLD STRINGS.** TDD row `brochure_demo_path_full_filenames` (line 221) enumerates the five canonical filenames as the pass condition. Outline file body unchanged (verified — lines 64–68 still say `demo_01`/`demo_02`/etc.). The patch result explicitly states this is intentional: the patch lane does not edit `docs/reports/gtm/`. The TDD now forces correction at the next iteration. Acceptable; not a regression. | None at plan level |
| Proof-count provenance | **CLEAN.** TDD row `brochure_proof_count_provenance` (line 220) requires `grep`-trace of each per-demo number to `digitalmodel/examples/demos/gtm/demo_0X_*.py` or its README. Plan-level gate now exists. No regression. | None |
| Tracker legal-gate / runtime enforcement boundary | **CLEAN.** Acceptance Criteria line 232 explicitly limits scope to documentation-surface verification. §Risks line 282 declares the must-file runtime-enforcement follow-up issue with three explicit deliverables before any send executes. Boundary now explicit. No regression. | None |
| Cross-provider coverage claims | **CLEAN.** §Adversarial Review Summary table (lines 248–251) clearly marks Claude as `MAJOR (single-author r1)`, Codex as `UNAVAILABLE` with #2479 + permission-gate citation, Gemini as `UNAVAILABLE` with permission-gate citation. The "Provider coverage after r2" line (269) explicitly says "Unchanged. Codex remains UNAVAILABLE; Gemini remains UNAVAILABLE; r2 is a single-author plan-revision pass, NOT a re-review." No false consensus claim. The plan correctly cites `docs/BUSINESS_BRAIN.md` lines 89–97 as the gate that current state does not meet. No regression. | None |

### Independent regression sweep beyond the prompt's six angles

| Item | Observation | Severity |
|---|---|---|
| **N1 — File-existence labels for already-existing report docs** | Plan §Resource Intelligence "File existence" still labels `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` and `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md` as `MISSING (this plan creates)` (lines 84–85). `ls -la` confirms BOTH files actually exist on disk (12,034 bytes and 12,510 bytes respectively, both at 2026-04-29 11:51). The plan handles this with the convention "these two `docs/reports/gtm/` documents land **with this draft plan**" (prose at line 200), but the literal `MISSING` tag contradicts a reviewer's `ls`. **This is a pre-existing inconsistency, not introduced by the 13:56 patch** — the patch's edit #5 rewrote this very block but retained the `MISSING` framing. The Claude r1 review observed the schema doc exists (read it end-to-end) but did not flag this; would be a defensible MINOR catch on a fresh re-review. Optional cleanup for the next iteration: change the convention to `EXISTS (created with this draft plan)` or `EXISTS (planning-artifact-at-draft-time)`. Not a blocker. | MINOR (pre-existing; not patch-introduced) |
| **N2 — Source-count comment math** | Line 93 reads "Source count: 6 distinct sources (issue body + #2554/#2555/#1669/#2016 + BUSINESS_BRAIN + 9 GTM files including installation-analysis-method-note.md added in r2). Meets ≥3 requirement." The arithmetic is non-obvious: "6 distinct sources" = issue body (1) + 4 sibling issues (4) + BUSINESS_BRAIN (1) = 6. Then "+ 9 GTM files" is additive but not part of the 6. The comment is internally consistent but reads sloppy. Cosmetic only. | NONE (cosmetic) |
| **N3 — Pricing consistency surface** | Brochure outline §3.5 lists "$5K–15K / $25K–75K / $10K/month" matching `capability-summary.md`. Plan does not test this consistency; only `brochure_provenance_check` would catch it indirectly. Not in scope of the patch lane and not raised in r1; flagging for the user-review pass only as a candidate additional TDD row. | NONE (out of scope of patch) |
| **N4 — Codex/Gemini run instructions** | Operator-next-step block (line 269) says "after `npm install -g @openai/codex@0.123.0` per [#2479](.../issues/2479)". Per `feedback_codex_cli_0_124_upstream_regression.md` and the Codex absence stub, the 0.123.0 downgrade also hangs from inside Claude Code's Bash tool but should work from a plain user terminal. The plan's instruction is correct because it directs the operator to a plain (un-sandboxed) terminal. No regression. | None |

No new MAJOR regressions. One MINOR pre-existing inconsistency (N1) that is not patch-introduced and is optional to fix in the next iteration.

---

## Provider-coverage statement

- **Claude (single-author, r1 nextwave + r2 self-revision + this r3 cold-context re-review):** all three lenses authored by Claude. r3 (this artifact) is a fresh-context re-review, not a self-revision pass. r3 has no privileged knowledge of the original review reasoning; it independently verified evidence via filesystem and live `gh` query.
- **Codex:** UNAVAILABLE for this plan in this session (Bash permission gate blocks `scripts/review/plan-review-fanout.sh` dispatch; upstream codex-cli 0.124.0 stdin-hang per [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) compounds this). r3 did not attempt to dispatch Codex (forbidden by the lane prompt's hard guardrails). Operator must run from un-sandboxed terminal after `npm install -g @openai/codex@0.123.0`.
- **Gemini:** UNAVAILABLE for this plan in this session (Bash permission gate). Wrapper itself is healthy after the 2026-04-24 `GEMINI_CLI_TRUST_WORKSPACE` fix. r3 did not attempt to dispatch (forbidden). Operator must run from un-sandboxed terminal.

This artifact does **not** establish multi-provider consensus and does **not** propose `status:plan-review` promotion. The plan is approved for **user review only**, not for label flips.

---

## Boundary compliance

| Guardrail | Status | Evidence |
|---|---|---|
| Read-only re-review only — no patches to plan/report/tracker/brochure/email/source/review files | ✅ | Only file written by this lane: the result artifact at the prompted path. No edits to plan, outline, schema, tracker, brochure, email, source code, prior review artifacts, or generated comment packs. |
| No GitHub mutations | ✅ | Only `gh issue view 2556 --json state,labels,updatedAt` (read-only). No `gh issue edit`, `gh issue comment`, `gh issue close`, `gh pr *`, or label flip. |
| No `status:plan-approved` flip; no `.planning/plan-approved/*` markers | ✅ | None created or edited. Plan front-matter unchanged from r2 ("draft (plan-revision r2 ...; ready for re-review, NOT for approval)"). |
| No `status:plan-review` self-promotion | ✅ | Verdict is APPROVE_FOR_USER_REVIEW — explicit user-in-loop gate; no autonomous label intent. |
| No `scripts/review/plan-review-fanout.sh`, `codex`, `gemini`, or mutating Hermes invocation | ✅ | None dispatched. Forbidden by lane prompt. |
| No `git push`, no PR ops, no outreach | ✅ | None attempted. |
| Did NOT overwrite other lanes' result files | ✅ | Pre-write `ls` confirmed the target path did not exist. The two prior lane results (`gtm-review-2556-2557.md` and `nextwave-followup-plan-patch-2556-20260429-1356.md`) were read-only inputs. |
| Single primary result artifact at the prompted path | ✅ | One file written: `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2556-20260429-1559.md`. |
| No private contact details, no PII, no secret printing | ✅ | This artifact contains no contact details, no PII, no secrets. |

---

## Operator next steps (after user review of this artifact)

1. **Decide whether to act on N1.** Optional cleanup — change the `MISSING (this plan creates)` annotation for the brochure-outline + send-tracker-schema files (which actually exist on disk) to `EXISTS (created with this draft plan)` for reviewer-clarity. Not blocking.
2. **Run the cross-review fanout from an un-sandboxed terminal** to land real Codex + Gemini artifacts (per the patch result's Operator next steps; not repeated here).
3. **Wait for #2555 to close with chart artifacts under `docs/reports/gtm/charts/`** before promoting past `status:plan-review`.
4. **Apply outline body fix for demo-path strings** (Claude r1 finding #5) — TDD row `brochure_demo_path_full_filenames` will fail at gate time if outline still has `demo_01`/`demo_02` shorthand at publication time.
5. **File the runtime-enforcement follow-up issue** before any human-initiated outbound send executes — three explicit deliverables documented in plan §Risks line 282.
6. **User decides** between the two open questions retained from r1 (brochure format split: PDF/HTML/both; tracker write-frequency: append-on-event vs batch nightly).

---

## Lane classification

**Lane:** plan-rereview (cold-context, read-only).

**Verdict:** `APPROVE_FOR_USER_REVIEW`. The 13:56 plan-patch lane resolved all r1 findings at plan-document level, introduced no new MAJOR regressions, and correctly preserved the plan's `status:draft` posture with explicit gates against `status:plan-review` promotion. One MINOR pre-existing inconsistency (N1: `MISSING` annotation for two report docs that actually exist on disk) is optional cleanup, not a blocker.

**Provider coverage:** UNCHANGED from r2. Codex + Gemini remain UNAVAILABLE; this r3 is a single-author Claude cold-context re-review, not a multi-provider lens.

**Promotion:** **NONE.** Plan stays at `status:draft`. The user is the gate to advance. r3 explicitly does NOT propose, apply, or pre-authorize any GitHub label change, plan-approved marker, fanout dispatch, implementation, outreach, or edits to other artifacts.

**Files written by this lane (exhaustive — exactly one path):**
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2556-20260429-1559.md`

**Files NOT written by this lane (despite being relevant):**
- The plan body — read-only re-review.
- Any file under `scripts/review/results/` — this is not a re-review-artifact lane in the cross-review-results sense; the prompt directs the result to the autofeed `results/` directory, and that single primary artifact is what landed.
- Any file under `docs/reports/gtm/` — out-of-scope.
- Any GitHub label, comment, issue body, or PR — read-only.
- Any `.planning/plan-approved/*` marker — forbidden.
- Any source code, tracker, brochure, email artifact — out-of-scope.

**Final lane classification:** `APPROVE_FOR_USER_REVIEW` — cold-context plan re-review of issue #2556 finds the 13:56 patch resolved all r1 findings without introducing MAJOR regressions; user review is the next gate.
