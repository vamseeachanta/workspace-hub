# Next-wave follow-up — #2554 High-priority count consistency verification (summaryfix r1)

> **Issue.** [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) — vessel contractor outreach matrix.
> **Lane.** Bounded follow-up planning/review/synthesis. Permissions: read + targeted edit on #2554 planning/report artifacts only. No labels mutated, no commits, no pushes, no outreach. No edits to [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555) / [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) / [#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557).
> **Date.** 2026-04-29.
> **Authoring lane.** Claude planning/research worker, ace-linux-1.

---

## Summary (one-paragraph)

The "9-vs-10 High-priority contractor count" inconsistency that the prior next-wave Claude review surfaced as a MINOR finding **is no longer live** in the #2554 artifact set. Between that review and this lane, the owner-approved GoM default added Hornbeck Offshore Services and Edison Chouest Offshore as fully-populated High-priority vessel/operator rows, which lifted the High count from 10 → 12 in the scaffold body and was simultaneously reflected in the lane summary at the time of that addition. The canonical structural gate in plan AC #6 — namely that `grep -cE '\*\*outreach_priority\.\*\* \*\*High\*\*' docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` must equal the integer printed in the scaffold's "Targets in `outreach_priority: High`" Summary Counts bullet AND must equal the count printed in `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` — currently returns **12 = 12 = 12**. AC #6 passes. No source-artifact repair was required, so this lane writes only the verification report at the requested result path and makes no edits to the plan, scaffold, or lane-summary.

---

## Files inspected

| Path | Read for | Read result |
|---|---|---|
| `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` | Plan AC #6 wording, prior adversarial-review row, all `9`/`10` references in count context | Read in full (228 lines) |
| `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` | Per-target `outreach_priority` lines, Summary Counts block, named High list | Read in full (494 lines) |
| `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` | Lane-summary High-count statements (header + acceptance audit + recommended-paste block) | Read in full (83 lines) |
| `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/` (directory listing) | Confirm requested result path does not yet exist; sibling next-wave outputs for context | Confirmed: requested path does not exist; safe to write |

Sibling next-wave artifacts that scope this verification (read for shape/precedent only — not edited):

- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2554-20260429-1446.md` (the plan-only patch lane that added AC #6 and disclosed it had no permission to touch the lane-summary).
- `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2554-20260429-1511.md` (next-wave re-review of #2554).

---

## Verification methodology

The plan AC #6 gate is the canonical truth here, because it is the structural definition the issue's `status:plan-review` promotion path is gated on. Three integers must match:

1. Scaffold per-row count: `grep -cE '\*\*outreach_priority\.\*\* \*\*High\*\*' docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`.
2. Scaffold Summary Counts integer: the bare integer in the bullet beginning `**Targets in `outreach_priority: High`:**`.
3. Lane-summary integer: the count printed in `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` for High-priority targets.

A fourth supporting check (named-list cardinality vs. integer) was added to detect the historical class of bug where the integer and the named list disagreed within the scaffold itself.

### Result table

| Surface | Source line(s) | Integer / cardinality |
|---|---|---|
| Scaffold per-row grep (AC #6 canonical) | scaffold rows matching `\*\*outreach_priority\.\*\* \*\*High\*\*` | **12** |
| Scaffold Summary Counts integer | `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` line 453 ("**Targets in `outreach_priority: High`:** 12") | **12** |
| Scaffold Summary Counts named list | line 453 names: Subsea7, TechnipFMC, Saipem, McDermott, Allseas, Heerema, Boskalis, DOF Group, Sapura Energy, Helix, Hornbeck Offshore Services, Edison Chouest Offshore | **12** |
| Lane summary primary statement | `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md` line 12 ("**12 High-priority targets** are identified ...") | **12** (12 names listed) |
| Lane summary recommended-paste block | same file, line 56 ("12 High-priority targets after owner-approved GoM defaults") | **12** |

### Cross-table agreement

- AC #6 left-hand integer ↔ middle integer: **12 = 12** ✓
- AC #6 middle integer ↔ right-hand integer: **12 = 12** ✓
- Scaffold integer ↔ scaffold named-list cardinality: **12 = 12** ✓ (anti-fabrication: the per-row grep, the integer, and the named list all match)
- Lane summary primary statement ↔ lane summary recommended-paste block: **12 = 12** ✓

### Per-target High mapping (audit trail)

The 12 High-priority rows in the scaffold body, by target heading:

1. Target 1 — Subsea7
2. Target 2 — TechnipFMC (Subsea)
3. Target 3 — Saipem
4. Target 4 — McDermott International
5. Target 5 — Allseas
6. Target 6 — Heerema Marine Contractors
7. Target 7 — Boskalis (Subsea Services)
8. Target 10 — DOF Group (DOF Subsea + Solstad merger)
9. Target 12 — Sapura Energy
10. Target 15 — Helix Energy Solutions
11. Target 23 — Hornbeck Offshore Services
12. Target 24 — Edison Chouest Offshore

Cross-checked against the named list at scaffold line 453 — exact match in name and order. Targets 8 (Van Oord), 9 (DEME), 11 (Bourbon), 13 (Seaway7), 16 (DeepOcean), 17 (Jan De Nul), 19 (Acteon) are correctly excluded (Medium); 14 (Cadeler), 21 (Solstad legacy), 22 (EMAS legacy) correctly excluded (Defer); 18 (Eidesvik), 20 (Otto Candies) correctly excluded (Low).

### Anti-fabrication checks performed

- The per-row grep was run with the exact pattern that AC #6 cites — no pattern relaxation.
- The named-list cardinality was counted from the literal scaffold text, not inferred.
- The lane-summary integer was read from two distinct surfaces (line 12 primary statement and line 56 recommended-paste block); both say 12 and both match the scaffold's 12.
- The Target 21–24 ordering anomaly in the scaffold (rows 23/24 appear before rows 21/22 because the deprecated rows were left as historical anchors) was inspected but does not affect the High count: rows 21 and 22 are both `Defer`, not `High`.

---

## Files changed

**None.** The verification confirmed AC #6 currently passes. No edits to `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`, `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`, or `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md`. No edits to `docs/plans/README.md`. No edits to any sibling-issue artifact.

This is intentional. The plan's adversarial-review summary at line 197 preserves the original 9-vs-10 finding text — that is appropriate audit-trail content for a remediated MINOR finding and rewriting it would erase the evidentiary record of why AC #6 exists. The literal "9" and "10" in AC #6 line 186 are framed as illustrative example numbers ("e.g., scaffold body lists 10 but lane summary still says 9"), not live state, so they remain instructive even after remediation. The narrative on line 208 ("reconciliation of the lane-summary count from 9 → 10") describes prior-lane permission scope and is past-tense, so it does not require updating to reflect the eventual 10 → 12 transition.

---

## Remaining blockers (not addressed by this lane)

The High-priority count gate is clean, but #2554 itself remains `draft` and not yet `status:plan-review`. The remaining blockers, all out of this lane's bounded scope, are:

- **[#2560](https://github.com/vamseeachanta/workspace-hub/issues/2560) — High-priority deep-link / pain-point evidence fill.** 10 of 12 High rows still carry `deep_link_evidence: PENDING` placeholders and `pain_point_evidence: inferred-from-demo-coverage` placeholders. Hornbeck and ECO are the only High rows with verified official fleet/vessels deep-link evidence so far. The matrix cannot feed [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) until #2560 closes or is explicitly waived.
- **[#2561](https://github.com/vamseeachanta/workspace-hub/issues/2561) — FOWT worked example.** Targets 8/9/13/14/17 (Van Oord, DEME, Seaway7, Cadeler, JDN-wind) are gated on the OC4-DeepCwind FOWT mooring screening 1-pager.
- **[#2562](https://github.com/vamseeachanta/workspace-hub/issues/2562) — GoM-niche evidence expansion.** Targets 15/20/23/24 sit in the GoM niche segment; Hornbeck and ECO have basic fleet/vessels evidence but the broader GoM-niche corpus is the lane that hardens this set.
- **Live adversarial review re-run.** The canonical-fanout artifacts at `scripts/review/results/2026-04-29-plan-2554-{claude,codex,gemini}.md` (no `-nextwave` suffix) are still PENDING. AC #5 in the plan requires a live non-Claude review for `status:plan-review` promotion.
- **Codex CLI 0.124.0 stdin-hang.** Per memory `feedback_codex_cli_0_124_upstream_regression.md`, any fanout that includes Codex must downgrade to 0.123.0 first.
- **Gemini sandbox overlay blindness.** Per memory `feedback_gemini_sandbox_overlay_blindness.md`, any Gemini cross-review MAJOR claiming `file does not exist` must be verified locally with `git ls-files` before being accepted.

These blockers are tracked in `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2554-20260429-1511.md` and in [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554)'s body. This lane neither resolves nor extends them.

---

## Next safe action

The user has two next-step options, both still bounded by the planning-research permission envelope this lane uses:

**Option A (recommended) — close #2560 evidence-fill, then run live re-review.**
The High-priority count gate now passes; the remaining MAJOR-class blockers are evidence-fill and live-fanout review. Closing or explicitly waiving [#2560](https://github.com/vamseeachanta/workspace-hub/issues/2560) replaces the 10 outstanding `PENDING` placeholders with verified official fleet/project/vessel deep-link evidence on the 10 non-GoM High targets, after which a live re-review against `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` is the precondition for `status:plan-review` promotion (per AC #5 of the plan).

**Option B — note this verification on #2554 first.**
Recommended issue-comment text (verbatim, ready for the user or a permitted gh-comment lane to paste):

```markdown
Planning/research follow-up (2026-04-29 next-wave summaryfix r1):

- Verified the High-priority count consistency gate (plan AC #6) currently passes:
  - scaffold per-row grep `**outreach_priority.** **High**` → 12
  - scaffold Summary Counts integer → 12 (named list cardinality also 12)
  - lane summary integer → 12 (both primary statement and recommended-paste block)
- The "9 vs 10" mismatch from the prior next-wave Claude review was already remediated by the owner-approved GoM-default lane that added Hornbeck Offshore Services and Edison Chouest Offshore as High rows (10 → 12).
- No source artifacts edited; no labels mutated; no commits.
- Verification artifact: docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2554-summaryfix-20260429-r1.md.

Remaining blockers before status:plan-review: #2560 (deep-link/pain-point evidence fill), #2561 (FOWT worked example), live cross-provider review re-run.
```

**Option C — do nothing.**
The artifact set is already internally consistent on the High-priority count. If the user is comfortable that AC #6 is now passing on the strength of this verification, no immediate action is required other than continuing the evidence-fill work in #2560.

---

## Cross-references

- **Plan:** `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`
- **Scaffold:** `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- **Lane summary:** `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md`
- **Prior plan-only patch lane (added AC #6, disclosed lane-summary scope gap):** `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-patch-2554-20260429-1446.md`
- **Prior next-wave re-review of #2554:** `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-rereview-2554-20260429-1511.md`
- **Original next-wave Claude review row** (now-remediated 9-vs-10 finding text):  plan §"Adversarial Review Summary" line 197.
- **Sibling weekly GTM issues** (NOT touched by this lane): [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555), [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556), [#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557).
- **Memory references applied:** `feedback_inline_gh_issue_url.md` (issue links rendered as Markdown), `feedback_plan_past_tense_artifact_claims.md` (this artifact uses past tense for what was done and explicit "PENDING" or "remaining" for what isn't), `feedback_attestation_enables_contradiction_detection.md` (the verification table is exactly the kind of contradiction-detection surface that prior-lane attestation enables).
