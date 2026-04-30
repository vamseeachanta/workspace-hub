# Plan for #2561: feat(gtm): FOWT mooring screening worked example for wind-contractor outreach

> **Status:** draft (nightly immediate batch 4/5; no implementation or outreach authorized)
> **Complexity:** T2
> **Date:** 2026-04-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2561
> **Review artifacts:** `scripts/review/results/2026-04-30-plan-2561-hermes.md` (created by this batch as local adversarial review); Codex/Gemini review still required before `status:plan-review`.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` — current public matrix scaffold for #2554 with explicit `corporate_root_evidence`, `deep_link_evidence`, and `pain_point_evidence` fields.
- Found: `docs/reports/gtm/assets/vessel-capability-chart-pack-manifest.json` — #2555 chart pack landed after the prior planning wave; downstream brochure work can now consume chart metadata only after its own approval and legal gate.
- Found: `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` — #2556 outline artifact exists, but outbound is blocked by evidence/legal/user-approval gates.
- Gap: no canonical `fowt-mooring-screening-worked-example` artifact exists yet under `docs/reports/gtm/`.

### Standards
Not applicable — GTM/business artifact. Engineering claims must cite existing public demo/method sources and avoid certification-grade claims unless a real standard-backed analysis is produced in a later approved issue.

### LLM Wiki pages consulted
Not required for this planning slice. If implementation uses engineering claims beyond existing GTM demo artifacts, the execution pass must consult relevant marine/offshore wiki pages and cite them explicitly.

### Documents consulted
- Issue #2561 — defines the immediate follow-up scope and acceptance criteria.
- Issue #2554 — parent contractor matrix and current blocker for #2556 send readiness.
- Issue #2555 — chart artifact issue; now CLOSED with `status:done`, providing brochure chart assets but not outbound authorization.
- Issue #2556 — brochure/send tracker issue; remains open and must not send outreach without separate user approval.
- `docs/BUSINESS_BRAIN.md` — legal-sanity gate and current weekly GTM target context.

### Gaps identified
- Missing durable artifact: `docs/reports/gtm/2026-04-30-fowt-mooring-screening-worked-example.md`.
- Missing legal-scan sidecar for the planned artifact.
- Missing cross-provider plan review; this draft is not approval-ready until Codex/Gemini or documented substitutes review the exact plan revision.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-30T03:56:30Z via `gh issue view` during nightly immediate batch 4/5):
- `#2561` — OPEN — feat(gtm): FOWT mooring screening worked example for wind-contractor outreach.
- `#2555` — CLOSED — `feat(gtm): vessel capability charts for contractor brochure` — labels include `status:done`.
- `#2556` — OPEN — `feat(gtm): vessel contractor brochure and outbound send tracker` — no `status:plan-approved` label in the batch inventory.

**File existence** (verified 2026-04-30T03:56:30Z from isolated worktree):
- `docs/reports/gtm/2026-04-30-fowt-mooring-screening-worked-example.md` — MISSING (new — this plan creates or updates)
- `docs/reports/gtm/legal-scans/2026-04-30-fowt-worked-example-scan.json` — MISSING (new — this plan creates or updates)

**Gap proof:** `find docs/reports/gtm -maxdepth 1 -iname '*fowt*'` did not reveal a canonical completed artifact for this issue number; the files named above are planned outputs.

<!-- Source count: issue #2561, #2554, #2555, #2556, BUSINESS_BRAIN, GTM report files. Meets ≥3 requirement. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-30-issue-2561-fowt-mooring-screening-worked-example.md` |
| Primary artifact | `docs/reports/gtm/2026-04-30-fowt-mooring-screening-worked-example.md` |
| Legal scan sidecar | `docs/reports/gtm/legal-scans/2026-04-30-fowt-worked-example-scan.json` |
| Plan review — Hermes/local | `scripts/review/results/2026-04-30-plan-2561-hermes.md` |
| Index update | `docs/plans/README.md` |

---

## Deliverable

A one-page evidence-bounded FOWT mooring screening worked-example artifact that uses a public reference geometry and clearly distinguishes transferable ACE offshore mooring/riser methods from wind-specific gaps.

This issue is explicitly no-outreach: no emails, messages, contact enrichment, calendar actions, send scheduling, or private/prospect routing may be performed in this execution lane.

---

## Pseudocode

```
select and freeze OC4-DeepCwind as the default public reference geometry unless a later plan revision names a specific replacement and explains why
freeze the minimum public geometry package before analysis: exact source document/URL, water depth, floater variant, mooring arrangement, copied parameters vs inferred assumptions, checked_at timestamp
map ACE transferable methods: mooring pretension, excursion envelope, mooring integrity framing, and metocean sensitivity; avoid riser analogies unless explicitly justified as a separate transferable-method note
declare analysis mode explicitly (screening/quasi-static or named method only) and list wind-specific non-claims: IEC 61400-3 DLC execution, aero-servo-elastic coupling, turbine OEM data, certification evidence, lender's engineer sign-off, and site-specific metocean
write one-page proof artifact with a prominent disclaimer block: screening-only, not certification/bankability evidence, not site-specific design; chart/table values only if source-backed
run legal scan and no-proprietary/path leak grep before surfacing for review
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/reports/gtm/2026-04-30-fowt-mooring-screening-worked-example.md` | Primary deliverable / evidence artifact |
| Create | `docs/reports/gtm/legal-scans/2026-04-30-fowt-worked-example-scan.json` | Legal/review/support artifact |
| Update | `docs/plans/README.md` | Add/maintain this plan row. |
| Create | `scripts/review/results/2026-04-30-plan-2561-{claude,codex,gemini}.md` | Required adversarial review artifacts before plan-review. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| public_reference_cited | Worked example cites the frozen public reference geometry/source | OC4-DeepCwind source package | Stable public citation, checked_at timestamp, and copied-vs-inferred parameter table |
| transfer_vs_gap_boundary | Artifact separates transferable offshore methods from wind-specific gaps and states analysis mode | Method table + disclaimer | No claim implies certification-grade, bankability-grade, or coupled aero-hydro-servo-elastic result |
| one_page_gtm_shape | Artifact is usable as brochure proof slot, not a research dump | Markdown report | Headline, method, 3 proof bullets, limitations, next step |
| legal_scan | scripts/legal/legal-sanity-scan.sh --diff-only passes | diff containing proof artifact | exit 0 |

---

## Acceptance Criteria

- [ ] Primary artifact exists at `docs/reports/gtm/2026-04-30-fowt-mooring-screening-worked-example.md` and is public-repo-safe.
- [ ] Every source-backed claim includes a path, official URL, or explicit no-public-proof-found / no-demo-gap boundary.
- [ ] No individual contacts, direct emails, phone numbers, private route details, or send actions are added.
- [ ] Legal scan passes: `scripts/legal/legal-sanity-scan.sh --diff-only`, with structured sidecar output archived; source quotations avoid standards/copyright overuse.
- [ ] Local path/proprietary leak grep passes over changed GTM artifacts.
- [ ] Cross-provider plan review artifacts exist and show no unresolved MAJOR before any `status:plan-review` promotion.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Hermes/local | PENDING | This batch writes the draft and a local review artifact; external Codex/Gemini review is still required. |
| Codex | PENDING | Not run in this batch. |
| Gemini | PENDING | Not run in this batch. |

**Overall result:** DRAFT — local adversarial review returned MAJOR and this r2 patch addresses the findings; still not approval-ready until external review is rerun on this exact revision.

Revisions made based on review:
- Initial nightly immediate batch 4/5 draft created with explicit no-outreach, no-PII, legal-scan, and path/proprietary leak gates.
- r2 locked OC4-DeepCwind as default, required frozen geometry package, sharpened transfer/gap boundaries, removed unjustified riser-overreach, and made screening-only/no-certification disclaimers mandatory after local MAJOR review.

---

## Risks and Open Questions

- **Risk:** If no public geometry is sufficiently clear, deliverable becomes discovery artifact plus recommendation, not invented analysis.
- **Risk:** Wind contractors remain deferred/Medium for outbound until this proof exists and is approved.
- **Risk:** No named prospect/contact routing belongs in this artifact.

---

## Complexity: T2

**T2** — artifact/data plan with multiple evidence gates, but no application code and no authorized outreach.
