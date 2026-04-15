# Adversarial Plan Review Request: Issue #2227

Review the CURRENT plan text only. Be adversarial and concrete. Identify any unresolved blockers, governance drift, missing retrieval, non-falsifiable acceptance criteria, hidden taxonomy decisions, or approval-readiness gaps.

Return exactly these sections:
1. Overall verdict: APPROVE | MINOR | MAJOR
2. Ready for user approval: Yes | No
3. Retrieval adequacy: adequate | insufficient
4. Top blockers
5. Critical findings
6. High findings
7. Medium findings
8. Low findings
9. Required revisions before user approval

Plan under review:

```markdown
     1|# Plan for #2227: Promote OCIMF Tandem Mooring and CSA Z276 Coverage into LLM-Wikis
     2|
     3|> **Status:** draft
     4|> **Complexity:** T2
     5|> **Date:** 2026-04-12
     6|> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2227
     7|> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2216
     8|> **Review artifacts:** scripts/review/results/2026-04-12-plan-2227-review-a.md | scripts/review/results/2026-04-12-plan-2227-review-b.md | scripts/review/results/2026-04-12-plan-2227-final.md
     9|
    10|---
    11|
    12|## Resource Intelligence Summary
    13|
    14|### Existing repo code
    15|- Found: `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — existing OCIMF standard page that can be updated with narrowly grounded historical/provenance context only.
    16|- Found: `knowledge/wikis/engineering/wiki/index.md` and `knowledge/wikis/engineering/wiki/log.md` — existing engineering wiki navigation/update surfaces that must be updated if the OCIMF page set changes.
    17|- Found: `knowledge/wikis/marine-engineering/wiki/index.md` and `knowledge/wikis/marine-engineering/wiki/log.md` — existing marine-engineering wiki navigation/update surfaces; no `wiki/standards/` directory currently exists, so this issue likely needs to create it.
    18|- Gap: no existing wiki pages found for `ocimf-tandem-mooring`, `csa-z276-1`, or `csa-z276-18`.
    19|
    20|### Standards
    21|| Standard | Status | Source |
    22||---|---|---|
    23|| `OCIMF-TANDEM-MOORING` | done in ledger; no wiki page yet | `data/document-index/standards-transfer-ledger.yaml` |
    24|| `OCIMF-MEG4-2018` | done in ledger; existing wiki page present | `data/document-index/standards-transfer-ledger.yaml` + `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` |
    25|| `OCIMF-MEG-3RD-ED-2008` | done in ledger; historical predecessor for MEG4 context | `data/document-index/standards-transfer-ledger.yaml` |
    26|| `CSA-Z276.1-20` | done in ledger; no wiki page yet | `data/document-index/standards-transfer-ledger.yaml` |
    27|| `CSA-Z276.18` | done in ledger; no wiki page yet | `data/document-index/standards-transfer-ledger.yaml` |
    28|| `CSA-Z276.2-19` | done in ledger but explicitly out of scope for this issue | `data/document-index/standards-transfer-ledger.yaml` + `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md` |
    29|
    30|### LLM Wiki pages consulted
    31|- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — current page structure, cross-links, and claims to preserve/update narrowly.
    32|- `knowledge/wikis/engineering/wiki/index.md` — engineering standards section currently includes `OCIMF MEG4`.
    33|- `knowledge/wikis/engineering/wiki/log.md` — existing log format for incremental-ingest updates.
    34|- `knowledge/wikis/marine-engineering/wiki/index.md` — marine-engineering wiki currently has entities/concepts/sources only; no standards section visible in current index state.
    35|- `knowledge/wikis/marine-engineering/CLAUDE.md` and `knowledge/wikis/engineering/CLAUDE.md` — wiki conventions, frontmatter expectations, and parent operating-model linkage.
    36|
    37|### Documents consulted
    38|- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` — parent approved plan identified OCIMF Tandem Mooring, CSA Z276.1-20, and CSA Z276.18 as the bounded promotion candidates.
    39|- `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md` — authoritative source for ledger-backed IDs, path evidence, and explicit out-of-scope breadth discovered after indexing.
    40|- `docs/plans/README.md` — confirms there was no canonical #2227 plan row before this planning recovery; this run creates it.
    41|- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` — provenance back-link expectations; promotion should consume ledger evidence, not raw reparse.
    42|- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` — durable L3 wiki promotion must stay separate from transient issue-tracking state.
    43|- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — issue must consume L2/L3 evidence into L3 wiki surfaces without redefining parent contracts.
    44|- GitHub issue #2227 — bounded scope and acceptance criteria.
    45|- GitHub issue #2216 comment chain — umbrella status and recommendation that #2227 remains blocked until canonical planning state is reconciled.
    46|
    47|### Gaps identified
    48|- No canonical repo-tracked plan artifact exists yet for #2227.
    49|- No existing wiki pages exist for OCIMF Tandem Mooring, CSA Z276.1-20, or CSA Z276.18.
    50|- Marine-engineering wiki appears to lack a current `wiki/standards/` surface, so this issue likely needs to create both the directory content and index references.
    51|- The plan has not yet proved that all target documents satisfy #2207 wiki-promotion prerequisites (`summaries/<doc_key>.json` present and non-empty, valid domain classification, no conflicting wiki page) — implementation must verify this before any promotion write.
    52|- The broader CSA/API breadth discovered in #2226 must not be silently absorbed here.
    53|
    54|<!-- Verification: distinct sources consulted = 9+ (issue #2227, issue #2216, #2216 plan, #2226 plan, standards ledger, ocimf-meg4.md, engineering index/log, marine-engineering index, wiki CLAUDE.md, parent/provenance/boundary docs). -->
    55|
    56|---
    57|
    58|## Artifact Map
    59|
    60|| Artifact | Path |
    61||---|---|
    62|| This plan | `docs/plans/2026-04-12-issue-2227-ocimf-tandem-csa-z276-wiki-promotion.md` |
    63|| Plan review A | `scripts/review/results/2026-04-12-plan-2227-review-a.md` |
    64|| Plan review B | `scripts/review/results/2026-04-12-plan-2227-review-b.md` |
    65|| Review synthesis | `scripts/review/results/2026-04-12-plan-2227-final.md` |
    66|| New engineering wiki page | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` |
    67|| Updated engineering wiki page | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` |
    68|| Engineering index/log updates | `knowledge/wikis/engineering/wiki/index.md`, `knowledge/wikis/engineering/wiki/log.md` |
    69|| New marine wiki pages | `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md`, `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-18.md` |
    70|| Marine index/log updates | `knowledge/wikis/marine-engineering/wiki/index.md`, `knowledge/wikis/marine-engineering/wiki/log.md` |
    71|| Parent issue summary | GitHub issue `#2216` comment |
    72|
    73|---
    74|
    75|## Deliverable
    76|
    77|Bounded, provenance-backed L3 wiki promotion for OCIMF Tandem Mooring, CSA Z276.1-20, and CSA Z276.18, plus a narrowly grounded historical update to `ocimf-meg4.md`, all reflected in the affected wiki indexes and logs without absorbing out-of-scope CSA/API breadth, contingent on verifying #2207 promotion prerequisites or explicitly stopping on missing L2 artifacts.
    78|
    79|---
    80|
    81|## Scope Boundaries
    82|
    83|### In scope now
    84|- Create `ocimf-tandem-mooring.md` in the engineering wiki.
    85|- Create `csa-z276-1.md` and `csa-z276-18.md` in the marine-engineering wiki.
    86|- Update `ocimf-meg4.md` only with historically/provenance-grounded context from ledger-backed evidence.
    87|- Update engineering and marine-engineering wiki indexes/logs accordingly.
    88|- Use provenance back-links consistent with #2207.
    89|- Verify before any write that each target document has the minimum reusable L2 artifacts required by #2207 (`doc_key`, non-empty summary artifact, valid domain classification) or stop and comment the blocker instead of guessing.
    90|- Verify whether `knowledge/wikis/marine-engineering/wiki/standards/` is acceptable within local conventions; if not, stop and document the convention gap rather than silently inventing a taxonomy change.
    91|
    92|### Explicitly out of scope
    93|- Promotion of `CSA-Z276.2-19`, `CSA-B625-13`, `CSA-22.1-12`, or broader API-family documents.
    94|- Accessibility-map or entry-point work (belongs to #2228 / already completed).
    95|- Registry-schema or ledger-schema changes.
    96|- Raw-document reparsing when ledger evidence is sufficient.
    97|- Downstream code-registry or repo-implementation work.
    98|
    99|---
   100|
   101|## Pseudocode
   102|
   103|```text
   104|for each approved promotion target:
   105|    verify #2207 promotion prerequisites:
   106|        doc is registered
   107|        summary artifact exists and is non-empty
   108|        domain classification exists
   109|        no conflicting wiki page already makes incompatible claims
   110|    if any prerequisite is missing:
   111|        stop implementation for that target
   112|        report blocker in GitHub comment / follow-up issue
   113|
   114|for each approved promotion target in [OCIMF-TANDEM-MOORING, CSA-Z276.1-20, CSA-Z276.18]:
   115|    read corresponding ledger entry and path evidence from standards-transfer-ledger
   116|    derive page title, scope summary, and provenance back-links from ledger-backed facts
   117|    create wiki page in target domain with required frontmatter and cross-links
   118|
   119|before creating marine-engineering standards pages:
   120|    verify local schema/conventions permit wiki/standards/
   121|    if conventions do not clearly permit it:
   122|        stop and document minimal follow-up instead of broadening scope
   123|
   124|read existing ocimf-meg4.md:
   125|    preserve current MEG4-oriented content
   126|    add only bounded historical comparison to MEG 3rd Ed / tandem context where ledger evidence supports it
   127|    avoid unsupported operational or implementation claims
   128|
   129|update engineering and marine-engineering wiki indexes:
   130|    add standards-section entries for new/updated pages
   131|    update page_count / last_updated fields if maintained manually
   132|
   133|append log entries:
   134|    record promotion source, pages created/updated, and bounded-scope note
   135|
   136|verify:
   137|    all new pages exist
   138|    provenance back-links present
   139|    index references resolve
   140|    no out-of-scope pages were created
   141|```
   142|
   143|---
   144|
   145|## Files to Change
   146|
   147|| Action | Path | Reason |
   148||---|---|---|
   149|| Create | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` | net-new OCIMF guideline promotion |
   150|| Modify | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` | add narrowly grounded historical/provenance context |
   151|| Modify | `knowledge/wikis/engineering/wiki/index.md` | index entry for new/updated engineering standards pages |
   152|| Modify | `knowledge/wikis/engineering/wiki/log.md` | promotion log entry |
   153|| Create | `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md` | net-new marine standard promotion |
   154|| Create | `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-18.md` | net-new marine standard promotion |
   155|| Modify | `knowledge/wikis/marine-engineering/wiki/index.md` | standards section / page references |
   156|| Modify | `knowledge/wikis/marine-engineering/wiki/log.md` | promotion log entry |
   157|
   158|---
   159|
   160|## TDD / Verification List
   161|
   162|| Test name | What it verifies | Expected input | Expected output |
   163||---|---|---|---|
   164|| verify_l2_prerequisites_ready | each target satisfies #2207 promotion prerequisites | target doc ids / refs | registered doc, non-empty summary artifact, valid domain classification |
   165|| verify_marine_wiki_structure_allowed | marine-engineering conventions support chosen target path | local schema + current structure | standards directory/path accepted or explicit blocker raised |
   166|| verify_ocimf_tandem_page_exists | new engineering standard page exists | target path | file present with frontmatter |
   167|| verify_csa_pages_exist | new marine standards pages exist | target paths | files present with frontmatter |
   168|| verify_provenance_backlinks_present | all new/updated pages cite concrete provenance fields | page content | explicit `doc_key`, `source_ref`, `domain`, `promoted_from` fields or documented approved equivalent |
   169|| verify_ocimf_meg4_scope_is_narrow | update did not replace MEG4 page focus with unrelated content | `ocimf-meg4.md` diff | historical/provenance additions only |
   170|| verify_engineering_index_links | engineering wiki index references resolve to standards pages | `engineering/wiki/index.md` | links for OCIMF MEG4 + tandem page |
   171|| verify_marine_index_links | marine wiki index references resolve to CSA pages | `marine-engineering/wiki/index.md` | links for CSA Z276.1 and Z276.18 |
   172|| verify_no_out_of_scope_pages | no extra CSA/API pages were created | standards dirs | only approved target pages added |
   173|
   174|---
   175|
   176|## Acceptance Criteria
   177|
   178|- [ ] Canonical plan artifact exists for #2227 and issue is moved into proper planning state before implementation.
   179|- [ ] Each target document satisfies #2207 promotion prerequisites before any wiki write, or execution stops with a clear blocker comment instead of guessing.
   180|- [ ] `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` exists with provenance back-links.
   181|- [ ] `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md` and `csa-z276-18.md` exist with provenance back-links.
   182|- [ ] `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` is updated only where warranted by ledger-backed evidence.
   183|- [ ] Engineering and marine-engineering indexes/logs reflect the new pages.
   184|- [ ] No out-of-scope CSA/API breadth is promoted in this issue.
   185|- [ ] Parent issue #2216 receives an implementation summary comment if execution occurs.
   186|
   187|---
   188|
   189|## Adversarial Review Summary
   190|
   191|| Provider | Verdict | Key findings |
   192||---|---|---|
   193|| Review A | REVISE | Bounded scope is correct, but #2207 promotion prerequisites are not yet demonstrably satisfied for the target docs. |
   194|| Review B | MINOR / conditional | Plan improvements are directionally correct, but current repo state still indicates missing summary/classification artifacts and unresolved marine standards-surface convention. |
   195|
   196|**Overall result:** FAIL for execution readiness in current repo state; keep as planning-recovery artifact and use it to drive the prerequisite unblock step.
   197|
   198|Revisions made based on review:
   199|- Added explicit #2207 prerequisite verification before any wiki write.
   200|- Added stronger provenance-field verification expectations.
   201|- Added explicit stop/blocker behavior when summary/classification artifacts are missing.
   202|- Removed unnecessary implementation-scope update to `docs/plans/README.md`.
   203|
   204|---
   205|
   206|## Risks and Open Questions
   207|
   208|- **Risk:** implementation may discover that summary artifacts or valid classifications for the target docs are missing; in that case this issue must stop rather than promote from insufficient evidence.
   209|- **Risk:** marine-engineering wiki currently has no explicit standards section/dir in the indexed structure; implementation must add this carefully without damaging the large index file.
   210|- **Risk:** wiki content under `knowledge/wikis/` is gitignored by default; execution must force-add the intended wiki files only.
   211|- **Risk:** ocimf-meg4 historical additions could drift beyond evidence if the updater over-infers from issue/plan prose rather than the ledger.
   212|- **Open:** should the new marine pages live under `wiki/standards/` or a different folder if marine-engineering conventions diverge? Current best evidence favors `wiki/standards/` for consistency with the issue intent, but implementation must verify local conventions before writing.
   213|- **Open:** if required summary artifacts are absent, is the correct next action a blocker comment only, or a small prerequisite follow-on issue under #2207 / #2216? Current plan assumes blocker comment plus follow-on recommendation.
   214|
   215|---
   216|
   217|## Complexity: T2
   218|
   219|**T2** — multi-file wiki/documentation promotion with bounded evidence-driven content creation, index/log updates across two wiki domains, and strict scope control against newly discovered adjacent breadth.
   220|
```
