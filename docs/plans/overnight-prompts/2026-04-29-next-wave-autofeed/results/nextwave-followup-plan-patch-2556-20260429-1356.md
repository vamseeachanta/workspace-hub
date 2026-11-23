# Next-wave follow-up plan patch — issue #2556 (vessel-contractor brochure + send tracker)

> **Lane kind:** Plan-revision r2 patch (planning-only). **Not** a re-review lane; **not** an approval lane.
> **Worker:** Claude (Opus 4.7) interactive autofeed, ace-linux-1 control plane.
> **Date / timestamp:** 2026-04-29 13:56 CT.
> **Source prompt:** docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/ (this batch).
> **Plan touched (only file changed beyond this artifact):** `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md`.

---

## Live state at run start

Read-only via `gh issue view 2556 --json number,title,state,labels,updatedAt`:

| Field | Value |
|---|---|
| Number | 2556 |
| State | OPEN |
| Title | feat(gtm): vessel contractor brochure and outbound send tracker |
| Labels | `priority:high`, `cat:business`, `cat:strategy`, `domain:gtm` |
| `updatedAt` | 2026-04-29T15:26:17Z |

No `status:plan-review` or `status:plan-approved` label is present. The plan-revision r2 in this lane does NOT add either; status remains `draft` per the autofeed prompt's hard guardrails.

---

## Summary of plan edits

Eleven targeted edits applied to `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md`. No other files were modified. Edits address all three blocking findings from the Claude r1 review and four MINOR findings that fit within the patch lane's scope (i.e., that did not require expanding scope or editing the brochure outline / report files outside the plan).

| # | Plan section | Change | Resolves |
|---|---|---|---|
| 1 | Front-matter (lines 3–8) | Status string annotated as plan-revision r2; new `Depends on:` line declares hard ordering against #2555 + soft input from #2554 | Claude finding #3 (blocking) |
| 2 | §Resource Intelligence → Existing repo code (line 29) | Added `Found:` row for the existing 5,157-byte `email-templates.md` (2026-04-02) and pointed at the retire-and-redirect disposition in §Files to Change | Claude findings #1 + #6 (both blocking) |
| 3 | §Resource Intelligence → Existing repo code (line 30) | Reframed the "directory empty" gap as "directory sparse" — only `email-templates.md` exists | Claude finding #1 (blocking) |
| 4 | §Resource Intelligence → Documents consulted (line 47) | Added `installation-analysis-method-note.md` (17,720 bytes, 2026-04-22) | Claude finding #4 (MINOR) |
| 5 | §Resource Intelligence → File existence (lines 80–82) | Replaced false "directory; empty" with the real file present, plus method-note + #2555 storyboard | Claude finding #1 (blocking), #4 (MINOR) |
| 6 | §Resource Intelligence → Gap proofs (lines 89–91) | Rewrote the `ls` proof to acknowledge `email-templates.md` and to anchor the #2555 storyboard-only state | Claude findings #1 + #3 (both blocking) |
| 7 | §Resource Intelligence → Source count comment (line 93) | Bumped "5 distinct sources" → "6 distinct sources, 9 GTM files" | Plan-internal consistency |
| 8 | §Files to Change (new top row) | Added `Modify (retire+redirect)` row for the canonical-folder `email-templates.md` — body replaced with a deprecation header pointing at `docs/gtm/email-outreach-templates.md` | Claude finding #6 (blocking) |
| 9 | §TDD Test List (rows around lines 211–214) | Split `outline_chart_slots_match_2555` into `_storyboard` (passable today) + `_artifacts` (hard-blocked behind #2555 closure); added `brochure_proof_count_provenance`; added `brochure_demo_path_full_filenames`; clarified `copy_variants_per_tier` source path | Claude findings #2, #3, #5 |
| 10 | §Acceptance Criteria (send-tracker bullets) | Rephrased to verify documentation surface (schema doc + grep checks) only; runtime enforcement explicitly deferred to follow-up issue | Claude finding #7 (MINOR) |
| 11 | §Adversarial Review Summary (post-result block) + §Risks and Open Questions | Added "Revisions made (plan-revision r2)" finding-resolution table + ordering risk + duplicate-source risk + runtime-enforcement follow-up note | Records the patch + resolves Claude finding #7 |

---

## Finding-by-finding resolution table

Mapped against `scripts/review/results/2026-04-29-plan-2556-nextwave-claude.md` (the only structured review artifact for this plan; Codex/Gemini remain UNAVAILABLE).

| Claude r1 finding | Severity | Status after r2 | Plan section(s) edited | Notes |
|---|---|---|---|---|
| #1 — Gap-proof contradicts filesystem reality (`vessel-installation-contractors/email-templates.md` exists) | **MAJOR / blocking** | **Resolved** | Resource Intelligence: Existing repo code, File existence, Gap proofs | Plan now correctly lists the 5,157-byte 2026-04-02 file as `Found:` and redirects the Gap framing to "directory sparse, only template doc present" |
| #2 — Brochure 1,292-cases proof-claim has no provenance check | MINOR | **Resolved** | TDD Test List | New `brochure_proof_count_provenance` row grep-traces each per-demo number to `digitalmodel/examples/demos/gtm/demo_0X_*.py` |
| #3 — `outline_chart_slots_match_2555` unverifiable (storyboard only, no chart artifacts) | **MAJOR / blocking** | **Resolved** | Front-matter `Depends on:` + TDD Test List + Risks | Front-matter declares `Depends on: #2555`; TDD row split into storyboard-passable today vs artifact-hard-blocked behind #2555 closure; promotion past `status:plan-review` gated |
| #4 — `installation-analysis-method-note.md` cited in outline §3.3 but missing from plan's Documents-consulted list | MINOR | **Resolved** | Resource Intelligence: Documents consulted, File existence | File added to both lists with size + date |
| #5 — Demo-path strings in outline §3.4 don't match real filenames | MINOR | **Resolved at plan level** | TDD Test List | New `brochure_demo_path_full_filenames` TDD row enumerates the five canonical filenames as the pass condition. **Note:** the outline file body itself is *not* edited from this lane — see §Boundary compliance. The plan's TDD now forces the outline to be corrected before publication. |
| #6 — Disposition of canonical-folder `email-templates.md` undeclared | **MAJOR / blocking** | **Resolved** | Files to Change (new row) + Resource Intelligence + Risks | New "Modify (retire+redirect)" row replaces body with deprecation header pointing at `docs/gtm/email-outreach-templates.md`; preserves history without leaving a duplicate-source trap |
| #7 — `send_tracker_state_enum` / `_legal_gate` deferred but ACs treat them as in-scope | MINOR | **Resolved** | Acceptance Criteria + Risks (runtime-enforcement follow-up) | ACs now verify documentation surface only; runtime enforcement made explicitly out of scope and surfaced as a must-file follow-up issue before any human-initiated outbound send |

All three blocking findings (#1, #3, #6) are addressed by content changes in the plan; not by promise. All four addressed MINOR findings sit within plan-only edits.

---

## Remaining blockers / user decisions

Even after r2, the plan is **not** ready for `status:plan-review`. Outstanding items:

1. **Multi-provider consensus is still single-author.** Codex and Gemini remain UNAVAILABLE for this plan. Per `docs/BUSINESS_BRAIN.md` lines 89–97, `status:plan-approved` requires *"repeated APPROVE/MINOR adversarial-review outcomes across Claude/Codex/Gemini with no unresolved MAJOR findings."* Operator must run, from an un-sandboxed terminal:

   ```
   npm install -g @openai/codex@0.123.0   # workaround for #2479
   bash scripts/review/plan-review-fanout.sh \
     docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md
   ```

   to land real Codex + Gemini artifacts before the consensus gate can flip.

2. **#2555 closure gate.** `outline_chart_slots_match_2555_artifacts` cannot pass until #2555 lands chart files under `docs/reports/gtm/charts/`. Promotion past `status:plan-review` is explicitly gated on this in the plan front-matter.

3. **Outline body fix (Claude finding #5).** The outline file `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` cites `demo_01`/`demo_02` shorthand that does not match real filenames. The plan's new TDD row makes this fail the gate, but the outline body itself was not edited from this lane (see §Boundary compliance). Operator should update the outline at the next pass.

4. **Runtime-enforcement follow-up issue.** Before any human-initiated outbound send executes against a populated tracker, a sibling issue must be filed to add a tracker-validator script + pre-commit hook + CI check that enforces the `send_state` state machine and `last_legal_scan_utc` legal gate at runtime. The plan now declares this explicitly in §Risks; the patch lane does not file the issue.

5. **User decision on brochure output formats.** Open question retained from r1: ship as PDF only, HTML only, or both? Plan recommends Markdown source + PDF for cold sends + HTML for the gated-URL surface. Flag at user-approval time.

6. **User decision on tracker write-frequency.** Append-on-event vs batch nightly. Default: append-on-event, human-initiated only. Flag at user-approval time.

---

## Boundary compliance

| Boundary | Status | Evidence |
|---|---|---|
| No production / code / report / tracker / brochure / email / outreach files modified | ✅ | Only the plan file and this result artifact were edited. `git diff --name-only` would show exactly two paths under `docs/plans/2026-04-29-issue-2556-...md` and the result file under `docs/plans/overnight-prompts/...nextwave-followup-plan-patch-2556-...md`. |
| No GitHub mutations | ✅ | Only `gh issue view 2556 --json ...` was used (read-only). No `gh issue edit`, `gh issue comment`, `gh issue close`, `gh pr *`, or label flip. |
| No outreach sends, no public claims from private/raw data, no private contact details | ✅ | Plan content is unchanged in those dimensions; this lane added zero PII, zero contact paths, zero outbound copy. |
| No `status:plan-approved` flip; no `.planning/plan-approved/*` markers created/edited | ✅ | Plan status string still reads "draft (plan-revision r2 ...; ready for re-review, NOT for approval)". |
| No `status:plan-review` self-promotion in chat or in plan | ✅ | Adversarial Review Summary explicitly preserves "single-author Claude only" provenance and forbids promotion past plan-review until #2555 closes + Codex/Gemini land. |
| No `scripts/review/plan-review-fanout.sh` / `codex` / `gemini` / mutating Hermes invocation | ✅ | None dispatched; Codex/Gemini remain UNAVAILABLE per the prior run. |
| No re-review artifact written in `scripts/review/results/` | ✅ | This lane is a patch lane, not a re-review lane. No file under `scripts/review/results/` was created or modified. |
| Outline file (`docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`) NOT edited | ✅ | Claude r1 finding #5 (demo-path strings) and #2 (proof-counts) are addressed by adding new TDD rows to the plan that will *force* the outline to be corrected at next iteration. The patch lane does not modify the outline body. |
| Single primary result artifact at the prompted path | ✅ | `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2556-20260429-1356.md` written exactly once. |
| Did NOT overwrite other lanes' result files | ✅ | Pre-write `ls` confirmed the target path did not exist. |

---

## Provider coverage statement

Per the autofeed prompt's "provider-coverage honesty" guardrail and per `feedback_permission_gate_blocks_cross_review.md`:

- **Claude (single-author, r1 nextwave + r2 self-revision):** MAJOR (r1, 7 findings, 3 blocking) → resolved in r2 above. r2 itself is a self-revision pass, NOT an additional review lens.
- **Codex:** UNAVAILABLE. Cause: this session's Bash permission gate + upstream codex-cli 0.124.0 stdin-hang regression (#2479). Run `npm install -g @openai/codex@0.123.0` then `scripts/review/plan-review-fanout.sh` from a plain terminal.
- **Gemini:** UNAVAILABLE. Cause: this session's Bash permission gate. Wrapper itself is healthy after the 2026-04-24 `GEMINI_CLI_TRUST_WORKSPACE` fix. A fresh terminal invocation should succeed.

This artifact does **not** claim multi-provider consensus, and does **not** change the plan's adversarial-review provenance. The plan is ready for re-review only.

---

## Lane classification

**Lane:** plan-revision (patch) lane.

**Verdict:** PATCH-APPLIED. The Claude r1 review's three blocking findings (#1 gap-proof factual error, #3 #2555 ordering dependency, #6 duplicate-source disposition) are fully resolved by edits to the plan body, plus four MINOR findings (#2, #4, #5 at plan level, #7) addressed in scope.

**Provider coverage:** UNCHANGED. Codex + Gemini remain UNAVAILABLE; this is single-author plan-revision r2, not a re-review.

**Promotion:** **NONE.** Plan stays at `status:draft`; ready for re-review only after the operator runs the cross-review fanout from an un-sandboxed terminal AND #2555 lands real chart deliverables.

**Files written by this lane (exhaustive, two paths):**
- `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` (11 targeted edits)
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2556-20260429-1356.md` (this artifact)

**Files NOT written by this lane (despite being relevant):**
- `scripts/review/results/*` — patch lane, not re-review lane
- `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` — out-of-scope; new TDD rows force its correction at next iteration
- Any GitHub state — no mutations
- Any tracker / brochure / email / send artifact — out-of-scope per autofeed guardrails
