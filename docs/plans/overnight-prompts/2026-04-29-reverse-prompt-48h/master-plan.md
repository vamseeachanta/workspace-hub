# Reverse-prompt 48-hour execution packet — GTM vessel contractor wave

> Date: 2026-04-29
> Parent: [#2016](https://github.com/vamseeachanta/workspace-hub/issues/2016)
> Child issues: [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554), [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555), [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556), [#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557)
> Purpose: turn Business Brain + current work into a concrete 48-hour agent execution queue.

## Reverse-prompt synthesis

The Business Brain says ACE Engineer's current bottleneck is not AI credits; it is harness/approval/execution throughput that creates client-facing artifacts. The highest-value path is therefore:

```text
contractor matrix (#2554) → capability charts (#2555) → brochure/send tracker (#2556) → outbound approval path (#2016/#1669)
```

[#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557) runs in parallel only where it reduces owner orchestration or unblocks provider review. It must not distract from the GTM artifact chain.

## Current state verified

| Issue | Current state | Review state | Best next action |
|---|---|---|---|
| #2554 contractor matrix | Plan + 22-target scaffold exist | Claude MINOR; Codex/Gemini unavailable | Patch MINOR findings, get at least Gemini or Codex review, then promote to `status:plan-review` if clean |
| #2555 capability charts | Plan + 4-chart storyboard exist | Claude MINOR; Codex/Gemini unavailable | Patch MINOR findings, clarify chart rendering home, get provider review, then promote to `status:plan-review` if clean |
| #2556 brochure/send tracker | Plan + outline + schema exist | Claude MAJOR; Codex/Gemini unavailable | Do not promote. Fix factual/ordering blockers after #2554/#2555 review progresses |
| #2557 productivity hacks | Plan + report exist | Claude MAJOR; Codex/Gemini unavailable | Do not promote. Refresh stale live numbers and scope H1/H2/H4 as issue comments/follow-ups only |

## 48-hour execution lanes

### Lane A — #2554 review-readiness patch

- **Agent:** Claude/Codex worker or Hermes direct patch lane.
- **Allowed paths:**
  - `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`
  - `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
  - `scripts/review/results/2026-04-29-plan-2554-*` only if running review.
- **Objective:** resolve Claude MINOR findings: heading grep mismatch, High-priority count inconsistency, AC wording for provider unavailable fallback, deep-link vs corporate-root evidence distinction, pain-point evidence slot.
- **Stop condition:** #2554 is ready for real provider review, not necessarily approved.

### Lane B — #2555 review-readiness patch

- **Agent:** Claude/Codex worker or Hermes direct patch lane.
- **Allowed paths:**
  - `docs/plans/2026-04-29-issue-2555-vessel-capability-charts.md`
  - `docs/reports/gtm/2026-04-29-vessel-capability-chart-storyboard.md`
  - `scripts/review/results/2026-04-29-plan-2555-*` only if running review.
- **Objective:** resolve Claude MINOR findings: provider-review AC, exact chart-rendering entry point outside `digitalmodel/` source edits, PNG/SVG/PDF asset home, headline-number verification scope.
- **Stop condition:** #2555 is ready for real provider review and later user approval.

### Lane C — #2556 dependency-aware blocker repair

- **Agent:** Claude planner after Lane A/B patch artifacts exist.
- **Allowed paths:**
  - `docs/plans/2026-04-29-issue-2556-vessel-contractor-brochure-send-tracker.md`
  - `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md`
  - `docs/reports/gtm/2026-04-29-vessel-contractor-send-tracker-schema.md`
- **Objective:** fix Claude MAJOR blockers without pretending dependencies are complete: acknowledge existing `vessel-installation-contractors/email-templates.md`, declare disposition/ownership, make brochure chart-slot checks explicitly dependent on #2555 execution artifacts.
- **Stop condition:** MAJOR findings are patched or converted into explicit dependency blockers; no send/email execution.

### Lane D — #2557 productivity refresh / decision support

- **Agent:** Hermes or Claude planning lane with live source reads.
- **Allowed paths:**
  - `docs/plans/2026-04-29-issue-2557-weekly-productivity-flow-hacks.md`
  - `docs/reports/2026-04-29-weekly-productivity-flow-hacks.md`
  - generated comments under `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/generated/`
- **Objective:** refresh stale provider/work-queue numbers from live files and narrow H1/H2/H4 into comments on existing issues (#2479/#2519) rather than creating duplicate issues.
- **Stop condition:** productivity report is truthful enough to guide queue draining; it does not block GTM artifact work.

## Provider/review path

Preferred order:

1. Patch #2554 and #2555 MINOR findings first.
2. Run Gemini review first if Codex CLI remains unreliable.
3. Run Codex review from a plain terminal only after confirming the #2479 CLI regression workaround/pin.
4. Promote to `status:plan-review` only when current plan contract is satisfied by valid reviews, or when the plan explicitly documents a permitted provider-unavailable fallback.
5. Never apply `status:plan-approved` without the user's explicit approval.

## Owner decisions needed

1. **GoM-niche priority:** Are Helix / Otto Candies / GoM-focused operators first-wave targets or second-wave?
2. **Wind/FOWT gating:** Should wind-segment targets wait for a FOWT worked example before outreach?
3. **Chart asset home:** default recommendation is `docs/reports/gtm/assets/` for brochure assets; avoid editing `digitalmodel/` until a plan-approved execution slice says otherwise.
4. **Brochure send authority:** no outbound send happens until user explicitly approves channel/account and target list.

## Verification checklist before any external outreach

- [ ] #2554 target matrix has no private contact data and each high-priority target has evidence sufficient for the claim level.
- [ ] #2555 chart assets are rendered, recomputable, and have evidence/assumption notes.
- [ ] #2556 brochure references only evidence-backed claims and has legal/evidence sanity review complete.
- [ ] Send tracker separates public artifact paths from private contacts.
- [ ] User has explicitly approved actual send channel and batch.

## Recommended next command sequence

Run Lane A and Lane B first. Only after both are patched should Lane C prepare a brochure review fix. Lane D can run in parallel, but should be time-boxed so it does not consume GTM execution time.

