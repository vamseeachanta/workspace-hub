# Plan for #2644: offshore raw-source family wiki backfill candidates

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-05-04
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2644
> **Review artifacts:** scripts/review/results/2026-05-04-plan-2644-claude.md | scripts/review/results/2026-05-04-plan-2644-codex.md | scripts/review/results/2026-05-04-plan-2644-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `data/document-index/index.jsonl` has no records under the selected `/mnt/ace-data/client_projects/energy_bsee/raw_data`, `/mnt/ace-data/worldenergydata/data/modules/hse/raw`, or `/mnt/ace-data/frontierdeepwater/data/raw` prefixes, so these families are not yet represented in the current index by those local raw-like paths.
- Found: `docs/document-intelligence/data-intelligence-map.md` provides the document-intelligence artifact map that future source summaries should reference.
- Gap to address after approval: no current plan or issue will directly scope the three offshore raw-source families as bounded, approval-gated llm-wiki backfill candidates.

### Standards
| Source family | Status | Source |
|---|---|---|
| BSEE/offshore local raw data | Gap / candidate package | `/mnt/ace-data/client_projects/energy_bsee/raw_data`; focused issue search found no direct duplicate |
| HSE/safety datasets | Gap / candidate package | `/mnt/ace-data/worldenergydata/data/modules/hse/raw`; focused issue search found no direct duplicate |
| Frontier Deepwater offshore operations PDFs | Gap / candidate package | `/mnt/ace-data/frontierdeepwater/data/raw`; focused issue search found no direct duplicate |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/` — candidate target for BSEE/HSE/offshore operations source summaries and concepts.
- `knowledge/wikis/marine-engineering/` — candidate target for offshore operations and marine execution context, subject to source-family approval.
- `knowledge/wikis/engineering-standards/` — not the primary target for this issue; standards raw work is explicitly routed elsewhere.

### Documents consulted
- Issue #2644 — asks for an approval-ready plan for the BSEE, HSE, and Frontier Deepwater raw-source family candidates.
- Issue #2643 — companion routing issue that will classify all raw-like roots and keep this issue from becoming a global raw-data umbrella.
- Issue #2390 — open llm-wiki roadmap umbrella.
- Issue #2392 — open coverage-gap detector; future implementation should consume/emit compatible source-family gap metadata.
- Issue #2487 — closed raw-data-to-readiness spine/control-plane; this issue will reuse the metadata-first, gap-to-dispatch principle.
- Issues #2103 and #2124 — adjacent AQWA/OrcaFlex ingestion anchors, confirming those local raw folders are out of this issue's scope.
- `docs/sessions/2026-05-02-llm-wiki-completeness-loop.md` — raw-data boundary and no-self-approval constraints.

### Gaps identified
- No BSEE/offshore raw-source family package plan exists.
- No HSE/safety raw-source family package plan exists.
- No Frontier Deepwater/offshore operations raw-source family package plan exists.
- No approval-gated sequencing matrix currently states which derived pages/summaries would be proposed for these families and which raw/project-sensitive inputs remain excluded.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-04 via `gh issue view`):
- `#2390` — OPEN — epic(knowledge): llm-wiki strengthening roadmap and execution waves
- `#2392` — OPEN — feat(knowledge): wiki coverage-gap detector — inventory × wiki diff per discipline
- `#2487` — CLOSED — feat(inventory-readiness): raw-data to GTM readiness matrix and dispatch board
- `#2103` — OPEN — feat(llm-wiki): extend ingestion to AQWA and BEMRosetta documentation
- `#2124` — OPEN — feat(llm-wiki): extend ingestion to Orcina resources, examples, and training materials

**Metadata-only source family findings**:
```text
/mnt/ace-data/client_projects/energy_bsee/raw_data: files=10 dirs=0 ext=.pdf/.xlsx/.zip/.docx
/mnt/ace-data/worldenergydata/data/modules/hse/raw: files=97 dirs=7 ext=.csv/.zip/.txt/.md/.sh
/mnt/ace-data/frontierdeepwater/data/raw: files=4 dirs=1 ext=.pdf/.md/.gitkeep
```

**Focused duplicate search proof**:
```text
gh issue list --search 'energy_bsee raw_data' -> no results
gh issue list --search 'worldenergydata hse llm-wiki' -> no results
gh issue list --search 'frontierdeepwater llm-wiki' -> no direct duplicate; returned portfolio/adjacent issues only
```

**Out-of-scope overlap proof**:
```text
gh issue list --search 'orcaflex examples raw llm-wiki' -> #2103, #2124, #2034, #2460
#2103 covers AQWA/BEMRosetta documentation; #2124 covers Orcina resources/examples/training.
```

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-04-issue-2644-llm-wiki-offshore-raw-source-family-backfill.md` |
| Prerequisite routing artifact | `data/document-index/raw-like-source-routing.yaml` from #2643 |
| Candidate package spec | `docs/document-intelligence/offshore-raw-source-family-packages.md` |
| Candidate package sidecar | `data/document-index/offshore-raw-source-family-packages.yaml` |
| Tests/checks | `tests/document_index/test_offshore_raw_source_family_packages.py` or equivalent validation test |
| Plan review — Claude | `scripts/review/results/2026-05-04-plan-2644-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-04-plan-2644-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-04-plan-2644-gemini.md` |

---

## Deliverable

An approval-gated offshore raw-source family package spec will define safe BSEE, HSE/safety, and Frontier Deepwater llm-wiki backfill candidates, including target domains, proposed derived summary/page types, exclusions, provenance gates, and sequencing without importing raw data.

---

## Pseudocode

```text
load #2643 output data/document-index/raw-like-source-routing.yaml as a hard prerequisite
fail if #2643 routing artifact is missing, not approved/implemented, or lacks the three selected family rows
select only BSEE, HSE/safety, and Frontier Deepwater family rows; do not rescan /mnt/ace-data
for each family:
    define target wiki domains and candidate page/source-summary types
    record allowed metadata fields and forbidden raw-content fields
    set sensitivity and approval_required fields explicitly
    default BSEE/client_projects family to sensitivity=client_project and approval_required=true
    list exclusions and approval gates for project/client-sensitive material
    define follow-up package sequencing and acceptance checks
write package markdown and YAML sidecar
validate schema, source-family uniqueness, no raw text, and no overlap with #2103/#2124/O&G standards packages
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/document-intelligence/offshore-raw-source-family-packages.md` | Human-readable source-family package definitions |
| Create | `data/document-index/offshore-raw-source-family-packages.yaml` | Machine-readable package queue for future approved extraction/backfill work |
| Create | `tests/document_index/test_offshore_raw_source_family_packages.py` | Verify package schema, no raw content, target-domain routing, and overlap exclusions |
| Update | `docs/document-intelligence/data-intelligence-map.md` | Add pointer to offshore source-family package artifact |
| Update | `docs/plans/README.md` | Add this plan to the plan index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_offshore_packages_schema_valid` | YAML package spec has required fields | package sidecar | all packages validate |
| `test_offshore_packages_requires_2643_routing` | implementation consumes #2643 routing and does not rescan raw mounts | missing/stale routing artifact | validation fails |
| `test_offshore_packages_only_selected_families` | scope is limited to BSEE, HSE, Frontier Deepwater | package sidecar | exactly those three families |
| `test_offshore_packages_no_raw_content` | no extracted file content, tables, or raw text appears | docs + YAML | only metadata/routing fields |
| `test_offshore_packages_have_approval_gates` | every family states approval requirement before promotion | package sidecar | all package rows include approval gate |
| `test_bsee_defaults_to_client_sensitive` | BSEE under `client_projects` is explicitly client/project-sensitive | BSEE package row | `sensitivity=client_project`, `approval_required=true` |
| `test_offshore_packages_do_not_overlap_existing_marine_ingestion` | AQWA/OrcaFlex/O&G standards are excluded from this issue | package sidecar | excluded refs point to #2103/#2124/#2364/#2373 |

---

## Acceptance Criteria

- [ ] The implementation treats #2643's routing artifact as a hard prerequisite and does not rescan `/mnt/ace-data` for this issue.
- [ ] The offshore package spec covers BSEE, HSE/safety, and Frontier Deepwater families only.
- [ ] Every package defines target domains, proposed derived outputs, exclusions, provenance requirements, sensitivity, and approval gate.
- [ ] No raw data, raw excerpts, or raw document contents are copied into git/wiki.
- [ ] The spec explicitly excludes AQWA, OrcaFlex examples, O&G standards, Elements/client-sensitive material, generated outputs, and code/vendor internals.
- [ ] Tests/checks prove schema validity, no raw-content fields, no direct mount rescan, and no overlap with existing issue-mapped families.
- [ ] The final evidence comment may link #2644 back to #2643, #2390, #2392, and #2487, but artifact correctness is the deliverable gate.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR → RESOLVED_TO_APPROVAL_READY | Review required future-tense/gate hygiene, hard dependency on #2643 output, and first-class BSEE sensitivity/approval fields. The plan now adds those contracts. |
| Codex | UNAVAILABLE_NOT_BLOCKING | Codex CLI remains blocked by #2479 stdin-hang/version issue; no Codex review was claimed. |
| Gemini | UNAVAILABLE_NOT_BLOCKING | Gemini review was not completed in this session; rerun path remains `scripts/review/plan-review-fanout.sh --providers=gemini docs/plans/2026-05-04-issue-2644-llm-wiki-offshore-raw-source-family-backfill.md`. |

**Overall result:** PASS after revision — approval-ready with provider limitations recorded.

Revisions made based on review:
- Made #2643's raw-like routing artifact a hard prerequisite and prohibited rescanning `/mnt/ace-data` inside this issue.
- Narrowed the plan to BSEE/HSE/Frontier only; AQWA, OrcaFlex, and O&G standards are explicitly excluded and mapped elsewhere.
- Added required `sensitivity` / `approval_required` fields and a BSEE client-sensitive default test.
- Added tests that enforce no raw content and approval gates per family.
- Added duplicate-search evidence to avoid creating a replacement umbrella.

---

## Risks and Open Questions

- **Risk:** BSEE and HSE material may be better handled as datasets than wiki prose; implementation should propose metadata/source pages first and defer deeper extraction to separate approved issues.
- **Risk:** Frontier Deepwater source files may include copyrighted magazine content; derived summaries must remain bounded and provenance-safe.
- **Open:** user should decide after plan approval whether these package specs become execution work directly or spawn separate per-family extraction/backfill issues.

---

## Complexity: T2

**T2** — creates bounded source-family package artifacts plus validation tests; no raw extraction, code-generation, or wiki promotion occurs in this issue.
