# Next-wave follow-up plan patch — issue #2556 outline demo-path canonicalization (r1)

> **Lane kind:** Plan-patch (write-allowed for #2556 planning artifacts only). NOT an approval lane; NOT an outreach lane; NOT a tracker-content lane.
> **Worker:** Claude (Opus 4.7) interactive autofeed, ace-linux-1 control plane.
> **Date / timestamp:** 2026-04-29 (post-17:12 re-review, autofeed wave).
> **Result artifact (this file):** `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2556-outline-demo-paths-20260429-r1.md`

---

## Summary

The 17:12 cold-context re-review (`nextwave-followup-plan-rereview-2556-file-existence-20260429-1712.md`) explicitly named **"outline body fix (Claude r1 #5)"** as a still-deferred blocker — the brochure outline at `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` §3.4 lines 64–68 still cited demo files by shorthand (`demo_01`, `demo_02`, `demo_03`, `demo_04`, `demo_05`) while the canonical filenames on disk are `demo_01_dnv_freespan_viv.py`, `demo_02_wall_thickness_multicode.py`, `demo_03_deepwater_mudmat_installation.py`, `demo_04_shallow_water_pipelay.py`, and `demo_05_deepwater_rigid_jumper_installation.py`. The plan's `brochure_demo_path_full_filenames` TDD row would have failed at gate time without this fix.

This lane prompt rescoped from the prior 16:49 lane by saying *"Edit only #2556 planning artifacts if needed"* and *"resolve the remaining outline/demo-path shorthand blocker."* That authorizes editing the outline (which self-identifies as `Status: outline (planning artifact)` in its header).

This patch performs three edits, all confined to two #2556 planning artifacts:

1. **Outline §3.4 body fix (5 demo rows + 1 paragraph).** Demo source column now cites canonical `.py` filenames; trailing paragraph documents the file-size verification + cross-reference to the plan's TDD row that enforces this canonical form.
2. **Plan front-matter revision bump.** `r2 → r3` with a one-line note that the outline body fix landed and the dependency-on-#2555 / no-send-legal-gate language is reinforced.
3. **Plan content reinforcement (three blocks).**
   - §Resource Intelligence Evidence: new "Demo / proof path canon" table that enumerates each canonical filename with byte-size + cases-cited and grounds the 1,292-cases sum.
   - §Acceptance Criteria: new "No-send legal gate (explicit, plan-binding)" sub-block that codifies the seven plan-binding constraints in one auditable place — zero outbound sends, legal-sanity scan exit-0, provenance citation rule, public-tracker PII rule, `last_legal_scan_utc` rule, `Depends on: #2555` hard gate, personalization-hook clearance rule.
   - §Adversarial Review Summary: row for finding #5 updated to RESOLVED (with the canonical filenames inline so the resolution is grep-locatable), plus an "r3 delta" sub-block documenting what changed and explicitly stating that provider coverage remains UNCHANGED.

**Result:** the plan is self-consistent at the demo-path layer; reviewers can verify the outline now passes its own TDD gate; the dependency on #2555 and the no-send legal gate are now explicit at the §Acceptance Criteria surface (instead of only implicit via §Risks references). Blockers from the 17:12 re-review (multi-provider consensus UNAVAILABLE, #2555 closure gate, runtime-enforcement follow-up issue, user decisions on brochure formats / tracker write-frequency) all remain in force exactly as before.

This patch does **not** propose `status:plan-review` or `status:plan-approved`. It does **not** flip any GitHub label, comment on any issue, send any outreach, or commit any file. The user remains the gate to advance.

---

## Files inspected (read-only)

- `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` — full plan body (292 lines pre-patch). Confirmed r2 status and the seven Claude r1 finding rows (with #5 still marked "outline body fix is downstream of plan-approval").
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2556-file-existence-20260429-1712.md` — full r5 re-review body (224 lines). Confirmed N1 (file-existence cleanup) RESOLVED + still-deferred outline body fix at lines 64–68 of the outline + §Blockers item 3 ("Outline body fix (Claude r1 #5)").
- `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` — full outline body (174 lines pre-patch). Confirmed §3.4 table at lines 64–68 cited demo paths by shorthand.
- `digitalmodel/examples/demos/gtm/` — directory listing via `ls -la`. Confirmed all 5 canonical filenames exist with byte-sizes 44,438 / 50,067 / 45,472 / 60,376 / 42,881 (Demos 1–5 respectively).
- `git status -s` (post-edit) — confirmed only the two named #2556 planning files plus auto-edit-tracking state files were modified. No edits to brochure source, tracker, email-templates, capability-summary, scripts, or any other surface.

---

## Files changed (write-allowed, scoped to #2556 planning artifacts only)

| Path | Change | Lines touched (approx) |
|---|---|---|
| `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` | §3.4 body fix: shorthand → canonical `.py` filenames + verification footnote paragraph | 14 lines (table 5 rows + footnote rewrite + column-header note) |
| `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` | (a) Front-matter status r2 → r3 + delta note; (b) §Resource Intelligence Evidence new "Demo / proof path canon" block; (c) §Acceptance Criteria new "No-send legal gate (explicit, plan-binding)" sub-block; (d) §Adversarial Review Summary row #5 → RESOLVED + new "r3 delta" sub-block | ~39 lines added/changed across the four named regions |

`git diff --stat` reports: `2 files changed, 44 insertions(+), 9 deletions(-)`.

No other working-tree paths were modified by this lane (excluding `.claude/state/corrections/...` auto-edit-tracking files which are harness-managed). No file was deleted. No file was created besides this result artifact.

---

## Edit-by-edit verification

### Edit 1 — outline §3.4 demo-path canonicalization

Before (lines 64–68):
```
| Demo 1 — freespan / VIV | 680 | `digitalmodel/examples/demos/gtm/demo_01` |
| Demo 2 — wall thickness comparison (API/DNV/PD8010) | 72 | `digitalmodel/examples/demos/gtm/demo_02` |
| Demo 3 — mudmat installation screening | 180 | `digitalmodel/examples/demos/gtm/demo_03` |
| Demo 4 — shallow-water pipelay screening | 60 | `digitalmodel/examples/demos/gtm/demo_04` |
| Demo 5 — rigid jumper installation | 300 | `digitalmodel/examples/demos/gtm/demo_05` |
```

After (lines 64–68):
```
| Demo 1 — freespan / VIV | 680 | `digitalmodel/examples/demos/gtm/demo_01_dnv_freespan_viv.py` |
| Demo 2 — wall thickness comparison (API/DNV/PD8010) | 72 | `digitalmodel/examples/demos/gtm/demo_02_wall_thickness_multicode.py` |
| Demo 3 — mudmat installation screening | 180 | `digitalmodel/examples/demos/gtm/demo_03_deepwater_mudmat_installation.py` |
| Demo 4 — shallow-water pipelay screening | 60 | `digitalmodel/examples/demos/gtm/demo_04_shallow_water_pipelay.py` |
| Demo 5 — rigid jumper installation | 300 | `digitalmodel/examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py` |
```

Plus a footnote paragraph (post-table) restating that filenames resolve on disk with the verified byte-sizes (44,438 / 50,067 / 45,472 / 60,376 / 42,881) and citing the plan's `brochure_demo_path_full_filenames` TDD row as the binding gate. Mentions that `demo_03` has a `demo_03_requirements.md` companion in the same directory but the brochure cites the executable `.py` file (avoids ambiguity for reviewers who might find the requirements file first).

`grep -n "demo_0" docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` post-edit returns exactly the five canonical strings — the shorthand form is fully eliminated.

### Edit 2 — plan front-matter r2 → r3

`Status:` line bumped from r2 to r3 with a single-line delta note describing what r3 changes (outline body fix landed; dependency-on-#2555 + no-send legal gate language reinforced). The "draft / NOT for approval" qualifier is preserved.

### Edit 3a — plan §Resource Intelligence Evidence: Demo / proof path canon block

New table after the existing "Gap proofs" block. Lists each demo (1–5) with canonical filename, byte-size, and cases-cited. Sums to 1,292. Cross-references the `brochure_demo_path_full_filenames` and `brochure_proof_count_provenance` TDD rows. Grounds reviewers without forcing a section-hop.

### Edit 3b — plan §Acceptance Criteria: No-send legal gate (explicit, plan-binding)

New sub-section after the four mapped-to-issue acceptance criteria + the four plan-level acceptance criteria, immediately before §Adversarial Review Summary. Codifies seven constraints in one place:

1. Zero outbound sends from this issue's execution slice.
2. `scripts/legal/legal-sanity-scan.sh --diff-only` exit-0 over brochure-source diff.
3. Every numeric/standards/methodology claim in the brochure cites a repo path or external public source.
4. Public send-tracker file contains zero contact-name / contact-email / contact-phone / LinkedIn-URL fields.
5. No `send_state=SENT` until `last_legal_scan_utc` populated for that row.
6. `Depends on: #2555` is a hard gate; promotion past `status:plan-review` blocked until #2555 ships chart files under `docs/reports/gtm/charts/`.
7. No personalization-hook content from `outreach-candidate-briefs-2026-04-28.md` lands in the public tracker without legal-sanity scan first.

Each constraint references the existing TDD row or risks-block that already encoded it; the new block consolidates rather than duplicating enforcement.

### Edit 3c — plan §Adversarial Review Summary: row #5 RESOLVED + r3 delta sub-block

- Row #5 of the resolution table now reads: r2 added the TDD row; **r3 (this revision):** outline §3.4 body now cites canonical filenames (each named inline so the resolution is grep-locatable); the TDD row's grep check passes against the outline as edited; **Status: RESOLVED.**
- New "r3 delta (2026-04-29 next-wave-autofeed-followup, this revision)" bullet block enumerates the four substantive changes: outline body fix, demo / proof path canon evidence block, no-send legal gate AC block, dependency reinforcement. Closes with "Provider coverage after r3: Still UNCHANGED" and a verbatim list of the still-in-force blockers from the 17:12 re-review.

---

## Plan-binding constraints honored (boundary compliance)

| Guardrail | Status | Evidence |
|---|---|---|
| Edit only #2556 planning artifacts | ✅ | Only `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` and `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` modified. Both self-identify as #2556 planning artifacts. `git status -s` confirms scope. |
| Do not create private tracker content or outreach | ✅ | No `docs/gtm/intake/send-tracker.private.yaml`, `*.private.yaml`, or any tracker row created. No email body, LinkedIn message, or contact-bearing content created. No personalization-hook value lifted from `outreach-candidate-briefs-2026-04-28.md`. |
| Do not run `gh issue edit/comment/close` | ✅ | No `gh` mutation invoked. Lane did NOT inspect issue `updatedAt` (read-only verification was already done by the 17:12 re-review and is preserved unchanged); skipping the read also reduces accidental-mutation risk. |
| Do not apply `status:plan-review` or `status:plan-approved` | ✅ | None applied. Plan front-matter explicitly states "ready for re-review, NOT for approval." This artifact does not propose label flips. |
| Do not write `.planning/plan-approved/*` markers | ✅ | None created or referenced. |
| Do not send outreach | ✅ | None sent. |
| Do not commit or push | ✅ | No `git commit`, `git push`, or `gh pr` invocation. Working tree carries the edits as `M` only; the operator commits at user-approval time. |
| Do not run production implementation | ✅ | No script run, no `digitalmodel` execution, no chart render, no PDF build. |
| Do not overwrite an existing result path | ✅ | Pre-write `ls` confirmed `nextwave-followup-plan-patch-2556-outline-demo-paths-20260429-r1.md` did not exist. Only one path written by this lane. |
| Re-read current files and live context before editing | ✅ | Plan body, outline body, prior re-review artifact, and demo-directory listing all read in the same session before any edit. |
| Keep changes scoped to the named issue/files | ✅ | Both modified files are #2556 planning artifacts; no scope creep into siblings (#2554 / #2555 / #1669 / #2016) or operational surfaces (`scripts/legal/`, `docs/gtm/intake/`, `.gitignore`, `docs/strategy/...`, `docs/gtm/email-outreach-templates.md`, `docs/gtm/capability-summary.md`, `docs/gtm/prospect-demo-sop.md`). |

---

## Remaining blockers (unchanged from 17:12 re-review)

This patch resolves one named blocker (Outline body fix — Claude r1 #5). It does not touch the following, which remain in force:

1. **Multi-provider consensus is still single-author.** Operator must run `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` from an un-sandboxed terminal (after `npm install -g @openai/codex@0.123.0` per [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479)) to land Codex + Gemini artifacts before the `BUSINESS_BRAIN.md` lines 89–97 consensus criterion can be met. Forbidden by this lane.
2. **#2555 closure gate.** `outline_chart_slots_match_2555_artifacts` cannot pass until #2555 lands chart files under `docs/reports/gtm/charts/`. Independently verified absent on disk by 17:12 re-review. Promotion past `status:plan-review` is hard-blocked on this; front-matter `Depends on: #2555` declares the dependency; new no-send legal gate AC block (constraint #6) makes this explicit.
3. **Runtime-enforcement follow-up issue** (tracker-validator script + pre-commit hook + CI check enforcing `send_state` and `last_legal_scan_utc`) must be filed before any human-initiated outbound send executes. Not filed by this lane.
4. **User decisions retained from r1:** brochure output formats (PDF only / HTML only / both) and tracker write-frequency (append-on-event vs batch nightly).
5. **Optional cosmetic carry-forwards from 17:12 re-review:** N2 (line-87 `MISSING (gitignored, NEVER tracked)` is forward-looking — `.gitignore` does not yet contain the matching glob); N3 (line-93 source-count comment arithmetic). Strictly cosmetic; not blocking.

No new MAJOR or MINOR regression introduced by this r3 patch. The deferred user-decision blockers and the multi-provider consensus blocker are the gates to advancement, not anything r3 introduced.

---

## Next safe action (single line, operator gate)

Run a fresh cold-context re-review of the plan post-r3 (recommended path, autofeed lane) — OR run cross-provider review via `bash scripts/review/plan-review-fanout.sh docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` from an un-sandboxed terminal after the codex-cli downgrade per [#2479](https://github.com/vamseeachanta/workspace-hub/issues/2479) (operator-driven path, requires unsandboxed terminal). Either way, the user remains the gate to advance to `status:plan-review` and a separate user decision is the gate to advance to `status:plan-approved`. **Commit the working-tree changes from this lane (`docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` + `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`) as part of the user-approval commit; this lane intentionally did not commit.**

---

## Lane classification

**Lane:** plan-patch (write-allowed for #2556 planning artifacts only).

**Verdict:** patch landed; one named blocker (outline body fix) RESOLVED; plan revision bumped r2 → r3; dependency-on-#2555 + no-send legal gate language reinforced via dedicated §Acceptance Criteria block + §Resource Intelligence Evidence Demo / proof path canon table. Boundary compliance verified across all eleven guardrails. No new regression. Plan stays at `status:draft`.

**Provider coverage:** UNCHANGED. Codex + Gemini remain UNAVAILABLE; this is a single-author Claude patch.

**Promotion:** **NONE.** Plan stays at `status:draft`. The user remains the gate to advance. r3 explicitly does NOT propose, apply, or pre-authorize any GitHub label change, plan-approved marker, fanout dispatch, implementation, outreach, or edits to other artifacts. Downstream patch lanes / rereview lanes / autofeed orchestration are not pre-authorized to flip any status from this verdict.

**Files written by this lane (exhaustive — three paths):**
- `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md` — modified (plan revision r3)
- `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` — modified (outline §3.4 body fix)
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2556-outline-demo-paths-20260429-r1.md` — this result artifact

**Final lane classification:** plan-patch — narrow-scope outline body fix + plan reinforcement for issue #2556. Resolves the still-deferred Claude r1 finding #5 named in the 17:12 re-review's §Blockers item 3, and makes the dependency-on-#2555 + no-send legal gate language explicit at the §Acceptance Criteria surface. User review remains the next gate.
