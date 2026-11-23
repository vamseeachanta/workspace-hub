# Next-wave follow-up plan re-review — issue #2556 post-r3 outline/demo-path patch

> **Lane kind:** Plan re-review (cold-context, read-only). NOT a patch lane; NOT an approval lane.
> **Worker:** Claude (Opus 4.7) bounded planning/review/synthesis worker, ace-linux-1.
> **Date:** 2026-04-29.
> **Inputs read (verbatim):**
> - `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md`
> - `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`
> - `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2556-outline-demo-paths-20260429-r1.md`
> - `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2556-file-existence-20260429-1712.md`
> **Result artifact (this file, exclusive output):** `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2556-post-r3-20260429-r1.md`
> **Pre-write `ls`:** target path did not exist; no collision; no overwrite.

---

## Verdict

**`APPROVE_FOR_USER_REVIEW`**

The r3 patch (1) replaces all five outline §3.4 executable demo citations with canonical `.py` filenames, (2) lands a Demo / proof-path canon table in the plan's Resource-Intelligence Evidence section whose byte-sizes match disk **exactly**, (3) consolidates the no-send legal gate into a seven-constraint plan-binding block at §Acceptance Criteria, (4) marks Claude r1 finding #5 RESOLVED in the Adversarial Review Summary, and (5) preserves the `status:draft` posture without introducing self-approval, implementation, outreach, or status-promotion language. The four blockers from the 17:12 re-review (multi-provider consensus, #2555 closure gate, runtime-enforcement follow-up issue, user format/cadence decisions) remain in force exactly as before. No new MAJOR or MINOR regression was introduced.

---

## Files inspected (read-only)

| Path | Lines read | State |
|---|---|---|
| `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` | 1–327 (full body) | working-tree `M` (uncommitted r3 edits) |
| `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` | 1–174 (full body) | working-tree `M` (uncommitted §3.4 fix) |
| `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2556-outline-demo-paths-20260429-r1.md` | 1–162 (full body) | untracked autofeed result (`??`) |
| `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2556-file-existence-20260429-1712.md` | 1–224 (full body) | untracked autofeed result (`??`) |

**Live disk evidence sampled** (read-only, via `ls`/`grep`):
- `digitalmodel/examples/demos/gtm/demo_01_dnv_freespan_viv.py` — 44,438 bytes (matches plan + outline citation)
- `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` — 50,067 bytes (matches)
- `digitalmodel/examples/demos/gtm/demo_03_deepwater_mudmat_installation.py` — 45,472 bytes (matches)
- `digitalmodel/examples/demos/gtm/demo_04_shallow_water_pipelay.py` — 60,376 bytes (matches)
- `digitalmodel/examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py` — 42,881 bytes (matches)
- `docs/reports/gtm/charts/` — **does not exist** (#2555 gate still binding)

`gh` was **not** invoked in this lane to avoid even read-side mutation surface; issue state was last verified by the 17:12 re-review (`updatedAt` 2026-04-29T15:26:17Z), and that verdict is preserved by reference rather than re-fetched.

---

## Findings table

| ID | Severity | Evidence (path:line) | Required action |
|---|---|---|---|
| F1 | OK | `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md:64–68` — five canonical `.py` citations present; **no** `demo_01`-style shorthand executable citation remains in §3.4 (`grep -n "demo_0"` returns only the 5 canonical strings + the in-prose `demo_03` references in the verification footnote). | None — claim verified. |
| F2 | OK | `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md:95–101` — the new Demo / proof path canon table cites byte-sizes (44,438 / 50,067 / 45,472 / 60,376 / 42,881) that exactly match the live `ls -la digitalmodel/examples/demos/gtm/` output; sum 680+72+180+60+300 = 1,292 = the `capability-summary.md` headline. | None — provenance is reviewer-grep-locatable. |
| F3 | OK | `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md:255–267` — "No-send legal gate (explicit, plan-binding)" sub-block lists all seven constraints (zero outbound sends, `legal-sanity-scan.sh --diff-only` exit-0, provenance-citation rule, public-tracker PII rule, `last_legal_scan_utc` rule, `Depends on: #2555` hard gate, personalization-hook clearance). Each cross-references an existing TDD row or §Risks line — consolidation, not duplication. | None — block is auditable in one place. |
| F4 | OK | `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md:291` — Adversarial Review Summary row #5 reads "**r3 (this revision):** outline §3.4 body now cites canonical filenames … **Status: RESOLVED.**" Inline-naming the five canonical filenames makes resolution `grep -F`-locatable. Lines 297–304 add the r3-delta sub-block, which explicitly states "Provider coverage after r3: Still UNCHANGED" and re-lists the four blockers from the 17:12 re-review. | None — summary is accurate and conservative. |
| F5 | OK | `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md:3` — Status line still reads "draft (… ready for re-review, NOT for approval)". `docs/plans/overnight-prompts/.../nextwave-followup-plan-patch-2556-outline-demo-paths-20260429-r1.md:27,116,155` — patch result reaffirms "Promotion: NONE", explicitly disclaims `status:plan-review` and `status:plan-approved`, and states the user remains the gate. No `.planning/plan-approved/*` marker referenced; no GitHub-mutation language; no `gh issue edit/comment/close` invocation. | None — no self-approval, implementation, or outreach language introduced by r3. |
| F6 | OK (carried) | `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md:7,231,264` — `Depends on: #2555` is anchored in three independent surfaces (front-matter, TDD row `outline_chart_slots_match_2555_artifacts`, no-send constraint #6); `ls -la docs/reports/gtm/charts/` returns "No such file or directory" — gate is real. | None — gate holds. |
| F7 | NONE (cosmetic, carried forward; not r3-introduced) | `docs/plans/...:87` still labels the private tracker `MISSING (gitignored, NEVER tracked)`, while `.gitignore` does not yet contain the matching glob (the line is forward-looking; the matching `.gitignore` modify row is queued in §Files to Change). Identical to the 17:12 re-review's N2 observation. | Optional: reword to "MISSING (will be gitignored once execution lands the .gitignore line)" or pre-land the glob. **Not** a blocker. |
| F8 | NONE (cosmetic, carried forward; not r3-introduced) | `docs/plans/...:105` source-count comment ("6 distinct sources … + 9 GTM files") is loosely-worded. Identical to the 17:12 re-review's N3 observation. | Optional copy edit; **not** a blocker. |

**No new MAJOR.** **No new MINOR.** Two cosmetic observations are both carried forward unchanged from prior re-reviews — neither was introduced by the r3 patch.

---

## Verification of the r3 patch's claims

| Patch-result claim | Verified? | Evidence |
|---|---|---|
| Outline §3.4 §body fix replaces shorthand with canonical filenames | YES | `grep -n "demo_0" docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` returns lines 64–68 with the five canonical `.py` filenames; no `\bdemo_0[1-5]\b`-shorthand executable citation remains. The footnote at line 70 cross-cites byte-sizes that match disk exactly. |
| Plan front-matter bumped r2 → r3, posture preserved | YES | Line 3 reads "draft (plan-revision r3 …; ready for re-review, NOT for approval. r3 lands the outline body fix for Claude r1 finding #5 …)". The "draft / NOT for approval" qualifier is intact. |
| Plan §Resource Intelligence Evidence gained Demo / proof path canon table | YES | Lines 93–105 host the table + cases-cited column + 1,292 sum + cross-reference to TDD rows `brochure_demo_path_full_filenames` / `brochure_proof_count_provenance`. |
| Plan §Acceptance Criteria gained "No-send legal gate (explicit, plan-binding)" sub-block | YES | Lines 255–267 host the seven-constraint block with explicit revert-and-drop language for violations. |
| Plan §Adversarial Review Summary updates row #5 → RESOLVED + r3 delta block | YES | Line 291 row #5 RESOLVED; lines 297–304 r3-delta sub-block enumerates the four substantive changes and re-asserts UNCHANGED provider coverage. |
| `git diff --stat` reports 2 files / 44 insertions / 9 deletions | NOT INDEPENDENTLY RE-RUN by this lane (read-only re-review) — claim is consistent with the working-tree `M` state observed for both files in `git status -s`. | `git status -s` shows exactly the two named files modified; no scope creep. |
| Two #2556 planning files only modified | YES | `git status -s` returns `M docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` and `M docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`; everything else in the working tree is `??` autofeed lane output (parallel lanes for #2554 / #2555 / #2557 / #2550-2552), not edits to live surfaces. |
| Patch did not commit, push, mutate GitHub, send outreach, build PDF, run scripts | YES | Working-tree `M` only; no commit on either file (last commit `e45bfcff1` is unrelated reconcile of the #2555 plan approval); no `.planning/plan-approved/*` marker created; patch-result file repeatedly disclaims promotion at lines 27, 116, 117, 155. |

All r3 claims that this lane could verify under read-only constraints **check out**. The one claim deferred (the exact `git diff --stat` arithmetic) is consistent with observable state but was not independently re-derived to avoid running additional shell beyond what is needed.

---

## Remaining blockers (unchanged from 17:12 re-review)

The r3 patch resolves Claude r1 finding #5 (deferred outline body fix) and consolidates the no-send legal gate into one auditable block. It **does not** change the following, which remain in force as the gates to advancement:

1. **Multi-provider consensus is still single-author.** Codex remains UNAVAILABLE (`#2479` 0.124.0 stdin-hang + Bash permission-gate in this autofeed session, per `feedback_codex_cli_0_124_upstream_regression.md` and `feedback_permission_gate_blocks_cross_review.md`). Gemini remains UNAVAILABLE (Bash permission-gate; wrapper itself is healthy after the 2026-04-24 `GEMINI_CLI_TRUST_WORKSPACE` fix). Operator must run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` from an un-sandboxed terminal (after `npm install -g @openai/codex@0.123.0` per [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479)) to land real Codex + Gemini artifacts before the `BUSINESS_BRAIN.md` lines 89–97 consensus criterion can be met. Forbidden by this re-review lane.
2. **`#2555` closure gate.** `outline_chart_slots_match_2555_artifacts` cannot pass until [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555) lands chart files under `docs/reports/gtm/charts/`. Independently re-verified absent on disk by this lane. Promotion past `status:plan-review` is hard-blocked on this; front-matter `Depends on: #2555` (line 7), TDD row `outline_chart_slots_match_2555_artifacts` (line 231), and no-send constraint #6 (line 264) are the three independent anchors.
3. **Runtime-enforcement follow-up issue must be filed before any human-initiated outbound send executes.** Tracker-validator script (fail-closed on `send_state` enum and `last_legal_scan_utc` invariants) + pre-commit hook + CI check. Plan §Risks line 317 names the must-file follow-up. Not filed by this lane (would mutate GitHub).
4. **User decisions retained from r1:**
   - Brochure output formats — PDF only / HTML only / both (default proposal in outline §7 question 1: Markdown source → PDF + HTML, but user decision needed).
   - Tracker write-frequency — append-on-event (every send) vs. batch nightly (default proposal: append-on-event, human-initiated only).
5. **Cosmetic carry-forwards (NOT blocking):** F7 (line 87 `MISSING (gitignored, NEVER tracked)` is forward-looking until `.gitignore` glob lands) and F8 (line 105 source-count arithmetic). Both already noted by the 17:12 re-review; r3 did not introduce them and did not promote them to scope.

---

## Next safe action

**Operator gate.** One of:

(a) Land the working-tree r3 edits via `git commit` of `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` and `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` (the patch result file documents these as the two scoped paths). The commit itself is operator-initiated; this re-review lane does not commit or push.

(b) Run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` from an un-sandboxed terminal — after the codex-cli downgrade per [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) — to land Codex + Gemini artifacts and unblock the multi-provider-consensus criterion. Required before any future `status:plan-review` label flip.

The plan stays at `status:draft`. The user remains the gate to advance to `status:plan-review`. A separate user decision is the gate to advance to `status:plan-approved`. This re-review **does not propose, apply, or pre-authorize** any GitHub label change, plan-approved marker, fanout dispatch, implementation, outreach, or edits to other artifacts.

---

## Boundary compliance

| Guardrail | Status | Evidence |
|---|---|---|
| Read-only — no edits to plan, outline, schema, brochure, tracker, email, source, scripts, `.gitignore`, or any sibling-issue surface | OK | Only the named result artifact at the prompted path was written; `git status -s` confirms no working-tree change beyond the pre-existing r3 patch state and parallel autofeed lane outputs. |
| No GitHub mutations | OK | No `gh issue edit/comment/close`, no label flip, no `gh pr` invocation. `gh issue view` was deliberately **not** invoked to minimize even read-side surface; issue state preserved by reference to 17:12 re-review's `updatedAt` 2026-04-29T15:26:17Z. |
| No `status:plan-review` self-promotion; no `status:plan-approved` flip; no `.planning/plan-approved/*` marker | OK | Verdict is `APPROVE_FOR_USER_REVIEW` — explicit user-in-loop gate. No autonomous label intent. No "may be applied automatically" language. No pre-authorization of downstream patch / re-review / autofeed lanes. |
| No outreach sends; no public claims from private/raw data; no contact details printed | OK | This artifact contains no contact details, no PII, no secrets, no tracker rows, no email-body content. |
| No commits, no pushes, no PR ops | OK | No `git commit`, `git push`, `git rebase`, or PR-creation invoked. Working-tree `M` for the two #2556 planning files was already present from the r3 patch lane and was not modified by this re-review. |
| No production implementation (no `digitalmodel` run, no chart render, no PDF build, no `legal-sanity-scan.sh` execution) | OK | This lane ran only `ls` / `grep` / `git status -s` for verification; no script execution. |
| Did not overwrite an existing result path | OK | Pre-write `ls` returned "No such file or directory" for the target path. Single primary output written. |
| Single primary result artifact at the prompted path | OK | Exactly one file written: `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2556-post-r3-20260429-r1.md`. |

---

## Lane classification

**Lane:** plan re-review (cold-context, read-only, post-r3 patch verification for issue #2556).

**Verdict:** `APPROVE_FOR_USER_REVIEW`.

**Provider coverage:** UNCHANGED. Codex + Gemini remain UNAVAILABLE for this plan in this session (`#2479` upstream + Bash permission gate). This is a single-author Claude cold-context re-review; multi-provider consensus is **not** established by this artifact.

**Promotion:** **NONE.** Plan stays at `status:draft`. The user is the gate to advance.
