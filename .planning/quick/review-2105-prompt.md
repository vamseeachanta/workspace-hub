# Adversarial Review Request: Issue #2105

You are an independent adversarial reviewer. Find gaps, risks, missing edge cases, missing retrieval, unclear scope boundaries, unsafe assumptions, and workflow/governance violations. Do NOT rubber-stamp.

Return verdict as one of: APPROVE, MINOR, MAJOR.

Required output format:
1. Verdict
2. Ready for user approval: Yes/No
3. Retrieval adequacy: adequate/insufficient
4. Top blockers (numbered)
5. Critical findings
6. High findings
7. Medium findings
8. Low findings
9. Required revisions before user approval

Context:
- Repository: workspace-hub
- Review type: plan-stage adversarial review
- Focus on whether this plan is genuinely approval-ready under repo workflow/governance rules.

GitHub issue metadata:
- Issue: #2105
- Title: chore(knowledge): define freshness cadences and staleness signals for intelligence assets
- URL: https://github.com/vamseeachanta/workspace-hub/issues/2105
- Labels: enhancement, priority:medium, cat:documentation, cat:harness, status:plan-approved

GitHub issue body:
## Summary
Define freshness cadences and staleness signals for llm-wikis, resource intelligence, and document intelligence so the weekly review in #2089 can judge whether these assets are current enough for execution.

## Why
The weekly review currently asks whether intelligence is up to date, but it needs explicit expectations by asset type. Different intelligence assets should have different acceptable staleness windows and different refresh signals.

## Scope
- classify intelligence assets by type and expected refresh cadence
- define acceptable staleness thresholds
- define freshness signals and evidence sources
- identify assets that need automatic refresh vs manual review
- define how freshness failures should appear in weekly findings

## Deliverables
- cadence matrix by intelligence type
- staleness thresholds and alert levels
- freshness evidence/checklist for weekly review
- recommendations for automation where helpful

## Parent
- Parent issue: #2089
- Related: #2096, #2097


Plan under review (docs/plans/2026-04-13-issue-2105-freshness-cadences-and-staleness-signals.md):
# Plan for #2105: define freshness cadences and staleness signals for intelligence assets

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2105
> **Review artifacts:** scripts/review/results/2026-04-13-plan-2105-subagent.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` already includes a freshness/staleness checklist and explicitly references #2105 for knowledge freshness.
- Found: `data/document-index/intelligence-accessibility-registry.yaml` already contains per-asset freshness metadata fields such as `freshness_source` and `freshness_cadence`; this is the natural machine-readable input surface for #2105.
- Found: `config/scheduled-tasks/schedule-tasks.yaml` defines an existing `staleness-scan` scheduled task.
- Found: `scripts/cron/staleness-scan-weekly.sh`, `scripts/docs/staleness-scanner.py`, and `docs/dashboards/doc-freshness-dashboard.md` already implement part of the freshness/staleness machinery.
- Found: `docs/document-intelligence/intelligence-accessibility-map.md` documents discoverability and freshness-adjacent weekly-review context.
- Found: `data/document-index/resource-intelligence-maturity.yaml` is a canonical freshness-sensitive ledger that must be part of the cadence matrix.
- Gap: no single canonical cadence/staleness matrix artifact is locked, and the existing freshness machinery is not yet explicitly unified with the weekly-review intelligence surfaces.

### Standards
N/A — documentation / governance / operational review task

### Documents consulted
- GitHub issue #2105 — defines the cadence/staleness scope.
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — consumer of freshness checks.
- `data/document-index/intelligence-accessibility-registry.yaml` — source of per-asset freshness metadata.
- `docs/document-intelligence/intelligence-accessibility-map.md` — sibling accessibility inventory.
- `data/document-index/resource-intelligence-maturity.yaml` — canonical maturity/freshness-sensitive ledger.
- `config/scheduled-tasks/schedule-tasks.yaml` — scheduled staleness-scan execution path.
- `scripts/cron/staleness-scan-weekly.sh` — existing weekly staleness runner.
- `scripts/docs/staleness-scanner.py` — existing freshness/staleness implementation surface.
- `docs/dashboards/doc-freshness-dashboard.md` — existing freshness output surface.
- GitHub issue #2097 — related recurring execution path for weekly review.

### Gaps identified
- No canonical cadence/staleness matrix artifact is locked.
- Existing staleness machinery is not yet explicitly connected to the intelligence-asset freshness contract used by weekly review.
- The threshold semantics (`current`, `warn`, `stale`) and ownership model for applying them are not yet defined in one bounded place.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-13-issue-2105-freshness-cadences-and-staleness-signals.md` |
| Weekly-review consumer | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` |
| Registry source | `data/document-index/intelligence-accessibility-registry.yaml` |
| Maturity ledger | `data/document-index/resource-intelligence-maturity.yaml` |
| Canonical cadence matrix | `docs/document-intelligence/freshness-cadence-matrix.md` |
| Existing scanner/runner | `scripts/docs/staleness-scanner.py`, `scripts/cron/staleness-scan-weekly.sh` |
| Existing dashboard | `docs/dashboards/doc-freshness-dashboard.md` |
| Planning index update | `docs/plans/README.md` |

---

## Deliverable

A bounded plan for #2105 that locks `docs/document-intelligence/freshness-cadence-matrix.md` as the canonical freshness/staleness artifact, defines threshold semantics and ownership, and specifies the minimal updates needed so weekly review, registry metadata, and existing scanner/dashboard surfaces work together consistently.

---

## Pseudocode

```text
inspect existing weekly-review freshness checks
inspect registry freshness metadata fields and maturity ledger freshness-sensitive assets
inspect existing staleness machinery:
    scripts/docs/staleness-scanner.py
    scripts/cron/staleness-scan-weekly.sh
    docs/dashboards/doc-freshness-dashboard.md
lock `docs/document-intelligence/freshness-cadence-matrix.md` as the canonical cadence artifact
define threshold semantics:
    current
    warn
    stale
map each intelligence asset class to cadence + threshold + evidence source + owner
specify minimal updates needed across matrix doc, weekly review checklist, registry metadata, and existing scanner/dashboard surfaces
prepare closure-ready implementation slice for the issue
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-13-issue-2105-freshness-cadences-and-staleness-signals.md` | canonical plan artifact |
| Create/Update | `docs/document-intelligence/freshness-cadence-matrix.md` | canonical cadence/staleness matrix |
| Update (if needed) | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | align weekly checks |
| Update (if needed) | `data/document-index/intelligence-accessibility-registry.yaml` | align freshness metadata |
| Update (if needed) | `scripts/docs/staleness-scanner.py` or `scripts/cron/staleness-scan-weekly.sh` | connect existing freshness machinery to the canonical matrix |
| Update | `docs/plans/README.md` | add plan index row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_weekly_review_has_freshness_section | consumer surface already references freshness checks | weekly review doc | freshness section present |
| test_registry_has_freshness_metadata | registry exposes cadence metadata fields | registry yaml | freshness fields present |
| test_plan_locks_canonical_output_surface | plan names one canonical cadence artifact | plan content | exact artifact path/owner |
| test_threshold_semantics_are_defined | canonical matrix defines `current` / `warn` / `stale` semantics | matrix doc | threshold definitions present |
| test_existing_staleness_machinery_is_integrated | plan references scanner/runner/dashboard instead of duplicating them | plan content | existing machinery explicitly integrated |
| test_maturity_ledger_included_in_scope | key ledger is included in freshness scope | plan content | maturity ledger referenced |

---

## Acceptance Criteria

- [ ] Canonical plan file exists for #2105.
- [ ] Existing freshness-related surfaces are inventoried and linked.
- [ ] `docs/document-intelligence/freshness-cadence-matrix.md` is locked as the canonical cadence/staleness artifact.
- [ ] Threshold semantics (`current`, `warn`, `stale`) and ownership are explicitly defined.
- [ ] Plan defines the minimal implementation slice required to make weekly review, registry metadata, and existing staleness machinery work together consistently.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Subagent review | MAJOR | Initial draft left canonical output path unlocked and missed existing freshness machinery |

**Overall result:** MINOR (approval-ready after revision)

Revisions made based on review:
- locked `docs/document-intelligence/freshness-cadence-matrix.md` as the canonical output surface
- added existing staleness machinery (`staleness-scan`, scanner, dashboard) to the evidence base and implementation slice
- defined threshold semantics and ownership expectations explicitly in the plan

---

## Risks and Open Questions

- **Risk:** freshness logic is distributed across docs, registry metadata, and scanner outputs; implementation must keep one canonical matrix while avoiding duplicate threshold definitions.
- **Open:** none for plan approval readiness; the remaining work is a bounded consolidation/integration task, not a scope-definition problem.

---

## Complexity: T2

**T2** — bounded governance/operational design work spanning a few documents and one registry surface.


Review questions — address ALL:
1. Is the plan specific enough to execute without hidden design decisions surfacing during implementation?
2. Does the resource intelligence satisfy the repo planning contract, or are important sources missing?
3. Are files-to-change, TDD, acceptance criteria, and risks concrete and falsifiable?
4. Are there unresolved scope/governance/status inconsistencies that should block approval?
5. Should this plan be approved as-is, revised, or split?
