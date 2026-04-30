# Lane summary — Issue #2554 (vessel-contractor outreach matrix)

> **Lane.** Claude planning/research worker, ace-linux-1, 2026-04-29.
> **Issue.** [#2554](https://github.com/vamseeachanta/workspace-hub/issues/2554) — feat(gtm): weekly vessel contractor outreach matrix for April target.
> **Permissions assumed.** Planning/research only. No production-code edits, no email sends, no `status:plan-approved` mutation, no autonomous adversarial-review fanout.

---

## What shipped

1. **Canonical plan.** `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` — T2, Resource Intelligence Summary, Pseudocode, Files-to-Change, research-artifact test list, Acceptance Criteria, Risks/Open Questions, and r2 review gate. Status: `blocker-remediation patch applied; pending fresh clean r2 review`.
2. **Research scaffold.** `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` — first artifact under the new `docs/reports/gtm/` directory. After owner approved defaults, the scaffold ranks **24 total rows** and **20 live countable vessel/operator targets** (acceptance criterion bar is ≥20). Each row carries `tier_seed`/`tier_revised`/`segment`/`relevant_fleet`/`demo_anchor`/`pain_point_hypothesis`/`corporate_root_evidence`/`deep_link_evidence`/`pain_point_evidence`/`can_say_now`/`cannot_claim_yet`/`outreach_priority`/`private_route`. **12 High-priority targets** are identified (Subsea7, TechnipFMC, Saipem, McDermott, Allseas, Heerema, Boskalis, DOF Group, Sapura, Helix, Hornbeck Offshore Services, Edison Chouest Offshore), with GoM niche targets High when they map to Demo 3/5 and Gulf access.
3. **Plan Index row.** `docs/plans/README.md` — new row for #2554 inserted ahead of the sibling weekly-GTM rows (#2555, #2556, #2557).
4. **Public/private boundary decision recorded.** Scaffold header explicitly states: corporate-domain evidence URLs only, no individual contact data inline, named contact routing lives outside this repo.

## What is intentionally NOT done

- **Adversarial review wave.** Not run. The lane prompt does not authorize provider fanout, and the `scripts/review/plan-review-fanout.sh` invocation is a separate execution permission. Plan review artifacts at `scripts/review/results/2026-04-29-plan-2554-{claude,codex,gemini}.md` do **not** exist yet.
- **`status:plan-review` label.** Not applied — the prompt is explicit that the label requires both a canonical plan AND adversarial review evidence; we have only the plan.
- **`status:plan-approved` label.** Not applied — explicitly forbidden by the prompt and the planning skill v3.1.0 (no self-approval).
- **Deep-link URL fabrication.** Avoided. Evidence URLs are official corporate-domain roots or official deep links / explicit access-boundary notes. #2560 closed the High-priority evidence-fill lane; remaining Medium/Low/Defer rows stay bounded and no send is authorized.
- **Follow-up issue creation.** Completed after owner approved defaults: [#2560](https://github.com/vamseeachanta/workspace-hub/issues/2560) for High-priority deep-link/pain-point evidence fill, [#2561](https://github.com/vamseeachanta/workspace-hub/issues/2561) for FOWT worked example, and [#2562](https://github.com/vamseeachanta/workspace-hub/issues/2562) for GoM niche evidence expansion.
- **Email send.** Not executed (forbidden by prompt).
- **GitHub issue progress comment on #2554.** Not posted — `gh issue comment` mutation is outside the planning-research lane's scope per the strict-rules block. Recommended comment text is provided below for the user or a follow-on lane to post.

## Acceptance-criterion gap audit

| Acceptance criterion (from #2554 body) | Scaffold status |
|---|---|
| ≥20 ranked contractor / operator targets | **PASS** (24 rows; 20 live countable vessel/operator targets after excluding Acteon partner-shape and deferred/deprecated rows) |
| Each target has public evidence and a reason for outreach fit | **PASS at scaffold-review depth / NOT SEND-READY** — live rows have official corporate roots; High-priority rows have official deep links or explicit access-boundary notes from #2560; Medium/Low rows are bounded and require deeper verification before individualized send copy. |
| Private contact data kept out of public artifacts | **PASS** — header decision + structural absence enforced |
| Follow-up issues created for high-value missing data | **PASS** — [#2560](https://github.com/vamseeachanta/workspace-hub/issues/2560), [#2561](https://github.com/vamseeachanta/workspace-hub/issues/2561), [#2562](https://github.com/vamseeachanta/workspace-hub/issues/2562) opened |

## Blockers

- **Adversarial-review fanout permission.** This lane cannot run `scripts/review/plan-review-fanout.sh`. Need a successor lane (or user-driven invocation) to drive Claude / Codex / Gemini reviews and write artifacts to `scripts/review/results/`. **Note:** memory `feedback_codex_cli_0_124_upstream_regression.md` flags that codex-cli 0.124.0 stdin-hangs on `codex exec`; downgrade to 0.123.0 before any fanout attempt that includes Codex.
- **FOWT worked-example dependency for wind-segment targets.** Targets 8/9/13/14/17 (Van Oord, DEME, Seaway7, Cadeler, JDN-wind) sit at `outreach_priority: Medium` or `Defer` for send-readiness because the OC4-DeepCwind FOWT mooring screening 1-pager (`outreach-candidate-briefs-2026-04-28.md` §4.3) has not been authored. DEME and Seaway7 also have broader offshore contractor/operator evidence, so they remain live-countable but not send-ready; Cadeler remains Defer/non-counted.
- **High-priority evidence-fill.** [#2560](https://github.com/vamseeachanta/workspace-hub/issues/2560) is CLOSED/status:done. Remaining #2554 blocker is clean r2 adversarial review/promotion, not evidence-fill execution.
- **GoM-niche ICP confirmation.** Resolved by owner default approval: GoM targets are High when mapped to Demo 3/5 and Gulf access; broader evidence expansion is tracked in [#2562](https://github.com/vamseeachanta/workspace-hub/issues/2562).

## Exact next action

**Option A (recommended) — evidence-fill, then re-review.**
Rerun live adversarial review against `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md` after the blocker-remediation patch. Apply `status:plan-review` only if no remaining MAJOR findings block promotion.

**Option B — post a progress comment on #2554 first.**
Recommended comment body (verbatim, ready to paste):

```markdown
Planning/research lane progress (2026-04-29):

- Canonical plan landed: docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md (status: draft, T2)
- Research scaffold landed: docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md
- 24 total rows / 20 live countable vessel-operator targets (≥20 required)
- 12 High-priority targets after owner-approved GoM defaults
  - Demo 3 / 4 / 5 mapped per target as proof anchors
  - Public/private boundary: corporate-domain evidence URLs only; no contact data inline
- Plan Index updated: docs/plans/README.md
- Lane summary: docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md

Not yet done (intentionally, per the planning-only lane scope):
- Clean adversarial review wave (Claude/Codex/Gemini or documented working fallback per plan AC) — needed to lift status to plan-review.
- Evidence-fill #2560 is closed; #2561/#2562 remain follow-up enrichment lanes before broader send-readiness. No sends authorized.
- No labels mutated; no emails sent.

Recommended next action: run `scripts/review/plan-review-fanout.sh` against the plan file above, then return for user approval.
```

**Option C — user-confirm scope toggles before review.**
Two open questions in the plan ("GoM-niche priority?" and "wind-segment outreach gating on FOWT worked example?") may prefer a human decision before the adversarial review wave runs, since reviewers will likely flag them.

---

## Cross-references for the next operator

- **Plan:** `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`
- **Scaffold:** `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- **Index row:** `docs/plans/README.md` (#2554 row; line number may drift as README changes)
- **Sibling overnight plans:** [#2555](https://github.com/vamseeachanta/workspace-hub/issues/2555) (capability charts), [#2556](https://github.com/vamseeachanta/workspace-hub/issues/2556) (brochure send-tracker), [#2557](https://github.com/vamseeachanta/workspace-hub/issues/2557) (productivity-flow review) — all `draft` per README rows immediately following #2554.
- **Email-template assumptions:** `docs/strategy/gtm/vessel-installation-contractors/email-templates.md` placeholders (`{{COMPANY}}`, `{{PAIN_POINT_1..3}}`) are designed to consume this matrix's `pain_point_hypothesis` field once it hardens past the v1 hypothesis stage.
- **Memory feedback most relevant:** `feedback_inline_gh_issue_url.md` (issue links rendered as Markdown), `feedback_data_format_guidelines.md` (Markdown for human reading; YAML companion is a possible follow-up), `feedback_codex_cli_0_124_upstream_regression.md` (downgrade Codex CLI before fanout).
