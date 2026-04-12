# Plan for #2227: Promote OCIMF Tandem Mooring and CSA Z276 Coverage into LLM-Wikis

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-12
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2227
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2216
> **Review artifacts:** scripts/review/results/2026-04-12-plan-2227-review-a.md | scripts/review/results/2026-04-12-plan-2227-review-b.md | scripts/review/results/2026-04-12-plan-2227-final.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — existing OCIMF standard page that can be updated with narrowly grounded historical/provenance context only.
- Found: `knowledge/wikis/engineering/wiki/index.md` and `knowledge/wikis/engineering/wiki/log.md` — existing engineering wiki navigation/update surfaces that must be updated if the OCIMF page set changes.
- Found: `knowledge/wikis/marine-engineering/wiki/index.md` and `knowledge/wikis/marine-engineering/wiki/log.md` — existing marine-engineering wiki navigation/update surfaces; no `wiki/standards/` directory currently exists, so this issue likely needs to create it.
- Gap: no existing wiki pages found for `ocimf-tandem-mooring`, `csa-z276-1`, or `csa-z276-18`.

### Standards
| Standard | Status | Source |
|---|---|---|
| `OCIMF-TANDEM-MOORING` | done in ledger; no wiki page yet | `data/document-index/standards-transfer-ledger.yaml` |
| `OCIMF-MEG4-2018` | done in ledger; existing wiki page present | `data/document-index/standards-transfer-ledger.yaml` + `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` |
| `OCIMF-MEG-3RD-ED-2008` | done in ledger; historical predecessor for MEG4 context | `data/document-index/standards-transfer-ledger.yaml` |
| `CSA-Z276.1-20` | done in ledger; no wiki page yet | `data/document-index/standards-transfer-ledger.yaml` |
| `CSA-Z276.18` | done in ledger; no wiki page yet | `data/document-index/standards-transfer-ledger.yaml` |
| `CSA-Z276.2-19` | done in ledger but explicitly out of scope for this issue | `data/document-index/standards-transfer-ledger.yaml` + `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md` |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — current page structure, cross-links, and claims to preserve/update narrowly.
- `knowledge/wikis/engineering/wiki/index.md` — engineering standards section currently includes `OCIMF MEG4`.
- `knowledge/wikis/engineering/wiki/log.md` — existing log format for incremental-ingest updates.
- `knowledge/wikis/marine-engineering/wiki/index.md` — marine-engineering wiki currently has entities/concepts/sources only; no standards section visible in current index state.
- `knowledge/wikis/marine-engineering/CLAUDE.md` and `knowledge/wikis/engineering/CLAUDE.md` — wiki conventions, frontmatter expectations, and parent operating-model linkage.

### Documents consulted
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` — parent approved plan identified OCIMF Tandem Mooring, CSA Z276.1-20, and CSA Z276.18 as the bounded promotion candidates.
- `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md` — authoritative source for ledger-backed IDs, path evidence, and explicit out-of-scope breadth discovered after indexing.
- `docs/plans/README.md` — confirms there was no canonical #2227 plan row before this planning recovery; this run creates it.
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` — provenance back-link expectations; promotion should consume ledger evidence, not raw reparse.
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` — durable L3 wiki promotion must stay separate from transient issue-tracking state.
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — issue must consume L2/L3 evidence into L3 wiki surfaces without redefining parent contracts.
- GitHub issue #2227 — bounded scope and acceptance criteria.
- GitHub issue #2216 comment chain — umbrella status and recommendation that #2227 remains blocked until canonical planning state is reconciled.

### Gaps identified
- No canonical repo-tracked plan artifact exists yet for #2227.
- No existing wiki pages exist for OCIMF Tandem Mooring, CSA Z276.1-20, or CSA Z276.18.
- Marine-engineering wiki appears to lack a current `wiki/standards/` surface, so this issue likely needs to create both the directory content and index references.
- The plan has not yet proved that all target documents satisfy #2207 wiki-promotion prerequisites (`summaries/<doc_key>.json` present and non-empty, valid domain classification, no conflicting wiki page) — implementation must verify this before any promotion write.
- The broader CSA/API breadth discovered in #2226 must not be silently absorbed here.

<!-- Verification: distinct sources consulted = 9+ (issue #2227, issue #2216, #2216 plan, #2226 plan, standards ledger, ocimf-meg4.md, engineering index/log, marine-engineering index, wiki CLAUDE.md, parent/provenance/boundary docs). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` |
| Plan review A | `scripts/review/results/2026-04-12-plan-2227-review-a.md` |
| Plan review B | `scripts/review/results/2026-04-12-plan-2227-review-b.md` |
| Review synthesis | `scripts/review/results/2026-04-12-plan-2227-final.md` |
| New engineering wiki page | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` |
| Updated engineering wiki page | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` |
| Engineering index/log updates | `knowledge/wikis/engineering/wiki/index.md`, `knowledge/wikis/engineering/wiki/log.md` |
| New marine wiki pages | `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md`, `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-18.md` |
| Marine index/log updates | `knowledge/wikis/marine-engineering/wiki/index.md`, `knowledge/wikis/marine-engineering/wiki/log.md` |
| Parent issue summary | GitHub issue `#2216` comment |

---

## Deliverable

Bounded, provenance-backed L3 wiki promotion for OCIMF Tandem Mooring, CSA Z276.1-20, and CSA Z276.18, plus a narrowly grounded historical update to `ocimf-meg4.md`, all reflected in the affected wiki indexes and logs without absorbing out-of-scope CSA/API breadth, contingent on verifying #2207 promotion prerequisites or explicitly stopping on missing L2 artifacts.

---

## Scope Boundaries

### In scope now
- Create `ocimf-tandem-mooring.md` in the engineering wiki.
- Create `csa-z276-1.md` and `csa-z276-18.md` in the marine-engineering wiki.
- Update `ocimf-meg4.md` only with historically/provenance-grounded context from ledger-backed evidence.
- Update engineering and marine-engineering wiki indexes/logs accordingly.
- Use provenance back-links consistent with #2207.
- Verify before any write that each target document has the minimum reusable L2 artifacts required by #2207 (`doc_key`, non-empty summary artifact, valid domain classification) or stop and comment the blocker instead of guessing.
- Verify whether `knowledge/wikis/marine-engineering/wiki/standards/` is acceptable within local conventions; if not, stop and document the convention gap rather than silently inventing a taxonomy change.

### Explicitly out of scope
- Promotion of `CSA-Z276.2-19`, `CSA-B625-13`, `CSA-22.1-12`, or broader API-family documents.
- Accessibility-map or entry-point work (belongs to #2228 / already completed).
- Registry-schema or ledger-schema changes.
- Raw-document reparsing when ledger evidence is sufficient.
- Downstream code-registry or repo-implementation work.

---

## Pseudocode

```text
for each approved promotion target:
    verify #2207 promotion prerequisites:
        doc is registered
        summary artifact exists and is non-empty
        domain classification exists
        no conflicting wiki page already makes incompatible claims
    if any prerequisite is missing:
        stop implementation for that target
        report blocker in GitHub comment / follow-up issue

for each approved promotion target in [OCIMF-TANDEM-MOORING, CSA-Z276.1-20, CSA-Z276.18]:
    read corresponding ledger entry and path evidence from standards-transfer-ledger
    derive page title, scope summary, and provenance back-links from ledger-backed facts
    create wiki page in target domain with required frontmatter and cross-links

before creating marine-engineering standards pages:
    verify local schema/conventions permit wiki/standards/
    if conventions do not clearly permit it:
        stop and document minimal follow-up instead of broadening scope

read existing ocimf-meg4.md:
    preserve current MEG4-oriented content
    add only bounded historical comparison to MEG 3rd Ed / tandem context where ledger evidence supports it
    avoid unsupported operational or implementation claims

update engineering and marine-engineering wiki indexes:
    add standards-section entries for new/updated pages
    update page_count / last_updated fields if maintained manually

append log entries:
    record promotion source, pages created/updated, and bounded-scope note

verify:
    all new pages exist
    provenance back-links present
    index references resolve
    no out-of-scope pages were created
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` | net-new OCIMF guideline promotion |
| Modify | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` | add narrowly grounded historical/provenance context |
| Modify | `knowledge/wikis/engineering/wiki/index.md` | index entry for new/updated engineering standards pages |
| Modify | `knowledge/wikis/engineering/wiki/log.md` | promotion log entry |
| Create | `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md` | net-new marine standard promotion |
| Create | `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-18.md` | net-new marine standard promotion |
| Modify | `knowledge/wikis/marine-engineering/wiki/index.md` | standards section / page references |
| Modify | `knowledge/wikis/marine-engineering/wiki/log.md` | promotion log entry |

---

## TDD / Verification List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_l2_prerequisites_ready | each target satisfies #2207 promotion prerequisites | target doc ids / refs | registered doc, non-empty summary artifact, valid domain classification |
| verify_marine_wiki_structure_allowed | marine-engineering conventions support chosen target path | local schema + current structure | standards directory/path accepted or explicit blocker raised |
| verify_ocimf_tandem_page_exists | new engineering standard page exists | target path | file present with frontmatter |
| verify_csa_pages_exist | new marine standards pages exist | target paths | files present with frontmatter |
| verify_provenance_backlinks_present | all new/updated pages cite concrete provenance fields | page content | explicit `doc_key`, `source_ref`, `domain`, `promoted_from` fields or documented approved equivalent |
| verify_ocimf_meg4_scope_is_narrow | update did not replace MEG4 page focus with unrelated content | `ocimf-meg4.md` diff | historical/provenance additions only |
| verify_engineering_index_links | engineering wiki index references resolve to standards pages | `engineering/wiki/index.md` | links for OCIMF MEG4 + tandem page |
| verify_marine_index_links | marine wiki index references resolve to CSA pages | `marine-engineering/wiki/index.md` | links for CSA Z276.1 and Z276.18 |
| verify_no_out_of_scope_pages | no extra CSA/API pages were created | standards dirs | only approved target pages added |

---

## Acceptance Criteria

- [ ] Canonical plan artifact exists for #2227 and issue is moved into proper planning state before implementation.
- [ ] Each target document satisfies #2207 promotion prerequisites before any wiki write, or execution stops with a clear blocker comment instead of guessing.
- [ ] `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` exists with provenance back-links.
- [ ] `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md` and `csa-z276-18.md` exist with provenance back-links.
- [ ] `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` is updated only where warranted by ledger-backed evidence.
- [ ] Engineering and marine-engineering indexes/logs reflect the new pages.
- [ ] No out-of-scope CSA/API breadth is promoted in this issue.
- [ ] Parent issue #2216 receives an implementation summary comment if execution occurs.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Review A | REVISE | Bounded scope is correct, but #2207 promotion prerequisites are not yet demonstrably satisfied for the target docs. |
| Review B | MINOR / conditional | Plan improvements are directionally correct, but current repo state still indicates missing summary/classification artifacts and unresolved marine standards-surface convention. |

**Overall result:** FAIL for execution readiness in current repo state; keep as planning-recovery artifact and use it to drive the prerequisite unblock step.

Revisions made based on review:
- Added explicit #2207 prerequisite verification before any wiki write.
- Added stronger provenance-field verification expectations.
- Added explicit stop/blocker behavior when summary/classification artifacts are missing.
- Removed unnecessary implementation-scope update to `docs/plans/README.md`.

---

## Risks and Open Questions

- **Risk:** implementation may discover that summary artifacts or valid classifications for the target docs are missing; in that case this issue must stop rather than promote from insufficient evidence.
- **Risk:** marine-engineering wiki currently has no explicit standards section/dir in the indexed structure; implementation must add this carefully without damaging the large index file.
- **Risk:** wiki content under `knowledge/wikis/` is gitignored by default; execution must force-add the intended wiki files only.
- **Risk:** ocimf-meg4 historical additions could drift beyond evidence if the updater over-infers from issue/plan prose rather than the ledger.
- **Open:** should the new marine pages live under `wiki/standards/` or a different folder if marine-engineering conventions diverge? Current best evidence favors `wiki/standards/` for consistency with the issue intent, but implementation must verify local conventions before writing.
- **Open:** if required summary artifacts are absent, is the correct next action a blocker comment only, or a small prerequisite follow-on issue under #2207 / #2216? Current plan assumes blocker comment plus follow-on recommendation.

---

## Complexity: T2

**T2** — multi-file wiki/documentation promotion with bounded evidence-driven content creation, index/log updates across two wiki domains, and strict scope control against newly discovered adjacent breadth.
