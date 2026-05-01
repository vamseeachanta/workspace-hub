# Plan for #2560: DATA(gtm): fill deep-link evidence for high-priority vessel contractor targets

> **Status:** draft (nightly immediate batch 4/5; no implementation or outreach authorized)
> **Complexity:** T2
> **Date:** 2026-04-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2560
> **Review artifacts:** `scripts/review/results/2026-04-30-plan-2560-hermes.md` (created by this batch as local adversarial review); Codex/Gemini review still required before `status:plan-review`.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` — current public matrix scaffold for #2554 with explicit `corporate_root_evidence`, `deep_link_evidence`, and `pain_point_evidence` fields.
- Found: `docs/reports/gtm/assets/vessel-capability-chart-pack-manifest.json` — #2555 chart pack landed after the prior planning wave; downstream brochure work can now consume chart metadata only after its own approval and legal gate.
- Found: `docs/reports/gtm/2026-04-29-vessel-contractor-brochure-outline.md` — #2556 outline artifact exists, but outbound is blocked by evidence/legal/user-approval gates.
- Gap: no canonical `gtm-contractor-evidence-fill` artifact exists yet under `docs/reports/gtm/`.

### Standards
Not applicable — GTM/business artifact. Engineering claims must cite existing public demo/method sources and avoid certification-grade claims unless a real standard-backed analysis is produced in a later approved issue.

### LLM Wiki pages consulted
Not required for this planning slice. If implementation uses engineering claims beyond existing GTM demo artifacts, the execution pass must consult relevant marine/offshore wiki pages and cite them explicitly.

### Documents consulted
- Issue #2560 — defines the immediate follow-up scope and acceptance criteria.
- Issue #2554 — parent contractor matrix and current blocker for #2556 send readiness.
- Issue #2555 — chart artifact issue; now CLOSED with `status:done`, providing brochure chart assets but not outbound authorization.
- Issue #2556 — brochure/send tracker issue; remains open and must not send outreach without separate user approval.
- `docs/BUSINESS_BRAIN.md` — legal-sanity gate and current weekly GTM target context.

### Gaps identified
- Missing durable artifact: `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`.
- Missing legal-scan sidecar for the planned artifact.
- Missing cross-provider plan review; this draft is not approval-ready until Claude/Codex/Gemini review the exact plan revision, or any unavailable provider is explicitly recorded as unavailable with reason and a conservative non-approved state.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-30T03:56:30Z via `gh issue view` during nightly immediate batch 4/5):
- `#2560` — OPEN — DATA(gtm): fill deep-link evidence for high-priority vessel contractor targets.
- `#2555` — CLOSED — `feat(gtm): vessel capability charts for contractor brochure` — labels include `status:done`.
- `#2556` — OPEN — `feat(gtm): vessel contractor brochure and outbound send tracker` — no `status:plan-approved` label in the batch inventory.

**File existence** (verified 2026-04-30T03:56:30Z from isolated worktree):
- `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` — EXISTS
- `docs/reports/gtm/2026-04-30-vessel-contractor-evidence-fill.md` — MISSING (new — this plan creates or updates)
- `docs/reports/gtm/legal-scans/2026-04-30-contractor-evidence-fill-scan.json` — MISSING (new — this plan creates or updates)

**Gap proof:** `find docs/reports/gtm -maxdepth 1 -iname '*gtm*'` did not reveal a canonical completed artifact for this issue number; the files named above are planned outputs.

<!-- Source count: issue #2560, #2554, #2555, #2556, BUSINESS_BRAIN, GTM report files. Meets ≥3 requirement. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-30-issue-2560-gtm-contractor-evidence-fill.md` |
| Primary artifact | `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` |
| Legal scan sidecar | `docs/reports/gtm/legal-scans/2026-04-30-contractor-evidence-fill-scan.json` |
| Plan review — Hermes/local | `scripts/review/results/2026-04-30-plan-2560-hermes.md` |
| Index update | `docs/plans/README.md` |

---

## Deliverable

A hardened public-evidence fill artifact that replaces High-priority vessel-contractor placeholder deep-link and pain-point fields with official/public proof or explicit no-public-proof-found boundaries, without contact details or outreach actions.

This issue is explicitly no-outreach: no emails, messages, contact enrichment, calendar actions, send scheduling, or private/prospect routing may be performed in this execution lane.

---

## Pseudocode

```
load scaffold rows from docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md
for each High-priority target:
    collect official-domain root already present
    verify at least one official fleet/project/vessel/service deep link, or write no-public-proof-found
    verify target-specific pain-point evidence from public target/company/project pages; if absent, write `no-public-proof-found — retain hypothesis as internal only`; shipped ACE demo proof may justify ACE capability claims but must not justify target-specific pain points
    preserve no-PII public/private split
write evidence-fill appendix with source URLs, checked_at timestamp, claim boundary, row update guidance, and an explicit authority rule: the #2554 scaffold row is authoritative after update; the appendix is review evidence and must not diverge
update the #2554 scaffold/blocker summary and rerun at least one live adversarial review of #2554 after evidence fill before removing the #2554 blocker; run legal scan and scoped/staged grep leak checks before any plan promotion
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Update | `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` | Primary deliverable / evidence artifact |
| Create | `docs/reports/gtm/2026-04-30-vessel-contractor-evidence-fill.md` | Legal/review/support artifact |
| Create | `docs/reports/gtm/legal-scans/2026-04-30-contractor-evidence-fill-scan.json` | Legal/review/support artifact |
| Update | `docs/plans/README.md` | Add/maintain this plan row. |
| Create | `scripts/review/results/2026-04-30-plan-2560-{claude,codex,gemini}.md` | Required adversarial review artifacts before plan-review. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| evidence_fill_high_priority_coverage | Every High-priority target named by #2560 has a row in the evidence-fill appendix | Target list from issue body | No missing target names |
| official_deeplink_or_boundary | Each row has official deep-link evidence or explicit no-public-proof-found | Subsea7 / TechnipFMC / Saipem / McDermott / Allseas / Heerema / Boskalis / DOF / Sapura / Seaway7 / Van Oord / DEME | No PENDING deep_link_evidence in High rows; target-specific pain points without public proof use the exact internal-only boundary |
| no_private_contact_fields | Public artifact excludes person names, email, phone, LinkedIn profile URLs, role+name combinations, and private routes | grep plus manual row scan for `@`, phone-like patterns, `linkedin.com/in`, person-name fields, and `private_route` details | 0 private-contact/private-route findings |
| legal_scan | scripts/legal/legal-sanity-scan.sh --diff-only passes | diff containing evidence artifact | exit 0 |

---

## Acceptance Criteria

- [ ] Primary artifact exists at `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md` and is public-repo-safe.
- [ ] Every source-backed claim includes a path, official URL, or explicit no-public-proof-found / no-demo-gap boundary.
- [ ] No individual contacts, direct emails, phone numbers, private route details, or send actions are added.
- [ ] Legal scan passes from a clean/staged-only diff: `scripts/legal/legal-sanity-scan.sh --diff-only`; if unrelated workspace dirt exists, run a scoped scan/grep over only the staged GTM files and record that limitation.
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
- r2 tightened target-specific pain-point evidence, #2554 update/re-review dependency, no-PII scan, provider-gate wording, scoped legal scan fallback, and source-of-truth authority after local MAJOR review.

---

## Risks and Open Questions

- **Risk:** External pages can move; each URL needs checked_at timestamp and official-domain classification.
- **Risk:** Do not promote #2556 from blocked to executable until #2554/#2560 evidence gate or explicit owner waiver is recorded.
- **Risk:** No outreach, send scheduling, contact enrichment, or private routing belongs in this issue.

---

## Complexity: T2

**T2** — artifact/data plan with multiple evidence gates, but no application code and no authorized outreach.
