# Plan for #2250: reconcile stale intelligence summary artifacts against canonical ledgers

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2250
> **Review artifacts:** scripts/review/results/2026-04-13-plan-2250-hermes.md | scripts/review/results/2026-04-13-plan-2250-subagent.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `data/document-index/resource-intelligence-maturity.yaml` explicitly marks itself as authoritative and states that the markdown summary must not diverge.
- Found: `data/document-index/resource-intelligence-maturity.md` currently diverges materially from the YAML ledger (5 docs in scope / 0 read versus 425 docs in scope / 29 read in YAML).
- Found: `data/document-index/data-audit-report.md` provides the current audit snapshot for index counts, summary coverage, and index-level `other` counts; it should be treated as a derived audit surface, not assumed authoritative for all metric families without cross-check.
- Found: `data/document-index/registry.yaml` is the current aggregate registry surface for total docs, total summaries, and by-domain counts, including `other: 44705`.
- Found: `data/document-index/standards-transfer-ledger.yaml` is a canonical ledger surface for standards metrics and currently reports `total: 436`, `done: 435`, `implemented: 1`, which materially conflicts with the 425/29/235/138 figures repeated elsewhere.
- Found: `data/document-index/enhancement-plan.yaml` is a large planning artifact whose `by_domain.other.count` appears older than newer audit artifacts; it should be treated as a planning input, not the final count authority for current corpus state.
- Found: issue #2205 and its plan establish the owner model: ledgers/registries own provenance and corpus-state facts, while convenience summaries must not become competing sources of truth.
- Gap: there is no dedicated drift-check issue/artifact that reconciles summary markdown, planning ledgers, audit outputs, and the standards ledger together.

### Standards
| Standard | Status | Source |
|---|---|---|
| Not a standards-implementation issue | not applicable | issue concerns control-plane artifact drift, not standards implementation |

### LLM Wiki pages consulted
- No direct LLM wiki page is required for this issue.
- The relevant architectural guidance comes from the #2205 operating-model plan, which assigns metric/provenance ownership to the registry/ledger layer and forbids competing truth in convenience summaries.

### Documents consulted
- GitHub issue #2250 — defines the drift-reconciliation scope and acceptance criteria.
- `data/document-index/resource-intelligence-maturity.yaml` — authoritative maturity ledger.
- `data/document-index/resource-intelligence-maturity.md` — stale derived summary with mismatched counts.
- `data/document-index/registry.yaml` — aggregate registry surface for total docs, summaries, and domain counts.
- `data/document-index/standards-transfer-ledger.yaml` — canonical standards ledger whose headline counts must be reconciled against copied/derived summaries.
- `data/document-index/data-audit-report.md` — current audit snapshot for summary coverage and index-level `other` counts.
- `data/document-index/enhancement-plan.yaml` — historical planning artifact whose `other` counts need careful positioning relative to newer audit outputs.
- `docs/document-intelligence/data-intelligence-map.md` — copy surface that repeats key metrics and therefore belongs in the drift/control analysis.
- `docs/assessments/document-intelligence-audit.md` — another copy/reporting surface that repeats key metrics and should be classified as derived rather than canonical.
- `docs/plans/2026-04-01-knowledge-persistence-architecture.md` — prior planning artifact that already states the YAML→markdown authoritative relationship and implies a generator/root-cause angle.
- GitHub issue #2205 and `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — architectural source-of-truth boundary.
- GitHub issue #2096 — accessibility/discoverability framing for intelligence assets.
- GitHub issue #2105 — freshness/staleness expectations for intelligence assets.
- GitHub issues #2156 and #2168 — registry coherence and cross-registry drift validation follow-ons.

### Gaps identified
- The maturity markdown summary has drifted from its canonical YAML ledger.
- The standards metrics family has a live contradiction between `standards-transfer-ledger.yaml` and the copied 425/29/235/138 figures repeated in audit/summary surfaces; this plan must explicitly decide ownership by metric family rather than assume one file owns everything.
- There is no explicit source-of-truth matrix for the main intelligence metrics and their allowed derivative copies.
- There is no committed regeneration/validation path that prevents convenience summaries from drifting from their canonical ledgers.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-13-issue-2250-reconcile-stale-intelligence-summary-artifacts.md` |
| Drift report | `docs/reports/intelligence-summary-ledger-drift-report.md` |
| Corrected summary artifacts | `data/document-index/resource-intelligence-maturity.md` and any other derived summaries found in scope |
| Canonical owner map | `docs/reports/intelligence-metric-owner-map.md` |
| Validator/check implementation | `scripts/validation/check-intelligence-ledger-drift.py` |
| Plan review — Hermes | `scripts/review/results/2026-04-13-plan-2250-hermes.md` |
| Plan review — Subagent | `scripts/review/results/2026-04-13-plan-2250-subagent.md` |
| Planning index update | `docs/plans/README.md` |

---

## Deliverable

A reconciled intelligence control-plane package that (1) assigns canonical ownership by metric family, (2) fixes the currently known stale/copy artifacts in scope, and (3) defines a repeatable regeneration/validation path so derived summaries cannot silently drift again.

---

## Canonical ownership decisions to lock in

| Metric family | Canonical owner | Allowed derivative surfaces | Rule |
|---|---|---|---|
| Maturity metrics (`documents_in_scope`, `documents_marked_read`, `% read`) | `data/document-index/resource-intelligence-maturity.yaml` | `resource-intelligence-maturity.md` | markdown must be regenerated from YAML |
| Corpus totals / summary coverage / by-domain counts | `data/document-index/registry.yaml` | `data-audit-report.md`, `docs/document-intelligence/data-intelligence-map.md`, `docs/assessments/document-intelligence-audit.md` | registry owns numbers; reports may copy them only via regeneration/validation |
| Standards-ledger totals / done / implemented / gap/reference counts | `data/document-index/standards-transfer-ledger.yaml` | any report/summary citing standards totals | ledger owns standards metrics; conflicting copies must be corrected or explicitly deprecated |
| Historical planning examples (`by_domain.other`, itemized examples) | `data/document-index/enhancement-plan.yaml` | planning docs only | not authoritative for current counts |

## Regeneration / validation decisions to lock in
- `resource-intelligence-maturity.md` is regenerated from the YAML ledger, not manually edited.
- Drift validation lives at `scripts/validation/check-intelligence-ledger-drift.py`.
- Validation runs against the owner map in `docs/reports/intelligence-metric-owner-map.md`.
- Copy surfaces that cannot be regenerated automatically must be explicitly listed as manual-but-validated in the owner map; anything else is out of policy.

---

## Pseudocode

```text
identify metric families in scope:
    maturity metrics
    corpus summary-coverage metrics
    standards-ledger metrics
    index-level other-bucket metrics
for each metric family:
    assign one canonical owner artifact
    list allowed derivative/copy surfaces
    state whether each copy is regenerated, manually maintained, or deprecated
compare canonical owner values to each derivative copy
record mismatches with file-level evidence
update or deprecate stale derived summaries
implement or specify a regeneration/validation path:
    regenerate markdown summaries from canonical YAML where applicable
    add a drift-check helper that fails when derivative copies diverge
link the result to freshness/coherence follow-on issues
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/reports/intelligence-summary-ledger-drift-report.md` | explicit mismatch inventory and remediation summary |
| Modify | `data/document-index/resource-intelligence-maturity.md` | align convenience summary with authoritative YAML ledger |
| Create/Modify (if needed) | `scripts/data/document-index/*.py` or `scripts/validation/*.py` | lightweight drift-check helper |
| Update | `docs/plans/README.md` | add plan index row |
| Update | GitHub issue `#2250` | surface reviewed plan after adversarial review completes |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_maturity_markdown_matches_yaml | derived maturity summary reflects authoritative YAML values | YAML + markdown pair | identical key metrics |
| test_metric_family_owner_map_is_total | each metric family in scope has exactly one canonical owner and explicit derivative list | owner-map artifact | one owner per family, no ambiguous ownership |
| test_audit_report_ownership_is_scoped | corpus summary-coverage and index `other` metrics are scoped correctly against audit and registry surfaces | audit + registry + owner map | explicit owner decision by family |
| test_standards_ledger_conflict_is_resolved | standards metric family explicitly resolves the 436 vs 425-style conflict | standards ledger + copied surfaces + owner map | canonical owner + treatment of stale copies |
| test_drift_report_lists_each_mismatch_once | drift report is deterministic and non-duplicative | known mismatch set | one row per mismatch |
| test_validator_flags_divergent_summary | check fails when derived summary diverges from canonical ledger | synthetic mismatch | validation failure |
| test_validator_passes_after_reconciliation | check passes after summary is corrected | corrected artifacts | validation success |

---

## Acceptance Criteria

- [ ] Known drift between `resource-intelligence-maturity.yaml` and `.md` is documented and corrected.
- [ ] Metric families in scope are explicitly enumerated and each has exactly one canonical owner artifact.
- [ ] The standards-ledger conflict is resolved by an explicit owner/treatment decision rather than left ambiguous.
- [ ] Allowed derivative/copy surfaces are listed for each metric family in scope.
- [ ] The plan/report explains how `enhancement-plan.yaml` should be treated relative to newer audit artifacts.
- [ ] A repeatable regeneration and drift-check path is specified, including which script/surface owns validation.
- [ ] Review artifacts are saved under `scripts/review/results/` before surfacing the plan for user approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Hermes | MAJOR | Missing standards-ledger reconciliation, incomplete owner map, and vague regeneration/validation path |
| Subagent review | MAJOR | Review gate incomplete, canonical-owner split unresolved, validator ownership too vague |

**Overall result:** APPROVE

Revisions made based on review:
- added `registry.yaml`, `standards-transfer-ledger.yaml`, and broader copy surfaces to the evidence base
- reworked the plan around explicit metric families and canonical-owner assignment
- added standards-ledger conflict resolution and regeneration/validation ownership to tests and acceptance criteria
- locked validator placement to `scripts/validation/check-intelligence-ledger-drift.py` and regeneration to owner-map rules for plan readiness

---

## Risks and Open Questions

- **Risk:** some artifacts are planning snapshots rather than canonical state; the remediation must avoid flattening all files into one truth source.
- **Risk:** adding too much generalized validation logic could broaden scope beyond the immediate drift-control need.
- **Open:** none for plan approval readiness; validator placement is locked to `scripts/validation/check-intelligence-ledger-drift.py`, regeneration follows owner-map rules, and standards-ledger conflict handling is fixed at the metric-family owner level.

---

## Complexity: T2

**T2** — bounded control-plane consistency work requiring evidence comparison across multiple intelligence artifacts, but limited implementation surface.
