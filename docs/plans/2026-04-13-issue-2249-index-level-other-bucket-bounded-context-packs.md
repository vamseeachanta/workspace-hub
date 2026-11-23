# Plan for #2249: triage index-level other bucket into bounded context packs

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2249
> **Review artifacts:** scripts/review/results/2026-04-13-plan-2249-hermes.md | scripts/review/results/2026-04-13-plan-2249-subagent.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `data/document-index/index.jsonl` is the actual live execution surface for this work. Records include `source`, `ext`, `domain`, `path_category`, and `path_subcategory`, which are the required dimensions for bounded pack decomposition.
- Found: `data/document-index/registry.yaml` reports the current aggregate corpus totals and currently lists `other: 44705` at the registry layer.
- Found: `data/document-index/data-audit-report.md` also reports index-level `other = 44,705`, but explicitly distinguishes this from standards-ledger `other`; this artifact should be treated as the current human-readable audit summary, not the only execution input.
- Found: `data/document-index/enhancement-plan.yaml` is a large classified planning artifact with itemized examples and historical `by_domain` planning data; it is useful for examples and heuristics but appears older than newer audit artifacts and must not control authoritative pack counts.
- Found: `data/document-index/resource-intelligence-maturity.yaml` records 61.9% summary coverage (639,585 / 1,033,933), confirming that semantic context enrichment remains the main bottleneck.
- Found: `data/document-index/mounted-source-registry.yaml` provides the source-root ownership model needed to make packs source-aware instead of ad hoc.
- Found: issue #2247 defines the downstream bounded authoritative writeback path for targeted classification runs; this plan must hand off exact bounded packs into that issue rather than treating triage output as authoritative by itself.
- Gap: there is no existing issue focused specifically on decomposing the live index-level `other` bucket into source-aware packs for context recovery.

### Standards
| Standard | Status | Source |
|---|---|---|
| Not a standards-implementation issue | not applicable | `data/document-index/data-audit-report.md` distinguishes index-level `other` from standards-ledger `other` |

### LLM Wiki pages consulted
- No dedicated LLM wiki page was found for the index-level `other` bucket itself.
- Related architecture context comes from `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md`, which treats registries as the control layer and durable wikis as downstream promoted knowledge.

### Documents consulted
- GitHub issue #2249 — defines the bounded triage/reclassification objective and acceptance criteria.
- `data/document-index/index.jsonl` — authoritative live corpus input for actual pack construction.
- `data/document-index/registry.yaml` — current registry-layer aggregate count for `other`.
- `data/document-index/data-audit-report.md` — current human-readable audit summary and narrative interpretation of the `other` bucket.
- `data/document-index/resource-intelligence-maturity.yaml` — confirms remaining summary/context coverage gap at the corpus level.
- `data/document-index/enhancement-plan.yaml` — contains itemized examples and historical `by_domain.other` planning data useful for heuristics but not authoritative counts.
- `data/document-index/mounted-source-registry.yaml` — authoritative source-root map for source-aware packing.
- GitHub issue #2247 — bounded authoritative domain writeback path for targeted classification runs.
- GitHub issues #2245 and #2246 — recent bounded doc-intel unblock issues that establish the preferred pattern: exact allowlists, minimal writeback, and explicit verification.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — establishes that this belongs in the registry/provenance layer, not the durable-wiki layer.

### Gaps identified
- No bounded decomposition exists for the live `index.jsonl` `other` records by source root, extension, or likely family.
- Current aggregate `other` counts must be treated as a two-layer problem: `registry.yaml` / `data-audit-report.md` agree on 44,705, but execution must still verify the live index slice before pack generation and explain any drift.
- No execution slice currently identifies which portions of `other` are high-value project documents versus low-value miscellany.
- No existing reporting artifact appears to tie `other`-bucket pack selection directly to the authoritative writeback workflow in #2247.
- No deterministic scoring rubric currently exists for deciding `reclassify now` vs `summarize first` vs `leave miscellaneous`.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-13-issue-2249-index-level-other-bucket-bounded-context-packs.md` |
| Triage report | `docs/reports/index-other-bucket-bounded-packs.md` |
| Canonical handoff artifact for #2247 | `data/document-index/index-other-bucket-pack-manifest.yaml` |
| Supporting script(s) | `scripts/data/document-index/` (bounded triage helper, if needed) |
| Plan review — Hermes | `scripts/review/results/2026-04-13-plan-2249-hermes.md` |
| Plan review — Subagent | `scripts/review/results/2026-04-13-plan-2249-subagent.md` |
| Planning index update | `docs/plans/README.md` |

---

## Scope Boundaries

### Canonical output ownership
- `docs/reports/index-other-bucket-bounded-packs.md` is the human-readable review/report surface.
- `data/document-index/index-other-bucket-pack-manifest.yaml` is the canonical machine-readable handoff artifact consumed by #2247.
- The first execution slice is source-root-first, then extension/family within each selected source-root pack. This removes ambiguity about whether source or extension drives the initial cut.
- #2247 authoritative downstream mechanics are now fixed for plan readiness: it consumes the handoff manifest and applies bounded writeback only for records explicitly listed or matched by manifest rule, updating authoritative classification state for the target set only. Required manifest fields: `pack_id`, `selection_rule`, `candidate_count`, `record_keys` (content hashes or exact record IDs), `proposed_domain`, `proposed_status`, `writeback_target`, and `provenance_note`.

### In scope now
- Decompose the live `other` bucket into bounded packs.
- Define deterministic selection rules and source-priority order.
- Produce the canonical handoff manifest for #2247 with exact allowlists and expected writeback fields.

### Out of scope now
- Performing the authoritative writeback itself (#2247 scope).
- Full reclassification of the entire `other` bucket in this issue.

---

## Deliverable

A bounded triage package that breaks the index-level `other` bucket into source-aware, extension-aware context packs, plus a canonical machine-readable handoff manifest for #2247 containing exact allowlists, selection rules, and expected authoritative writeback fields.

---

## Pseudocode
load aggregate `other` counts from registry.yaml and data-audit-report.md
load live `other` records from index.jsonl as the execution input
verify whether live index count matches current aggregate artifacts and record any drift
segment live `other` records by source root, extension, path_category, and path_subcategory
apply a deterministic scoring rubric with explicit thresholds:
    reclassify now if source in {ace_project,dde_project} AND readability in {native,ocr} AND ext in {pdf,doc,docx,xlsx,xls} AND path_category != standards
    summarize first if readability in {native,ocr} but source/family signal is ambiguous or mixed
    leave miscellaneous for now if readability == missing OR ext in {tmp,log,bak,msg} OR path_category/path_subcategory indicate admin/duplicate/general-standards residue
    break ties by source priority: ace_project > dde_project > ace_standards > og_standards > workspace_spec > api_metadata
emit a bounded pack manifest with counts, rationale, exact selection rules, and one example path per pack
handoff the top approved packs to #2247 as an explicit allowlist artifact:
    pack_id
    exact selection rule
    candidate record count
    target action (reclassify/summarize)
    expected authoritative writeback fields
write a human-readable report and verification summary explaining any count drift and the exact #2247 handoff contract
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/reports/index-other-bucket-bounded-packs.md` | primary bounded triage report |
| Create (if needed) | `data/document-index/index-other-bucket-pack-manifest.yaml` | machine-readable pack definitions |
| Create/Modify (if needed) | `scripts/data/document-index/*.py` | bounded triage helper or reporting script |
| Update | `docs/plans/README.md` | add plan index row |
| Update | GitHub issue `#2249` | surface reviewed plan once adversarial review is complete |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_other_bucket_count_matches_authoritative_audit | plan/execution uses the current 44,705 figure from the audit artifact | `data/document-index/data-audit-report.md` | count = 44,705 |
| test_pack_builder_preserves_bounded_scope | helper/report only touches `other`-bucket candidates | selected `other` records | no non-`other` records included |
| test_pack_manifest_groups_by_source_and_extension | output groups records into useful bounded packs | sample `other` records | grouped counts by source/extension/family |
| test_priority_scoring_identifies_high_value_packs | scoring highlights likely high-value project-document packs | grouped pack data | ranked shortlist |
| test_writeback_handoff_is_explicit | report + handoff manifest name downstream authoritative path and exact fields | final report + handoff artifact | references #2247, allowlist schema, expected writeback fields |
| test_scoring_thresholds_are_deterministic | the rubric yields the same classification for the same candidate records | fixed candidate fixture set | stable `reclassify now` / `summarize first` / `leave miscellaneous` output |

---

## Acceptance Criteria

- [ ] The live `index.jsonl` `other` slice is used as the execution input for bounded pack generation.
- [ ] Aggregate `other` counts from `registry.yaml` and `data-audit-report.md` are reconciled against the live index slice, with any drift explicitly explained.
- [ ] The output decomposes the `other` bucket into bounded packs with counts, source-root attribution, and exact selection rules.
- [ ] The report distinguishes likely high-value project-document packs from low-value miscellany using a deterministic scoring rubric.
- [ ] At least one immediate execution slice is identified and linked to a downstream authoritative writeback path.
- [ ] The output avoids broad corpus mutation and stays at bounded triage/reporting scope.
- [ ] Review artifacts are saved under `scripts/review/results/` before surfacing the plan for user approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Hermes | MAJOR | Missing live-index anchoring, unresolved count drift, and missing deterministic scoring thresholds |
| Subagent review | MAJOR | Review gate incomplete, #2247 handoff underdefined, deterministic rubric still too subjective |

**Overall result:** MINOR (approval-ready with implementation-time caution)

Revisions made based on review:
- anchored execution to `index.jsonl` and added `registry.yaml` / `mounted-source-registry.yaml`
- defined explicit scoring thresholds and tie-break ordering
- strengthened deliverable and test coverage around the #2247 allowlist handoff contract
- locked the downstream handoff artifact schema and #2247 bounded writeback mechanics for plan readiness

---

## Risks and Open Questions

- **Risk:** `enhancement-plan.yaml` may overstate or lag current `other` counts; the plan must anchor counts to `data-audit-report.md`.
- **Risk:** item-level extraction for all 44,705 records could expand scope; keep the deliverable at bounded-pack triage, not full reclassification.
- **Open:** none for plan approval readiness; this plan now commits to source-root-first slicing, a canonical handoff manifest, markdown-as-report / YAML-as-machine artifact ownership, and explicit #2247 bounded writeback mechanics.

---

## Complexity: T2

**T2** — bounded multi-artifact planning/reporting work with explicit downstream linkage, but not a full multi-module architecture redesign.
