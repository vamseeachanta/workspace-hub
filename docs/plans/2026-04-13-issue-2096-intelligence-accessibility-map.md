# Plan for #2096: intelligence accessibility map for llm-wikis and document/resource intelligence

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2096
> **Review artifacts:** scripts/review/results/2026-04-11-issue-2096-final-review.md | scripts/review/results/2026-04-11-issue-2096-claude-review.md | scripts/review/results/2026-04-13-plan-2096-subagent.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/document-intelligence/intelligence-accessibility-map.md` already exists as the primary deliverable for #2096 and is marked as a normative accessibility inventory for weekly review consumption.
- Found: `scripts/review/results/2026-04-11-issue-2096-claude-review.md` and `scripts/review/results/2026-04-11-issue-2096-final-review.md` already record prior approval-oriented review evidence for the deliverable itself.
- Found: `data/document-index/intelligence-accessibility-registry.yaml` exists as the machine-readable sibling surface for accessibility metadata and discoverability gaps.
- Found: `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` explicitly references #2096 in the weekly checklist and defines discoverability regression checks that consume the accessibility map.
- Found: `docs/document-intelligence/data-intelligence-map.md` provides the registry/index location reference that #2096 should treat as an L4 navigation input.
- Gap: the remaining work is not to create the accessibility map, but to reconcile completion/closure readiness against sibling-registry drift and confirm whether any final minimal fixes are needed before closing the issue.

### Standards
N/A — documentation / accessibility / knowledge-governance task

### LLM Wiki pages consulted
- `knowledge/wikis/*/CLAUDE.md` are referenced by the accessibility map as entry points, but this issue is about accessibility inventory, not wiki-content changes.

### Documents consulted
- GitHub issue #2096 — scope and deliverables for the accessibility map.
- `docs/document-intelligence/intelligence-accessibility-map.md` — existing normative artifact implementing the issue scope.
- `scripts/review/results/2026-04-11-issue-2096-claude-review.md` — prior adversarial review of the deliverable.
- `scripts/review/results/2026-04-11-issue-2096-final-review.md` — prior integrator/final review marking the deliverable approved.
- `data/document-index/intelligence-accessibility-registry.yaml` — machine-readable accessibility sibling artifact whose discoverability metadata may lag the human-readable map.
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — weekly review consumer.
- `docs/document-intelligence/data-intelligence-map.md` — companion navigation/reference map.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — parent operating model placing #2096 at Layer 4 entry-point scope.

### Gaps identified
- Need to determine whether any human-readable map vs machine-readable registry discoverability drift must be fixed inside #2096, or explicitly delegated to a sibling issue.
- Need a closure-ready verification checklist that proves the existing deliverable still satisfies issue scope and weekly-review consumption.
- Need to avoid duplicating prior approved review work; this plan should focus on completion/verification, not re-design.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-13-issue-2096-intelligence-accessibility-map.md` |
| Primary deliverable | `docs/document-intelligence/intelligence-accessibility-map.md` |
| Machine-readable sibling | `data/document-index/intelligence-accessibility-registry.yaml` |
| Weekly-review consumer | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` |
| Planning index update | `docs/plans/README.md` |

---

## Deliverable

A bounded completion/validation plan for #2096 that treats `docs/document-intelligence/intelligence-accessibility-map.md` as the already-approved primary deliverable and defines the exact final verification and drift-reconciliation steps needed to move the issue to closure-ready state.

---

## Pseudocode

```text
confirm the accessibility map remains the primary deliverable and reuse prior approved review evidence
cross-check the map against the weekly review checklist and sibling registry
identify only the remaining drift items that block closure:
    map says discoverable / registry says partially-discoverable or hard-to-discover
    missing backlinks from current canonical entry points
if drift is within #2096 scope:
    define minimal corrective edits
else:
    record explicit delegation to sibling/follow-on issue
prepare a closure-ready verification checklist and closeout note
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-13-issue-2096-intelligence-accessibility-map.md` | canonical plan artifact |
| Update (if needed) | `docs/document-intelligence/intelligence-accessibility-map.md` | final gap fixes only |
| Update (if needed) | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | ensure consumer checklist aligns |
| Update | `docs/plans/README.md` | add plan index row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_accessibility_map_exists | primary deliverable exists | map path | file present |
| test_prior_review_artifacts_exist | existing approved review evidence is present and reused | review artifact paths | files present |
| test_accessibility_map_covers_required_asset_classes | map covers wiki, registry, docs, weekly-review surfaces | map content | all required classes listed |
| test_weekly_review_references_2096_checks | weekly review consumes #2096 outputs | weekly review doc | accessibility checks present |
| test_registry_sibling_is_referenced | map points to machine-readable registry sibling | map content | registry path referenced |
| test_drift_resolution_is_explicit | any remaining map/registry drift is either fixed or delegated explicitly | plan + artifacts | no ambiguous closure blocker |

---

## Acceptance Criteria

- [ ] Canonical plan file exists for #2096.
- [ ] Existing approved deliverable and prior review evidence are explicitly reused rather than re-invented.
- [ ] Existing accessibility map is verified against issue scope and weekly-review use.
- [ ] Any remaining map/registry drift is either fixed in-scope or explicitly delegated.
- [ ] Issue can be moved to closure-ready state once the bounded verification steps are complete.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Prior deliverable review | APPROVE | Existing accessibility-map artifact already reviewed and approved |
| Subagent review | MAJOR | Initial draft was stale about plan/review existence and closure scope |

**Overall result:** MINOR (approval-ready after revision)

Revisions made based on review:
- removed stale premise about missing plan/review artifacts
- reframed scope around closure-readiness and map/registry drift reconciliation
- explicitly reused prior approved review evidence
- tightened acceptance criteria around bounded closure verification

---

## Risks and Open Questions

- **Risk:** the machine-readable registry may lag the human-readable map on discoverability states; closure should only depend on whether that drift is explicitly resolved or delegated.
- **Open:** none for plan approval readiness; the remaining work is bounded closure verification, not architecture redesign.

---

## Complexity: T2

**T2** — bounded documentation/governance validation work with an existing primary artifact and a small number of dependent surfaces.
