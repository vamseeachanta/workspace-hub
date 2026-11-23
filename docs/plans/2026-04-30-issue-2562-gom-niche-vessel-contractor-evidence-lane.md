# Plan for #2562: DATA(gtm): expand GoM niche vessel-contractor evidence lane

> **Status:** draft (nightly immediate batch 4/5; no implementation or outreach authorized)
> **Complexity:** T2
> **Date:** 2026-04-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2562
> **Review artifacts:** `scripts/review/results/2026-04-30-plan-2562-hermes.md` (created by this batch as local adversarial review); Codex/Gemini review still required before `status:plan-review`.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` — current public matrix scaffold for #2554 with explicit `corporate_root_evidence`, `deep_link_evidence`, and `pain_point_evidence` fields.
- Found: `docs/reports/gtm/assets/vessel-capability-chart-pack-manifest.json` — #2555 chart pack landed after the prior planning wave; downstream brochure work can now consume chart metadata only after its own approval and legal gate.
- Found: `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` — #2556 outline artifact exists, but outbound is blocked by evidence/legal/user-approval gates.
- Gap: no canonical `gom-niche-vessel-contractor-evidence-lane` artifact exists yet under `docs/reports/gtm/`.

### Standards
Not applicable — GTM/business artifact. Engineering claims must cite existing public demo/method sources and avoid certification-grade claims unless a real standard-backed analysis is produced in a later approved issue.

### LLM Wiki pages consulted
Not required for this planning slice. If implementation uses engineering claims beyond existing GTM demo artifacts, the execution pass must consult relevant marine/offshore wiki pages and cite them explicitly.

### Documents consulted
- Issue #2562 — defines the immediate follow-up scope and acceptance criteria.
- Issue #2554 — parent contractor matrix and current blocker for #2556 send readiness.
- Issue #2555 — chart artifact issue; now CLOSED with `status:done`, providing brochure chart assets but not outbound authorization.
- Issue #2556 — brochure/send tracker issue; remains open and must not send outreach without separate user approval.
- `docs/BUSINESS_BRAIN.md` — legal-sanity gate and current weekly GTM target context.

### Gaps identified
- Missing durable artifact: `docs/reports/gtm/2026-04-30-gom-niche-vessel-contractor-evidence-lane.md`.
- Missing legal-scan sidecar for the planned artifact.
- Missing cross-provider plan review; this draft is not approval-ready until Codex/Gemini or documented substitutes review the exact plan revision.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-30T03:56:30Z via `gh issue view` during nightly immediate batch 4/5):
- `#2562` — OPEN — DATA(gtm): expand GoM niche vessel-contractor evidence lane.
- `#2555` — CLOSED — `feat(gtm): vessel capability charts for contractor brochure` — labels include `status:done`.
- `#2556` — OPEN — `feat(gtm): vessel contractor brochure and outbound send tracker` — no `status:plan-approved` label in the batch inventory.

**File existence** (verified 2026-04-30T03:56:30Z from isolated worktree):
- `docs/reports/gtm/2026-04-30-gom-niche-vessel-contractor-evidence-lane.md` — MISSING (new — this plan creates or updates)
- `docs/reports/gtm/legal-scans/2026-04-30-gom-niche-evidence-scan.json` — MISSING (new — this plan creates or updates)

**Gap proof:** `find docs/reports/gtm -maxdepth 1 -iname '*gom*'` did not reveal a canonical completed artifact for this issue number; the files named above are planned outputs.

<!-- Source count: issue #2562, #2554, #2555, #2556, BUSINESS_BRAIN, GTM report files. Meets ≥3 requirement. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-30-issue-2562-gom-niche-vessel-contractor-evidence-lane.md` |
| Primary artifact | `docs/reports/gtm/2026-04-30-gom-niche-vessel-contractor-evidence-lane.md` |
| Legal scan sidecar | `docs/reports/gtm/legal-scans/2026-04-30-gom-niche-evidence-scan.json` |
| Plan review — Hermes/local | `scripts/review/results/2026-04-30-plan-2562-hermes.md` |
| Index update | `docs/plans/README.md` |

---

## Deliverable

A public, no-PII GoM niche vessel-contractor evidence lane for the established #2554 GoM-niche target set (Helix, Otto Candies, Hornbeck, Edison Chouest Offshore) that classifies candidate operators/contractors, maps each High-priority row to Demo 3/Demo 5 or a no-demo-gap, and records official fleet/service evidence. Tidewater or other candidates require a cited source before addition.

This issue is explicitly no-outreach: no emails, messages, contact enrichment, calendar actions, send scheduling, or private/prospect routing may be performed in this execution lane.

---

## Pseudocode

```
seed candidate set from #2554 scaffold/backlog and #2562 body; required initial set is Helix, Otto Candies, Hornbeck, Edison Chouest Offshore; any extra candidate needs cited basis
for each candidate:
    classify countable vessel contractor/operator vs partner-shape/non-counted
    verify official corporate root and fleet/service deep link for every classified candidate, including Medium/Low/non-counted classifications
    map to Demo 3, Demo 5, or no-demo-gap using a rubric: offshore/subsea install or heavy-lift support fit = Demo 3 candidate; subsea jumper/IRM/tie-in support fit = Demo 5 candidate; generic OSV/logistics-only fit = no-demo-gap unless public service evidence says otherwise
    record public-only evidence; omit contacts and private routes
write GoM lane appendix and update the #2554 matrix only after evidence row is complete; #2562 owns GoM classification/demo-fit expansion, while #2560 owns broad High-priority deep-link/pain-point fill, so duplicate URLs should reference the #2560 source rather than diverge
run legal scan and no-path/proprietary leak grep before review
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/reports/gtm/2026-04-30-gom-niche-vessel-contractor-evidence-lane.md` | Primary deliverable / evidence artifact |
| Create | `docs/reports/gtm/legal-scans/2026-04-30-gom-niche-evidence-scan.json` | Legal/review/support artifact |
| Update | `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` | Apply complete GoM row updates after evidence rows are verified. |
| Update | `docs/plans/README.md` | Add/maintain this plan row. |
| Create | `scripts/review/results/2026-04-30-plan-2562-{claude,codex,gemini}.md` | Required adversarial review artifacts before plan-review. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| candidate_classification_complete | Each established GoM-niche candidate is classified countable/non-counted | Helix, Otto Candies, Hornbeck, Edison Chouest Offshore | No unclassified initial candidates; extras have cited basis |
| demo_mapping_boundary | Each High row maps to Demo 3/Demo 5 or no-demo-gap | Candidate rows | No unsupported demo claim |
| official_evidence_required | Each classified candidate has official root and fleet/service evidence or an explicit no-public-proof-found boundary | Public URLs | No placeholder-only classification row |
| no_private_contact_fields | Public artifact excludes person names, email, phone, LinkedIn profile URLs, role+name combinations, and private routes | grep plus manual row scan for `@`, phone-like patterns, `linkedin.com/in`, person-name fields, and `private_route` details | 0 private-contact/private-route findings |
| legal_scan | scripts/legal/legal-sanity-scan.sh --diff-only passes | diff containing GoM lane artifact | exit 0 |

---

## Acceptance Criteria

- [ ] Primary artifact exists at `docs/reports/gtm/2026-04-30-gom-niche-vessel-contractor-evidence-lane.md` and is public-repo-safe.
- [ ] Every source-backed claim includes a path, official URL, or explicit no-public-proof-found / no-demo-gap boundary.
- [ ] No individual contacts, direct emails, phone numbers, private route details, or send actions are added.
- [ ] Legal scan passes: `scripts/legal/legal-sanity-scan.sh --diff-only`.
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
- r2 aligned the target set with #2554 (Helix/Otto Candies/Hornbeck/ECO), separated #2562 ownership from #2560 evidence fill, added #2554 matrix as a planned update, strengthened evidence/no-PII gates, and defined a Demo 3/5 fit rubric after local MAJOR review.

---

## Risks and Open Questions

- **Risk:** Some GoM operators may be vessel owners but not the right buyer; classify partner-shape separately rather than forcing High.
- **Risk:** Official fleet pages may be sparse; use no-public-proof-found rather than unofficial aggregators for hard evidence.
- **Risk:** No outreach, route disclosure, contact data, or Gulf access/private relationship claims belong in the public artifact.

---

## Complexity: T2

**T2** — artifact/data plan with multiple evidence gates, but no application code and no authorized outreach.
