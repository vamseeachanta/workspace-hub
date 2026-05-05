# Plan for #2643: llm-wiki raw-like source coverage triage

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-05-04
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2643
> **Review artifacts:** scripts/review/results/2026-05-04-plan-2643-claude.md | scripts/review/results/2026-05-04-plan-2643-codex.md | scripts/review/results/2026-05-04-plan-2643-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `data/document-index/mounted-source-registry.yaml` — defines mounted-source governance context for local/remote/API sources; this plan will not replace it, only add a raw-like routing view that can be reconciled with it.
- Found: `data/document-index/index.jsonl` — already indexes some mounted sources, but selected raw-like roots show uneven coverage: 72 records for the ACMA/DAS raw sensor path and 0 records for O&G raw, BSEE raw data, AQWA raw decks, OrcaFlex raw examples, Frontier Deepwater raw, and worldenergydata HSE raw.
- Gap: no existing `ace-data` raw-like source routing matrix was found in `docs/plans/` or document-intelligence docs that covers all discovered `/mnt/ace-data` raw-like roots with target wiki/domain, sensitivity, and issue mapping.

### Standards
| Standard/source family | Status | Source |
|---|---|---|
| O&G standards raw store | Partial / needs routing, not direct promotion | `/mnt/ace-data/O&G-Standards/raw`; related #2364, #2373, #2392, #2487, and completed bounded standards promotions #2586/#2590/#2591/#2594/#2595/#2611 |
| Proprietary/project/client raw material | Approval-gated | #2540/#2541-#2544/#2559 precedent and raw-data boundary |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/` — target for general engineering source-family gaps, but not a raw-data sink.
- `knowledge/wikis/engineering-standards/` — target for standards metadata/summaries only after bounded approval, not raw standards copying.
- `knowledge/wikis/marine-engineering/` — target for offshore/marine concept/entity/source summaries, but project-sensitive raw material remains mounted-source only.

### Documents consulted
- Issue #2643 — asks for metadata-only raw-like source coverage triage after `/mnt/ace-data/raw data` was found missing as a literal path.
- Issue #2390 — open llm-wiki strengthening roadmap umbrella; all new raw-like coverage work will link back here.
- Issue #2392 — open wiki coverage-gap detector; this plan will feed it raw-like source families instead of duplicating the detector.
- Issue #2487 — closed raw-data-to-GTM readiness spine/control-plane; this plan will reuse its readiness-mapping principle rather than recreate it.
- Issues #2103 and #2124 — existing AQWA/BEMRosetta and Orcina/OrcaFlex ingestion anchors; AQWA and OrcaFlex raw-like local folders will be routed to those issues.
- `docs/document-intelligence/data-intelligence-map.md` and `docs/document-intelligence/README.md` — document-intelligence entry points for durable data artifact discovery.
- `docs/sessions/2026-05-02-llm-wiki-completeness-loop.md` — raw-data boundary and plan-review hard stop precedent.

### Gaps identified
- No durable metadata-only table currently classifies all discovered raw-like directories under `/mnt/ace-data` by corpus suitability, sensitivity, target wiki/domain, existing issue mapping, and next action.
- No explicit exclusion list distinguishes `.gitkeep`, code/vendor internals, generated outputs, marketing images, personal/project-sensitive raw data, and true llm-wiki candidates.
- No follow-up package queue currently converts the raw-like inventory into approval-gated source-family issues without promoting raw content.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-04 via `gh issue view`):
- `#2390` — OPEN — epic(knowledge): llm-wiki strengthening roadmap and execution waves
- `#2392` — OPEN — feat(knowledge): wiki coverage-gap detector — inventory × wiki diff per discipline
- `#2487` — CLOSED — feat(inventory-readiness): raw-data to GTM readiness matrix and dispatch board
- `#2103` — OPEN — feat(llm-wiki): extend ingestion to AQWA and BEMRosetta documentation
- `#2124` — OPEN — feat(llm-wiki): extend ingestion to Orcina resources, examples, and training materials

**File/path existence and metadata-only findings**:
```text
/mnt/ace-data -> /mnt/ace
MISSING /mnt/ace-data/raw data
TOTAL_RAW_LIKE_DIRS=14
/mnt/ace-data/O&G-Standards/raw: files=28803 dirs=692
/mnt/ace-data/client_projects/energy_bsee/raw_data: files=10 dirs=0
/mnt/ace-data/digitalmodel/docs/aqwa/data/scripts/mooring_analysis/raw: files=28 dirs=0
/mnt/ace-data/digitalmodel/docs/orcaflex/literature/examples/raw: files=38 dirs=76
/mnt/ace-data/frontierdeepwater/data/raw: files=4 dirs=1
/mnt/ace-data/worldenergydata/data/modules/hse/raw: files=97 dirs=7

Frozen inventory roots for implementation:
1. /mnt/ace-data/O&G-Standards/raw
2. /mnt/ace-data/aceengineercode/data/raw
3. /mnt/ace-data/build/codex-desktop/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/hashbrown-0.16.1/src/raw
4. /mnt/ace-data/client_projects/energy_bsee/raw_data
5. /mnt/ace-data/data/archive/acematrix-admin/AceMatrix/2000 Projects/2001 Engineering/AceEngineer/Programs/struts-2.0.14-all/struts-2.0.14/docs/docs/images/raw
6. /mnt/ace-data/data/archive/acematrix-admin/AceMatrix/2000 Projects/2001 Engineering/Superseeded/AceEngineer/NetBeansProjects/struts-2.1.6/docs/docs/images/raw
7. /mnt/ace-data/digitalmodel/docs/aqwa/data/scripts/mooring_analysis/raw
8. /mnt/ace-data/digitalmodel/docs/orcaflex/literature/examples/raw
9. /mnt/ace-data/digitalmodel/docs/qgis/data/project1/outputs/elevation/raw
10. /mnt/ace-data/docs/disciplines/misc/projects/0133_ssi_marketing/00_inbox/0133 SSI Marketing/Phase1/Images/Raw
11. /mnt/ace-data/docs/disciplines/misc/projects/0136_das/00_inbox/0136 DAS/Data/Raw
12. /mnt/ace-data/frontierdeepwater/data/raw
13. /mnt/ace-data/opm-common/opm/input/eclipse/Parser/raw
14. /mnt/ace-data/worldenergydata/data/modules/hse/raw
```

**Index prefix coverage proof**:
```text
/mnt/ace-data/O&G-Standards/raw -> index_records 0
/mnt/ace-data/client_projects/energy_bsee/raw_data -> index_records 0
/mnt/ace-data/digitalmodel/docs/aqwa/data/scripts/mooring_analysis/raw -> index_records 0
/mnt/ace-data/digitalmodel/docs/orcaflex/literature/examples/raw -> index_records 0
/mnt/ace-data/frontierdeepwater/data/raw -> index_records 0
/mnt/ace-data/worldenergydata/data/modules/hse/raw -> index_records 0
/mnt/ace-data/docs/disciplines/misc/projects/0136_das/.../Data/Raw -> index_records 72; repo=acma-projects; status=gap
```

**Plan duplicate search proof**:
```text
docs/plans grep ace-data -> 0 hits
docs/plans grep O&G-Standards/raw -> 0 hits
docs/plans grep energy_bsee -> 0 hits
docs/plans grep worldenergydata/data/modules/hse/raw -> 0 hits
docs/plans grep frontierdeepwater/data/raw -> 0 hits
docs/plans grep orcaflex/literature/examples/raw -> 0 hits
docs/plans grep aqwa/data/scripts/mooring_analysis/raw -> 0 hits
```

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-04-issue-2643-llm-wiki-rawlike-source-triage.md` |
| Frozen metadata-only inventory snapshot | `data/document-index/ace-data-raw-like-inventory-2026-05-04.yaml` |
| Proposed raw-like routing matrix | `docs/document-intelligence/raw-like-source-routing.md` |
| Proposed machine-readable sidecar | `data/document-index/raw-like-source-routing.yaml` |
| Tests/checks | `tests/document_index/test_raw_like_source_routing.py` or equivalent no-raw-content validation test |
| Plan review — Claude | `scripts/review/results/2026-05-04-plan-2643-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-04-plan-2643-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-04-plan-2643-gemini.md` |

---

## Deliverable

A metadata-only raw-like source routing matrix and machine-readable sidecar will classify all discovered `/mnt/ace-data` raw-like roots by source family, target wiki/domain, existing issue mapping, sensitivity/exclusion status, and recommended next action without copying or promoting raw content.

---

## Pseudocode

```text
load frozen inventory from data/document-index/ace-data-raw-like-inventory-2026-05-04.yaml
assert inventory contains exactly the 14 planning-time raw-like roots
for each root:
    normalize alias path (/mnt/ace-data -> /mnt/ace) and preserve display path
    use frozen file_count/dir_count/extension metadata; do not read raw file contents
    classify routing_outcome = candidate | issue_mapped | excluded | approval_gated_sensitive
    assign exactly one primary_issue_ref or primary_decision_owner for every root
    assign related_issue_refs[] with typed relation enum:
        owned_by | feeds | excluded_overlap | approval_precedent | completed_precedent | roadmap_anchor
    fail if a root has multiple primary ownership decisions
    fail if a candidate root is already owned/excluded by an existing issue family
    write docs table row and YAML sidecar row
validate sidecar schema, allowed classifications, mutually-exclusive routing outcomes, and raw-content-free fields
fail if row includes raw text excerpts, file contents, secrets, or unapproved project terms
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `data/document-index/ace-data-raw-like-inventory-2026-05-04.yaml` | Frozen metadata-only inventory snapshot for the 14 planning-time roots; path/count/extension metadata only |
| Create | `docs/document-intelligence/raw-like-source-routing.md` | Human-readable metadata-only routing matrix and rationale |
| Create | `data/document-index/raw-like-source-routing.yaml` | Machine-readable routing sidecar for #2392/#2487-style downstream use |
| Create | `tests/document_index/test_raw_like_source_routing.py` | Verify schema, full inventory coverage, allowed classifications, and no raw-content fields |
| Update | `docs/document-intelligence/data-intelligence-map.md` | Add pointer to raw-like routing artifact |
| Update | `docs/plans/README.md` | Add this plan to the plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_raw_like_routing_schema_valid` | YAML sidecar has required fields and allowed enum values | sidecar rows | all rows validate |
| `test_frozen_inventory_contains_14_roots` | frozen snapshot enumerates every planning-time raw-like root exactly once | `ace-data-raw-like-inventory-2026-05-04.yaml` | 14 unique roots |
| `test_raw_like_routing_covers_inventory` | every frozen raw-like root is present in routing | 14 known metadata-only roots | no missing roots |
| `test_raw_like_routing_has_no_raw_content` | routing sidecar/docs do not include raw excerpts or extracted content | generated artifacts | only path/count/type/routing metadata allowed |
| `test_sensitive_sources_are_approval_gated` | ACMA/DAS/project/client-like roots are not candidate-promoted by default | sensitive path examples | classification is approval-gated or excluded |
| `test_existing_issue_mappings_present` | AQWA/OrcaFlex/O&G standards/Elements mappings point to existing issues | known path families | #2103/#2124/#2364/#2373/#2392/#2487/#2540-family are present |
| `test_each_root_has_single_primary_owner` | typed mapping prevents duplicate issue ownership | routing rows | exactly one primary decision per root |
| `test_candidate_roots_not_already_owned_elsewhere` | candidate rows cannot also be owned/excluded by another issue family | routing rows | mutually-exclusive routing outcomes |

---

## Acceptance Criteria

- [ ] A frozen metadata-only inventory artifact enumerates all 14 planning-time raw-like roots and becomes the canonical input for this issue.
- [ ] The routing matrix covers all 14 frozen raw-like roots using metadata only.
- [ ] Every row has `source_path`, `real_path`, `file_count`, `dir_count`, `dominant_extensions`, `routing_outcome`, `target_domain`, `primary_issue_ref` or `primary_decision_owner`, typed `related_issue_refs[]`, `sensitivity`, and `next_action`.
- [ ] Candidate rows distinguish direct llm-wiki candidates from issue-mapped families and exclusions, and no row has more than one primary owner.
- [ ] Project/client/personal/generated/vendor/code-internal raw-like roots are not promoted as general wiki candidates.
- [ ] Tests/checks prove the artifacts are schema-valid, raw-content-free, and mutually exclusive by ownership/routing outcome.
- [ ] GitHub comments link #2643 back to #2390, #2392, and #2487.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR → RESOLVED_TO_APPROVAL_READY | Review required a canonical frozen inventory, typed issue-mapping relations, duplicate-prevention tests, and enforceable discovery behavior. The plan now adds those contracts. |
| Codex | UNAVAILABLE_NOT_BLOCKING | Codex CLI remains blocked by #2479 stdin-hang/version issue; no Codex review was claimed. |
| Gemini | UNAVAILABLE_NOT_BLOCKING | Gemini review was not completed in this session; rerun path remains `scripts/review/plan-review-fanout.sh --providers=gemini docs/plans/2026-05-04-issue-2643-llm-wiki-rawlike-source-triage.md`. |

**Overall result:** PASS after revision — approval-ready with provider limitations recorded.

Revisions made based on review:
- Added a frozen metadata-only inventory artifact as the canonical source of truth for the 14 planning-time roots.
- Added typed issue mappings (`primary_issue_ref`, typed `related_issue_refs[]`) and mutually-exclusive ownership tests.
- Made duplicate-prevention an acceptance criterion instead of a narrative-only claim.
- Explicitly treated exact `/mnt/ace-data/raw data` as missing and `/mnt/ace-data` as alias to `/mnt/ace`.

---

## Risks and Open Questions

- **Risk:** raw-like directories may drift as external mounts change; the implementation should record discovery timestamp and avoid assuming a permanent count.
- **Risk:** O&G standards raw contains proprietary/copyrighted material; only metadata/routing is in scope.
- **Risk:** project-sensitive/client material may contain useful engineering knowledge but must remain approval-gated until separately authorized.
- **Open:** after this routing artifact is approved and implemented, user should choose which candidate families receive separate extraction/backfill package issues first.

---

## Complexity: T2

**T2** — creates docs + YAML metadata artifacts plus validation tests, with no raw extraction or wiki implementation in this issue.
