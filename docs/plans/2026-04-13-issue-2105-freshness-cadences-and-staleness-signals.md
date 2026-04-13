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
| Update (if needed) | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | align weekly checks |
| Update (if needed) | `data/document-index/intelligence-accessibility-registry.yaml` | align freshness metadata |
| Create/Update (to be determined) | `docs/document-intelligence/...` | cadence matrix / staleness doc |
| Update | `docs/plans/README.md` | add plan index row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_weekly_review_has_freshness_section | consumer surface already references freshness checks | weekly review doc | freshness section present |
| test_registry_has_freshness_metadata | registry exposes cadence metadata fields | registry yaml | freshness fields present |
| test_plan_locks_canonical_output_surface | plan names one canonical cadence artifact | plan content | exact artifact path/owner |
| test_maturity_ledger_included_in_scope | key ledger is included in freshness scope | plan content | maturity ledger referenced |

---

## Acceptance Criteria

- [ ] Canonical plan file exists for #2105.
- [ ] Existing freshness-related surfaces are inventoried and linked.
- [ ] Plan locks one canonical cadence/staleness output surface.
- [ ] Plan defines the minimal implementation slice required to make #2105 closure-ready.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Pending | — | Review not yet run |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk:** freshness logic may already be partially implemented across multiple files, making this more of a consolidation task than a greenfield task.
- **Open:** should #2105 primarily update docs, registry metadata, or both?

---

## Complexity: T2

**T2** — bounded governance/operational design work spanning a few documents and one registry surface.
