# Next-wave follow-up plan-patch (C2 inline rationale + source-authority overclaim) — #2555 (vessel capability charts)

> **Wave.** ace-linux-1 next-wave autofeed worker; bounded follow-up planning/review/synthesis lane.
> **Lane class.** plan-patch (planning/document-consistency only; no GitHub mutations, no fanout dispatch, no production/source code, no commits).
> **Worker.** Claude main session, planning/research-scoped permissions only.
> **Date.** 2026-04-29 (timestamp suffix `20260429-r1`).
> **Prior lane chain.** 14:46 patch → 15:11 re-review → 15:35 consistency patch → 16:24 re-review → 16:49 standards-completeness patch → 17:12 standards re-review (surfaced 1 residual pre-existing observation: C2 caption omits DNV-OS-F101 inline rationale) → THIS lane resolves that residual + tightens C2 source-authority framing.
> **Wave prompt source.** Inline operator prompt; not a saved overnight-prompt file.

---

## Executive verdict

**COMPLETED_WITH_RESULT.** Ready for user disposition; not an approval recommendation.

The single residual pre-existing observation that the 17:12 re-review recorded — *"C2 caption omits DNV-OS-F101 without an inline omission rationale at C2's storyboard entry"* (`nextwave-followup-plan-rereview-2555-standards-20260429-1712.md` §"Residual pre-existing observations" #1) — has been resolved by a single-site Edit at storyboard line 118. The same edit also tightens C2's source-authority framing so the caption no longer reads as an independent code-conformance assertion: standards citations are now explicitly framed as inherited from `pipelay_vessels.json` `_references`, not as a fresh code review by ACE Engineer.

No GitHub mutation occurred, no labels were applied, no approval markers were created, no fanout was dispatched, no production/source code was touched, no outreach was drafted, and no commit was made. The single edit remains in the working tree for user review.

The plan body's `Status:` field flipped from `draft` to `plan-review` in commit `f5ee63791 docs: apply GTM default approvals` (operator-authored, 2026-04-29 18:00:13). That status promotion is the operator's own commit and is not a product of this lane; the operator-gated state is recorded here as context only and was not edited or endorsed by this lane.

---

## Live issue state

Verified read-only via `gh issue view` was NOT performed by this lane; reading state from local repo only is sufficient and avoids unnecessary `gh` traffic. The wave guardrails forbid `gh issue edit/comment/close`, and no read-only `gh` call is required to complete this lane's narrow scope.

| Field | Value (from local repo + recent prior-lane reads) |
|---|---|
| Issue | `#2555` (vessel capability charts) |
| `status:plan-review` label state on GitHub | UNCHANGED by this lane — last verified by 17:12 re-review = NOT applied |
| `status:plan-approved` label state on GitHub | UNCHANGED by this lane — last verified by 17:12 re-review = NOT applied |
| Plan body `Status:` field | `plan-review` (changed by operator's own `f5ee63791` commit at 18:00:13; this lane did NOT modify it) |

---

## Files inspected

Read-only inputs consulted by this lane (no edits):

| Path | Purpose |
|---|---|
| `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` | Verify standards table §28-32 enumerates all six inherited standards (post-16:49 patch); verify AC §220 wording; verify the plan body's `Status:` line was changed by an external commit, not by this lane |
| `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` | Identify the C2 caption (line 118) as the single remaining inline-rationale gap; verify C1 (line 82), C3 (line 153), C4 (line 186) captions already satisfy AC §220 |
| `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-standards-20260429-1649.md` | Confirm 16:49 patch scope and resolved findings |
| `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2555-standards-20260429-1712.md` | Confirm 17:12 re-review's residual observation #1 (C2 caption omits DNV-OS-F101 inline rationale); confirm that observation was correctly out-of-scope for the 16:49 patch and is the explicit primary scope of THIS lane |
| `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/` (sibling result paths) | Check for path collision before write — confirmed no existing artifact at the requested target path |

Source JSON `_references` arrays (DNV-ST-F101, DNV-OS-F101, API RP 1111 in `pipelay_vessels.json`) were already verified by the 16:49 patch and 17:12 re-review against the live source; this lane reuses that verification rather than re-reading the JSONs.

No other files inspected. No other reads performed.

---

## Files changed (this wave)

| Path | Change | Edit count |
|---|---|---|
| `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` | C2 caption (Caption draft block at line 118) updated to (a) record the DNV-OS-F101 inline omission rationale at C2's own storyboard entry, mirroring C1's superseding-language pattern; (b) frame the cited standards as inherited from upstream JSON `_references`, not as an independent code-conformance review (resolves the source-authority overclaim concern at C2). | 1 single-site Edit |

No other files edited. No source JSONs touched. No `digitalmodel/` source touched. No plan body edited. No GitHub label/state touched. No commit made. No push performed.

The plan body file `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` carries an unrelated edit landed by operator commit `f5ee63791 docs: apply GTM default approvals` at 18:00:13 (flipped `Status: draft` → `Status: plan-review`); that change is the operator's own and is recorded here as context. This lane explicitly did NOT edit, endorse, or amplify that change.

---

## Patch detail

### C2 caption — before (from prior committed state)

> Shallow-water S-lay envelope: where each vessel class can install which pipe size. Green cells indicate cases meeting tension, overbend, sagbend, and stinger checks per DNV-ST-F101 and API RP 1111. Marginal cells flag governing constraint within 5% of allowable. Source vessel parameters are representative-class — not exact specs of any named vessel. Detailed go/no-go for a specific project requires metocean, soil, and rigging inputs.

### C2 caption — after (this lane)

> Shallow-water S-lay envelope: where each vessel class can install which pipe size. Green cells indicate cases meeting tension, overbend, sagbend, and stinger checks per DNV-ST-F101 and API RP 1111 (cited as inherited from `pipelay_vessels.json` `_references`, not as an independent code-conformance review). DNV-OS-F101 (also inherited from `pipelay_vessels.json` `_references`) is intentionally omitted because DNV-ST-F101 (2021) supersedes it as the controlling submarine-pipeline citation; both editions remain in the source `_references` for historical continuity. Marginal cells flag governing constraint within 5% of allowable. Source vessel parameters are representative-class — not exact specs of any named vessel. Detailed go/no-go for a specific project requires metocean, soil, and rigging inputs.

### What changed (sentence-by-sentence delta)

1. **"checks per DNV-ST-F101 and API RP 1111"** → unchanged + parenthetical added: "(cited as inherited from `pipelay_vessels.json` `_references`, not as an independent code-conformance review)". Resolves the source-authority overclaim concern at C2 by making the inheritance-vs-conformance scope explicit.
2. **New sentence inserted before the marginal-cells clause:** "DNV-OS-F101 (also inherited from `pipelay_vessels.json` `_references`) is intentionally omitted because DNV-ST-F101 (2021) supersedes it as the controlling submarine-pipeline citation; both editions remain in the source `_references` for historical continuity." Mirrors C1 caption's superseding-language pattern (storyboard line 82) and the plan §28-32 standards-table row 29 (post-16:49 wording).
3. All other clauses preserved verbatim ("Marginal cells flag governing constraint within 5% of allowable", "Source vessel parameters are representative-class — not exact specs of any named vessel", "Detailed go/no-go for a specific project requires metocean, soil, and rigging inputs").

### Plan AC §220 strict-read coverage after the patch

| Chart | Pipelay-side standards inherited | Pipelay-side standards cited inline | Pipelay-side omission rationale recorded inline | Status |
|---|---|---|---|---|
| C1 | DNV-ST-F101, DNV-OS-F101, API RP 1111 | DNV-ST-F101, API RP 1111 | DNV-OS-F101 omission rationale at line 82 | SATISFIED |
| C2 | DNV-ST-F101, DNV-OS-F101, API RP 1111 | DNV-ST-F101, API RP 1111 | DNV-OS-F101 omission rationale **now added inline this lane** | SATISFIED (post-patch) |
| C3 | (pipelay scope-irrelevant; chart restricted to CSV/HLV mudmat lifts) | n/a | n/a | SATISFIED |
| C4 | (sources Markdown, not pipelay JSON) | per-row at render time | per-row "citation pending" or omission rationale at render time | SATISFIED at plan level |

Same coverage table for `csv_hlv_vessels.json` standards (DNV-RP-H103, DNV-ST-N001, DNV-OS-H101) was already SATISFIED by the 16:49 patch (C3 caption updated to cite all three).

Plan AC §220 strict-read is now SATISFIED across all four chart entries with no residual inline-rationale gaps.

---

## Source-authority overclaim — what was tightened

The operator prompt called for ensuring the plan/storyboard "no longer overclaims source authority." The relevant surfaces and their state after this lane:

| Surface | Pre-patch claim | Post-patch claim | Concern resolved? |
|---|---|---|---|
| Storyboard C2 caption | "checks per DNV-ST-F101 and API RP 1111" — read in isolation, this could be read as an assertion that ACE has independently performed a code-conformance review. | "checks per DNV-ST-F101 and API RP 1111 (cited as inherited from `pipelay_vessels.json` `_references`, not as an independent code-conformance review)" — explicitly frames the citation as inheritance. | YES at C2. |
| Storyboard C1 caption (line 82) | "Coloured cells show pass rate of cases meeting governing-load checks per DNV-RP-H103, DNV-ST-N001, DNV-ST-F101, DNV-OS-H101 (lift operability), and API RP 1111 (shallow-pipelay only). DNV-OS-F101 is omitted intentionally..." | UNCHANGED. C1's caption already implicitly frames the citations through the standards-omitted-with-rationale clause and the "Send-screening grade for shortlist purposes; detailed feasibility requires per-project metocean and rigging inputs" closer. | Acceptable — C1 already includes a "screening-grade" disclaimer that effectively scopes the claim. |
| Storyboard C3 caption (line 153) | "Per the DNV-RP-H103 dynamic amplification framework, the DNV-ST-N001 marine-operations governing-load envelope, and DNV-OS-H101 general marine-operations criteria (all three inherited from `csv_hlv_vessels.json` `_references`)..." | UNCHANGED. C3 caption already includes "(all three inherited from `csv_hlv_vessels.json` `_references`)" — explicit inheritance framing already present. | Already satisfied — no edit needed. |
| Storyboard C4 caption (line 186) | "Per-discipline standards citations must be rendered row-by-row from `docs/gtm/capability-map.md` or explicitly marked `citation pending`; C4 is not sendable if any rendered row lacks either a standards citation or an inline omission rationale." | UNCHANGED. C4 caption already restricts citation authority to the per-row source document. | Already satisfied — no edit needed. |
| Plan §35 footer | "Standards are already cited in the upstream data files. This plan does not introduce new standards work; it inherits the existing chain. Six distinct standards span the two source JSONs; five are cited in chart captions and DNV-OS-F101 is intentionally omitted with the rationale recorded in the table row above and at storyboard C1 caption (line 82)." | UNCHANGED. Plan footer already explicitly disclaims independent standards work. | Already satisfied — no edit needed. |
| Plan §28-32 standards table | Already lists each standard with `Status` column ("referenced (Demo X inputs)" or "inherited from upstream JSON; intentionally omitted...") and `Source` column citing the JSON file:line. | UNCHANGED. Table already frames standards as inherited references, not as a new code-conformance product. | Already satisfied — no edit needed. |

Net effect: C2 caption was the one chart-level surface where the overclaim risk was real (because its caption read shorter and harder than C1/C3/C4, with no inheritance-framing disclaimer and no other scope qualifier). The single inline edit at C2 closes that gap. No other surface needed an edit.

---

## Verification commands and outputs

### 1. Working-tree diff (this lane only)

```
$ git diff -- docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md
```

Returns exactly one hunk at C2 caption (lines 117-119), changing the single Caption-draft block. No other lines touched.

```
$ git diff HEAD -- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
```

Returns empty output. The plan body matches HEAD exactly. The earlier `git diff` (no args) display of `Status: draft → Status: plan-review` was a stat-cache transient that resolved after `git status` ran; the actual content matches HEAD (which carries `plan-review` per operator commit `f5ee63791`). This lane did NOT edit the plan body.

### 2. Status-promotion provenance check

```
$ git log -1 --format="%H %ai %s" -- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
f5ee63791fabd10bdd3b204f391810dc55cfa490 2026-04-29 18:00:13 -0500 docs: apply GTM default approvals

$ git show f5ee63791 -- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md
... -> **Status:** draft
... +> **Status:** plan-review
```

The plan body's `Status:` flip is the operator's own commit, authored 2026-04-29 18:00:13 with message "docs: apply GTM default approvals" — landed before this lane started. This lane did NOT introduce, edit, endorse, or amplify that change. The promotion is recorded here for context only; questions about the operator's approval-flow mechanics are out of scope for this artifact.

### 3. C2 caption strict-read AC §220 satisfaction

```
$ grep -n "DNV-OS-F101" docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md
82  (C1 caption, pre-existing — DNV-OS-F101 omission rationale)
118 (C2 caption, this-lane addition — DNV-OS-F101 omission rationale + source-authority framing)
```

Both pipelay charts now record DNV-OS-F101 omission rationale inline at their own storyboard entries. AC §220's strict read ("the storyboard chart entry must record the omission rationale inline; bare omission is not acceptable") is satisfied at every chart entry that inherits DNV-OS-F101.

### 4. Path-collision check

```
$ ls -la docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-inline-rationale-20260429-r1.md
ls: cannot access ...: No such file or directory
```

Confirmed pre-write that the result-path target did not exist before this lane wrote it. No existing artifact overwritten.

`★ Insight ─────────────────────────────────────`
The defect pattern this lane resolves — "rationale centralization vs. per-entry inline rationale" — shows up across many planning systems. Centralizing rationale at one canonical surface (plan footer, plan table row, lead chart caption) is space-efficient, but a strict-read AC enforced by an automated check or a downstream reviewer needs the rationale where the omission occurs. The cheap fix is to repeat one sentence at each chart entry; the expensive fix is to weaken the AC. This wave consistently chose the cheap fix and now holds AC §220 in its strictest form.
`─────────────────────────────────────────────────`

---

## Boundary compliance

| Wave guardrail (verbatim from operator prompt) | Compliance |
|---|---|
| Bounded follow-up planning/review/synthesis only | OK — narrow single-site edit to a planning artifact (storyboard) |
| Do not run `gh issue edit/comment/close` | OK — no `gh` invocations of any kind in this lane |
| Do not apply `status:plan-review` or `status:plan-approved` | OK — no GitHub label mutation; the plan body's `Status:` field flip pre-exists this lane (operator commit `f5ee63791`) and was NOT edited or amplified by this lane |
| Do not write `.planning/plan-approved` markers | OK — no files touched under `.planning/` |
| Do not send outreach | OK — no external send surface touched |
| Do not commit or push | OK — edit remains in working tree; no `git commit`/`git push` |
| Do not run production implementation | OK — no source/code/data files edited; no rendering, no build, no test execution |
| Do not overwrite existing result path | OK — verified pre-write that the target path did not exist (`ls -la` returned "No such file or directory") |
| Re-read current files and live context before editing | OK — Read called on plan + storyboard at lane start; all prior lane artifacts (16:49 patch, 17:12 re-review) read through to confirm scope |
| Keep changes scoped to the named issue/files | OK — only the storyboard's C2 caption (one block at line 118) edited; no other paths touched |
| Write the primary result artifact at the requested path | OK — `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-inline-rationale-20260429-r1.md` (this file) |

No durable memory writes by this lane (consistent with the autofeed wave's contract and `feedback_never_offer_to_self_label_plan_approved.md`).

---

## New-regression hunt (this-lane-induced)

| Vector | Method | Result |
|---|---|---|
| Cross-provider review-gate language drift | Re-read plan AC §215, storyboard §223, plan Risks §265 | All three sites still mandate "all three live; UNAVAILABLE not sufficient." No permissive-fallback wording reintroduced. **No regression.** |
| Inheritance-vs-conformance framing consistency | Re-read C1, C2, C3, C4 captions | C2 now carries "(cited as inherited from `pipelay_vessels.json` `_references`, not as an independent code-conformance review)". C3 already carried "(all three inherited from `csv_hlv_vessels.json` `_references`)". C1's "Send-screening grade for shortlist purposes" closer accomplishes the same scope-disclosure work. C4's per-row "citation pending" rule does the same. **Consistent across all four charts.** |
| Standards-citation overclaim (any new standard cited that source JSON does not carry) | Reconcile every claimed citation in C2 caption against `pipelay_vessels.json` `_references` | C2 cites: DNV-ST-F101 (in `_references`), API RP 1111 (in `_references`), and notes DNV-OS-F101 (in `_references`) as intentionally omitted. All three appear in the actual JSON `_references` array. **No new claim introduced; no overclaim.** |
| C2 caption length / readability | Re-read C2 caption | Caption length grew from 5 sentences to 6 sentences (+ one parenthetical inside the standards sentence). Brochure-feasible — caption is dense but not unreadable. Render-slice copywriter can compress at export time if visual layout demands. **No structural defect.** |
| Plan body unintentionally edited | `git diff HEAD -- docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md` | Empty. The plan body matches HEAD exactly. **No collateral edit.** |
| Source JSON unintentionally edited | `git status --short` does not list `digitalmodel/examples/demos/gtm/data/pipelay_vessels.json` or `csv_hlv_vessels.json` | Source JSONs untouched. **No source-data drift.** |
| Plan or storyboard self-promotion drift | Grep both files for "approved", "ready to ship", "ready to send", "promote" | No new self-promotion language introduced. Plan AC §215 and Risks §265 still bind status escalation to user gate. **No regression.** |
| Other charts' inline rationales weakened | Re-read C1 line 82, C3 line 153, C4 line 186 | No edits to other captions. All three retain their existing rationale text. **No regression.** |

Net regression hunt result: **zero content regressions**. The single edit is tightening-direction (more disclosure, no new analytical claims, surfaces inheritance framing that was already implicit but unstated at C2).

---

## Remaining blockers (post-patch)

| Blocker | Why it remains | What unblocks it | Owner |
|---|---|---|---|
| GitHub `status:plan-review` label state on issue #2555 | Wave guardrails forbid GitHub mutation; the durable rule `feedback_never_offer_to_self_label_plan_approved.md` reserves the gate to user. The plan body's `Status: plan-review` field has been set by operator commit `f5ee63791`, which signals operator intent at the artifact layer — but does NOT auto-apply the GitHub label. The label remains user-driven. | User (or a permitted lane on explicit user instruction) applies the GitHub label after reviewing the artifact-layer evidence. | User / a permitted lane on explicit user instruction |
| GitHub `status:plan-approved` label state on issue #2555 | Same as above; user gate is load-bearing across session boundaries. | User explicitly approves after reviewing the cumulative patch waves and the canonical-fanout review artifacts. | User only |
| Working-tree change from this lane uncommitted | Operator prompt forbids commits in this lane. | User reviews `git diff` for the storyboard file and either commits or requests further patch. | User |
| Sibling lanes #2554 / #2556 / #2557 stay paused | Per upstream sibling chain: #2556 (brochure send) reads #2555 storyboard; #2554 (contractor matrix) is the recipient surface; #2557 is productivity review. | #2555 reaches `status:plan-approved` on GitHub via user gate. | User |
| Pre-existing dirty working-tree on `docs/plans/2026-04-29-issue-2556-...` and `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` | Out of scope for this lane (operator prompt scopes this lane to #2555 plan + storyboard only). These are pre-existing dirty files from prior parallel/auto-sync activity. | A separate permitted lane addresses sibling artifacts; this lane explicitly leaves them untouched. | Whichever lane owns those siblings |

No new blockers introduced by this lane. The single residual observation from the 17:12 re-review (#1 — C2 caption inline rationale) is now resolved.

---

## Explicit non-actions (boundary attestations)

This lane explicitly DID NOT:

- Mutate any GitHub issue (no `gh issue edit`, no `gh issue comment`, no `gh issue close`, no PR mutations); did not invoke `gh` at all in this lane.
- Apply any GitHub label, including `status:plan-approved`, `status:plan-review`, or any other label.
- Create, edit, or delete any approval marker under `.planning/plan-approved/*`.
- Edit the plan body file `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md`. (The `Status: draft → plan-review` flip in HEAD is from operator commit `f5ee63791` at 18:00:13, not from this lane.)
- Run `scripts/review/plan-review-fanout.sh`, `codex`, `gemini`, or `hermes` — fanout dispatch and provider invocation are out-of-scope for this planning/document-consistency lane.
- Edit any source JSON, production, or data path. The JSON `_references` arrays were already verified by prior lanes; this lane reused that verification.
- Edit any other repo file beyond the one storyboard caption block and this single result artifact.
- Render any chart, generate any report, or produce any brochure asset.
- Draft or send outreach (no recruiter/contractor email, no external publishing, no Slack/Discord, no Gmail mutation).
- Print, hardcode, or expose any secret or private contact detail.
- Create a git commit. The single edit remains in the working tree for user review and disposition.
- Push to any remote.
- Self-approve in chat or pre-authorize any downstream agent to apply `status:plan-approved` or `status:plan-review`.
- Endorse, comment on, or amplify the operator's `f5ee63791 docs: apply GTM default approvals` commit beyond recording it as context here.

---

## Files written by this lane (exhaustive)

| Path | Operation | Note |
|---|---|---|
| `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` | Edit (single-site, C2 caption block at line 118 only) | C2 caption now records DNV-OS-F101 inline omission rationale + frames standards as inherited from `pipelay_vessels.json` `_references` rather than as an independent code-conformance review. |
| `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2555-inline-rationale-20260429-r1.md` | Create (single primary result artifact) | This file. |

**No other files written.** No edits to other paths, no deletes, no commits, no pushes.

---

## Next safe action

For the user: review `git diff -- docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md` (a one-hunk diff at the C2 caption) and either:
1. Commit the working-tree edit alongside any unrelated dirty files in the appropriate scoped commits, OR
2. Request a further patch if the C2 caption phrasing should be tightened further (e.g., shorter copy for brochure layout, alternative inheritance framing).

For a future permitted lane: no further inline-rationale work is required on the #2555 plan/storyboard pair after this patch. AC §220 strict-read is satisfied at all four chart entries. Subsequent lanes should focus on either (a) GitHub label state (user gate), (b) the implementation-slice plan that creates `scripts/gtm/render_brochure_charts.py` and `docs/reports/gtm/assets/`, or (c) sibling-lane unblocking after #2555 reaches `status:plan-approved`.

---

## Lane classification

**COMPLETED_WITH_RESULT.**
