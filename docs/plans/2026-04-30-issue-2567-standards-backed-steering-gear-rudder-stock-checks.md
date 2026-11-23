# Plan for #2567: Standards-backed steering gear and rudder-stock design checks

> **Status:** plan-review — adversarial reviewed; awaiting user approval
> **Complexity:** T3
> **Date:** 2026-04-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2567
> **Review artifacts:** scripts/review/results/2026-04-30-plan-2567-claude.md | scripts/review/results/2026-04-30-plan-2567-codex.md | scripts/review/results/2026-04-30-plan-2567-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- `digitalmodel/src/digitalmodel/naval_architecture/maneuverability.py` contains the current Whicker/Fehlner-style rudder normal force helper.
- `digitalmodel/src/digitalmodel/naval_architecture/yaw_moment.py` implements preliminary yaw moment only and explicitly excludes class/IMO compliance.
- `digitalmodel/src/digitalmodel/naval_architecture/rudder_stock_torque.py` implements preliminary torque only: `T_stock = scalar_normal_force_N * stock_to_center_of_pressure_arm_m`, with required holding torque equal/opposite. It explicitly excludes steering gear machinery sizing, actuator sizing, rudder stock scantling, bearing reactions, and SOLAS/class compliance proof.
- `digitalmodel/src/digitalmodel/naval_architecture/compliance.py` exists but uses coarse pass/fail semantics and is not clause-traceable enough for standards-backed checks.

### Standards
- No dedicated steering-gear or rudder-stock transferred standard was found in `data/document-index/standards-transfer-ledger.yaml` during the read-only audit.
- Strong portal/source anchors exist in `data/document-index/online-resource-registry.yaml`:
  - DNV Rules and Standards Explorer.
  - ABS Marine Vessel Rules — Part 4 (2024).
  - SOLAS 2020 Consolidated Edition, with local backup path under `/mnt/ace/docs/_standards/SNAME/textbooks/`.
  - IACS Unified Requirements and Blue Book.
- A metadata-only local inventory anchor was found for `2010 DNV/2010 Ship Rules/ts414, steering gear.pdf` in `docs/reports/2264-wave4-inventory.yaml`; this is not implementation-grade until clause text is extracted/promoted.

### LLM Wiki pages consulted
- `knowledge/wikis/naval-architecture/wiki/concepts/yaw-moment-rudder-sweep.md` — current yaw envelope and future boundaries.
- `knowledge/wikis/naval-architecture/wiki/concepts/rudder-force-modeling.md` — current rudder normal force basis.
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-coordinate-conventions.md` — sign convention caveats.
- `knowledge/wikis/naval-architecture/wiki/concepts/maneuvering-validation-metrics.md` — IMO/ABS validation context, not enough for rudder-stock scantling.

### Documents consulted
- #2565 closeout and implementation review: confirms #2565 is preliminary and cross-reviewed but not standards-backed.
- `data/document-index/online-resource-registry.yaml` lines for DNV, ABS, SOLAS, IACS portals.
- `docs/reports/2264-wave4-inventory.yaml` metadata-only DNV TS414 steering gear anchor.

### Gaps identified
- Clause-level source extraction/crosswalk for steering gear and rudder-stock checks does not yet exist.
- No standards-backed formulas should be implemented until source clauses, editions, assumptions, and exclusions are promoted into a traceable crosswalk.
- Current #2565 torque workflow cannot be relabeled as compliance or machinery/scantling sizing.

### Evidence
- #2565 implementation files and tests contain explicit exclusion language.
- `online-resource-registry.yaml` contains DNV/ABS/SOLAS/IACS portal entries.
- Subagent resource-intelligence audit for #2567 found no direct standards-transfer-ledger entry for steering gear or rudder-stock rule text.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-30-issue-2567-standards-backed-steering-gear-rudder-stock-checks.md` |
| Source map | `knowledge/wikis/naval-architecture/wiki/comparisons/issue-2567-steering-gear-rudder-stock-source-map.md` |
| Steering gear concept | `knowledge/wikis/naval-architecture/wiki/concepts/steering-gear-design-checks.md` |
| Rudder stock concept | `knowledge/wikis/naval-architecture/wiki/concepts/rudder-stock-design-checks.md` |
| Standards crosswalk | `knowledge/wikis/naval-architecture/wiki/standards/steering-gear-rudder-stock-rule-crosswalk.md` |
| Follow-up issue pack | `docs/plans/followups/2026-04-30-issue-2567-child-issues.md` |
| Plan review artifacts | `scripts/review/results/2026-04-30-plan-2567-*.md` |

---

## Deliverable

A standards-source crosswalk and decomposition package for steering-gear/rudder-stock checks, with a draft child-issue pack for later GitHub filing after source clauses are verified and the crosswalk is approved; this issue does not create live implementation issues by default and does not implement standards formulas.

---

## Hard-stop / source-authority gate

This issue is source-intelligence and decomposition only. It must not add standards-derived code/formulas, relabel #2565 outputs as compliant, or create live implementation child issues unless the user explicitly requests that after reviewing the crosswalk. Portal entries, metadata-only inventory anchors, and secondary wiki summaries are not formula authority; every implementation-ready row must cite clause-ready source text with edition and locator.

---

## Pseudocode

```text
function build_source_crosswalk():
    collect candidate standards from online registry, standards ledger, /mnt/ace inventory, and wiki
    for each source:
        record publisher, title, edition, local path/url, clause/part locator, extraction status
        classify into steering gear load envelope, rudder stock scantling/stress, machinery/actuator sizing, or compliance criteria
        classify as functional/regulatory requirement, class-rule load/scantling formula, machinery sizing, bearing reaction, or non-authoritative reference
        mark whether implementation-ready clause text exists; metadata-only or portal-only sources are source-gap
    write wiki source-map and standards crosswalk
    draft child issue proposals in docs/plans/followups only for implementation-ready slices; do not open GitHub child issues by default
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/naval-architecture/wiki/comparisons/issue-2567-steering-gear-rudder-stock-source-map.md` | exact source inventory and gap map |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/steering-gear-design-checks.md` | concept boundary and vocabulary |
| Create | `knowledge/wikis/naval-architecture/wiki/concepts/rudder-stock-design-checks.md` | concept boundary and vocabulary |
| Create | `knowledge/wikis/naval-architecture/wiki/standards/steering-gear-rudder-stock-rule-crosswalk.md` | clause/source crosswalk |
| Create | `docs/plans/followups/2026-04-30-issue-2567-child-issues.md` | draft issue pack only; not live GitHub issues |
| Update | `docs/plans/README.md` | plan index |

---

## TDD / Validation List

| Check | What it verifies | Expected result |
|---|---|---|
| crosswalk source completeness check | DNV/ABS/SOLAS/IACS candidates classified | all candidates present with status |
| no-compliance-overclaim text check | source files explicitly say no formula implementation yet | pass |
| child issue draft check | each implementable slice has a title, scope, exclusions, required source clauses | pass |
| wiki lint/status | naval-architecture wiki remains valid after additions | pass |

---

## Acceptance Criteria

- [ ] Source map identifies DNV, ABS, SOLAS, IACS, and local DNV TS414 metadata anchor status with exact paths/URLs and extraction status.
- [ ] Crosswalk rows include publisher, standard title, edition/year, exact clause/part locator, source path/URL, extraction status, readiness status, and rationale.
- [ ] Crosswalk separates functional/regulatory requirements, class-rule load/scantling formulas, machinery/actuator sizing, bearing reactions, and non-authoritative references.
- [ ] Every item is marked implementation-ready / source-gap / out-of-scope with rationale; portal-only and metadata-only entries cannot be marked implementation-ready.
- [ ] Draft follow-up file exists at `docs/plans/followups/2026-04-30-issue-2567-child-issues.md` containing 0+ candidate child issues; each candidate has title, scope, exclusions, required clause citations, and readiness status.
- [ ] No live GitHub child implementation issue is created and no standards-derived formula/code is added unless explicitly approved in a later step.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Engineering reviewer | MINOR -> resolved | Added metadata/portal non-authority rule, source-readiness row requirements, and regulatory-vs-class formula classification. |
| Governance reviewer | MAJOR -> resolved | Reframed child issues as draft-only, strengthened hard stop, and made crosswalk acceptance deterministic. |
| Package/test reviewer | UNAVAILABLE | Subagent timed out; no code/package work is in scope for this source-crosswalk issue. |

**Overall result:** PASS after revisions; ready for user approval gate.

---

## Risks and Open Questions

- **Risk:** standards access may remain portal-only or metadata-only, blocking formula implementation.
- **Risk:** broad issue title could tempt scope creep; this plan intentionally narrows #2567 to source crosswalk/decomposition before formulas.
- **Open:** if clause text is found quickly, should implementation still be child issues? Default answer: yes, keep formula/check implementation separate.

---

## Complexity: T3

**T3** — standards/source-intelligence issue with future implementation decomposition and strict compliance-overclaim risk control.
