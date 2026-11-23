# Plan for #2370: Build closed-issue promotion ledger for engineering wiki ingest

> **Status:** draft
> **PLAN DRAFT — NOT APPROVED**
> **Complexity:** T2
> **Date:** 2026-04-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2370
> **Review artifacts:** scripts/review/results/2026-04-29-plan-2370-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

<!-- RETRIEVAL CONTRACT (per #2208):
     Issue class: Data Pipeline + Knowledge/Intelligence (union).
     Required bundles: prior plans, existing code, recent related issues,
     intelligence entry points, registry.yaml, resource-intelligence-maturity.yaml,
     operating model (#2205), sibling contracts.
-->

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` — wiki lifecycle tool (init, status, lint, ingest, batch-ingest, query). **No issue-specific ingestion or promotion logic exists.** The script operates on YAML/JSONL metadata files, not GitHub issue data. The `cmd_batch_ingest` function (line 1248) handles YAML-based batch ingestion into wiki pages — this is the *downstream consumer* of any promotion ledger but does not produce one.
- Found: `scripts/knowledge/validate_inventory_readiness.py` — likely validates source inventory for readiness.
- Found: `data/document-index/promotions/2026-04-16-standards-promotion.yaml` — **precedent YAML schema** for promotion records. Contains structured records with fields: `title`, `slug`, `id`, `org`, `domain`, `tags`, `doc_key`, `doc_path`, `summary`, `issue`, `status`, `source_registry`. Closest structural analog for the ledger output format.
- Gap: No `build_closed_issue_promotion_ledger.py` or similar script exists anywhere in `scripts/knowledge/`.
- Gap: No `closed-issue-promotion-ledger.yaml` exists in `data/document-index/`.
- Gap: No scoring/ranking logic for promotion candidates exists in any script.

### Standards
- Not applicable — this is a data pipeline / knowledge management issue, not an engineering-calculation issue.

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — **82 pages** across 5 categories (34 concepts, 22 entities, 12 sources, 7 standards, 3 workflows, 4 others). Updated 2026-04-28.
- `knowledge/wikis/engineering/SOURCE_INVENTORY.md` — **Class 11** covers closed engineering issues: only 3 pages created from 5 issues (out of 20 originally scanned). "Future" section notes "15 remaining" closed engineering issues — this count is severely stale (now 106 deduped).
- Wiki concept pages inspected for overlap surface: 34 concept pages exist covering mooring, fatigue, hydrodynamics, structural analysis, VIV, seakeeping, CFD, pile capacity, pipeline integrity, cathodic protection, field economics, wave theory, standards tracking.

### Documents consulted
- Issue [#2370](https://github.com/vamseeachanta/workspace-hub/issues/2370) body — scope definition, deliverables, acceptance criteria.
- `docs/reports/engineering-wiki-skill-ingest-readiness-2039-2042.md` — quantified the backlog at time of writing: 79 closed `cat:engineering` (now 92) and 13 `cat:engineering-calculations` (now 15), with 5 issues already ingested. Recommends a "scan pass to identify the ~10 most instructive ones" as prerequisite to Slice 3 execution.
- Issue [#2039](https://github.com/vamseeachanta/workspace-hub/issues/2039) — OPEN — engineering wiki ingest umbrella (parent scope).
- Issue [#2042](https://github.com/vamseeachanta/workspace-hub/issues/2042) — OPEN — skill metadata ingest partner.
- Issue [#2236](https://github.com/vamseeachanta/workspace-hub/issues/2236) — OPEN — adds post-closure promotion step to issue-planning-mode (governs *future* closures, not the existing backlog).
- Issue [#2238](https://github.com/vamseeachanta/workspace-hub/issues/2238) — OPEN — closed-issue citation guardrail (ensures durable docs reference promoted knowledge). Guards the citation surface, not the promotion decision.
- Issue [#2366](https://github.com/vamseeachanta/workspace-hub/issues/2366) — OPEN — llm-wiki strengthening scorecard (adjacent, not overlapping — operates at wiki-page level, not issue-level).
- `data/document-index/promotions/2026-04-16-standards-promotion.yaml` — precedent for promotion YAML schema.

### Gaps identified
- No existing script fetches closed GitHub issues by label and scores them for promotion value.
- No scoring rubric or weighting for promotion dimensions (reusable methodology, decision durability, evidence richness, wiki overlap) exists as structured data.
- No extend-vs-create recommendation engine or heuristic exists.
- The 5 previously-ingested issues (Class 11) are not tracked in any ledger — only in `SOURCE_INVENTORY.md` prose. The ledger must reconcile them.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-29T04:30Z via `gh issue view`):
- `#2370` — OPEN — feat(knowledge): build closed-issue promotion ledger for engineering wiki ingest
- `#2039` — OPEN — feat: engineering wiki — ingest remaining high-value sources (skills metadata, closed issues)
- `#2042` — OPEN — feat: engineering wiki — ingest skill metadata as wiki pages
- `#2236` — OPEN — chore(workflow): add post-closure promotion step to issue-planning-mode
- `#2238` — OPEN — feat(conformance): add closed-issue citation guardrail...
- `#2366` — OPEN — feat(knowledge): add llm-wiki strengthening scorecard...

**File existence** (verified 2026-04-29T04:30Z):
- EXISTS: `knowledge/wikis/engineering/SOURCE_INVENTORY.md`
- EXISTS: `docs/reports/engineering-wiki-skill-ingest-readiness-2039-2042.md`
- EXISTS: `data/document-index/promotions/2026-04-16-standards-promotion.yaml`
- EXISTS: `scripts/knowledge/llm_wiki.py`
- MISSING (new — this plan creates): `scripts/knowledge/build_closed_issue_promotion_ledger.py`
- MISSING (new — this plan creates): `data/document-index/closed-issue-promotion-ledger.yaml`
- MISSING (new — this plan creates): `docs/reports/closed-issue-promotion-shortlist.md`
- MISSING (new — this plan creates): `scripts/knowledge/tests/test_build_closed_issue_promotion_ledger.py`

**Closed issue counts** (verified 2026-04-29T04:30Z via `gh issue list`):
- `cat:engineering` closed: **92** (issue body cited 74 — stale)
- `cat:engineering-calculations` closed: **15** (issue body cited 13 — stale)
- Dual-labeled (both labels): **1**
- Deduped unique total: **106**

**Gap proofs**:
- `grep -c 'promot\|ledger\|closed.issue' scripts/knowledge/llm_wiki.py` → 1 match (irrelevant prose comment about "Level-2 promotion" enforcement). No promotion logic.

<!-- Verification: distinct sources = issue body (1) + readiness report (2) + SOURCE_INVENTORY (3) + promotions YAML (4) + 5 related issues (5-9) + llm_wiki.py (10) + wiki index.md (11). Count: 11. Minimum 3 required. ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-29-issue-2370-closed-issue-promotion-ledger.md` |
| Tests | `scripts/knowledge/tests/test_build_closed_issue_promotion_ledger.py` |
| Implementation | `scripts/knowledge/build_closed_issue_promotion_ledger.py` |
| Primary output | `data/document-index/closed-issue-promotion-ledger.yaml` |
| Shortlist report | `docs/reports/closed-issue-promotion-shortlist.md` |
| Plan review — Claude | `scripts/review/results/2026-04-29-plan-2370-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-29-plan-2370-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-29-plan-2370-gemini.md` |

---

## Deliverable

A `build_closed_issue_promotion_ledger.py` script that fetches all closed `cat:engineering` and `cat:engineering-calculations` issues from GitHub, scores each on four promotion dimensions, and produces a durable YAML ledger plus a human-readable markdown shortlist report with target wiki domain, extend-vs-create recommendation, and overlap citations.

---

## Pseudocode

```
# build_closed_issue_promotion_ledger.py

function main():
    args = parse_args()  # --repo, --output-yaml, --output-md, --wiki-root, --already-ingested
    issues = fetch_closed_issues(repo, labels=["cat:engineering", "cat:engineering-calculations"])
    issues = deduplicate_by_number(issues)

    wiki_pages = load_wiki_index(wiki_root)  # parse index.md → list of {slug, title, category, summary}
    already_ingested = load_already_ingested(already_ingested_path)  # issue numbers already promoted

    ledger = []
    for issue in issues:
        scores = score_issue(issue, wiki_pages)
        target = recommend_target(issue, wiki_pages)  # {domain, page_slug, action: extend|create}
        overlap = find_overlap(issue, wiki_pages)  # list of existing page slugs with similarity
        ledger.append({
            number: issue.number,
            title: issue.title,
            labels: issue.labels,
            closed_at: issue.closed_at,
            scores: scores,
            composite_score: weighted_sum(scores),
            target_wiki: target,
            overlap: overlap,
            already_ingested: issue.number in already_ingested,
        })

    ledger.sort(by=composite_score, descending=True)
    write_yaml(ledger, output_yaml)
    write_shortlist_markdown(ledger, output_md, top_n=20)

function score_issue(issue, wiki_pages) -> dict:
    return {
        reusable_methodology: score_methodology(issue),   # 0-5: does body describe a reusable method?
        decision_durability: score_durability(issue),      # 0-5: is the decision still valid / timeless?
        evidence_richness: score_evidence(issue),          # 0-5: code refs, data, standards cited?
        overlap_risk: score_overlap(issue, wiki_pages),    # 0-5: 0=no overlap, 5=fully covered already
    }

function score_methodology(issue) -> int:
    body_length = len(issue.body or "")
    has_code_blocks = count("```", issue.body) > 0
    has_formulas = contains_pattern(r"[=×÷∑∫]|formula|equation|method", issue.body)
    has_references = contains_pattern(r"DNV|API|ISO|ASME|standard", issue.body)
    # Heuristic scoring: longer body + code + formulas + references = higher methodology value
    return clamp(0, 5, base_score + bonuses)

function recommend_target(issue, wiki_pages) -> dict:
    keywords = extract_keywords(issue.title + " " + issue.body)
    best_match = find_closest_wiki_page(keywords, wiki_pages)  # cosine or keyword overlap
    if best_match and similarity > EXTEND_THRESHOLD:
        return {domain: "engineering", page: best_match.slug, action: "extend"}
    else:
        suggested_slug = slugify(issue.title)
        suggested_category = classify_category(issue)  # concepts | entities | workflows | standards
        return {domain: "engineering", page: suggested_slug, action: "create", category: suggested_category}

function find_overlap(issue, wiki_pages) -> list:
    keywords = extract_keywords(issue.title + " " + issue.body)
    overlapping = []
    for page in wiki_pages:
        overlap_score = keyword_overlap(keywords, page.title + " " + page.summary)
        if overlap_score > OVERLAP_THRESHOLD:
            overlapping.append({page: page.slug, score: overlap_score})
    return overlapping
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/build_closed_issue_promotion_ledger.py` | Main implementation — issue fetcher, scorer, ledger writer |
| Create | `scripts/knowledge/tests/test_build_closed_issue_promotion_ledger.py` | TDD test suite |
| Create (generated) | `data/document-index/closed-issue-promotion-ledger.yaml` | Primary durable output — all 106 issues scored |
| Create (generated) | `docs/reports/closed-issue-promotion-shortlist.md` | Human-readable top-20 shortlist report |
| Update | `knowledge/wikis/engineering/SOURCE_INVENTORY.md` | Update Class 11 counts and add reference to ledger |
| Update | `docs/plans/README.md` | Add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_deduplicate_issues` | Dual-labeled issues are not double-counted | 2 issue dicts with same number | 1 unique issue |
| `test_score_methodology_rich_body` | Issue with code blocks + formulas scores 4-5 | Issue body with ```` ``` ````, equations, DNV ref | score ≥ 4 |
| `test_score_methodology_empty_body` | Issue with no body scores 0 | Issue with body=None | score == 0 |
| `test_score_durability_recent_closed` | Recently closed issue gets higher durability | Issue closed 2026-03-01 | score ≥ 3 |
| `test_score_evidence_with_standards` | Issue referencing standards gets high evidence score | Body with "DNV-RP-C203" | score ≥ 4 |
| `test_score_overlap_exact_match` | Issue title matching wiki page title gets high overlap | Title "Fatigue Analysis..." vs wiki page "Fatigue Analysis for Offshore..." | overlap_risk ≥ 4 |
| `test_score_overlap_no_match` | Issue on novel topic gets 0 overlap | Title "Drillbotics Sensor Calibration" vs engineering wiki | overlap_risk == 0 |
| `test_recommend_target_extend` | High-similarity issue recommends extend | Issue matching existing page | action == "extend", page slug set |
| `test_recommend_target_create` | Low-similarity issue recommends create | Issue on novel topic | action == "create", category set |
| `test_composite_score_ordering` | Ledger sorted by composite score descending | 3 issues with different scores | sorted correctly |
| `test_yaml_output_schema` | Written YAML has required fields per record | Ledger with 3 entries | All fields present per schema |
| `test_yaml_idempotent` | Running twice produces identical YAML | Same issue set | byte-identical output |
| `test_shortlist_markdown_top_n` | Shortlist contains only top N entries | Ledger with 30 entries, top_n=20 | Markdown has 20 rows |
| `test_already_ingested_flagged` | Previously ingested issues are marked | Issue #1234 in already-ingested list | `already_ingested: true` |
| `test_handles_gh_api_errors` | Graceful handling of rate limit / network error | Mocked 403 response | Raises clear error with retry guidance |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest scripts/knowledge/tests/test_build_closed_issue_promotion_ledger.py -v`
- [ ] No regression: `uv run pytest scripts/knowledge/tests/ -v` passes
- [ ] Ledger YAML covers all 106 deduped closed issues (verified count at execution time)
- [ ] Each ledger entry has: `number`, `title`, `labels`, `closed_at`, `scores` (4 dimensions), `composite_score`, `target_wiki`, `overlap`, `already_ingested`
- [ ] Shortlist report shows top-20 candidates ranked by composite score
- [ ] Each shortlisted issue has target wiki domain + extend/create recommendation
- [ ] Overlap analysis cites specific existing wiki page slugs (not generic claims)
- [ ] Output is durable YAML, not markdown-only
- [ ] Script is idempotent — running twice with same input produces identical YAML
- [ ] Manually-reviewable diff: changes to ledger between runs are visible via `diff` or `git diff`
- [ ] 5 previously-ingested issues (Class 11 in SOURCE_INVENTORY) are marked `already_ingested: true`
- [ ] SOURCE_INVENTORY.md Class 11 section updated with accurate counts
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING

Revisions made based on review:
- (none yet — draft)

---

## Risks and Open Questions

- **Risk: Stale issue counts** — The issue body cites 74+13; actual counts are now 92+15 (106 deduped). The script must query GitHub live, not rely on hardcoded counts. The ledger should record the query timestamp.
- **Risk: Scoring heuristics are subjective** — The 0-5 scoring dimensions (methodology, durability, evidence, overlap) are text-heuristic based. Without embeddings or LLM scoring, keyword matching may produce false positives/negatives. **Mitigation:** The shortlist is human-reviewed before any promotion action; scoring is a triage aid, not an oracle.
- **Risk: GH API rate limits** — Fetching 106 issues' full bodies may hit unauthenticated rate limits. **Mitigation:** Script uses `gh` CLI which inherits authenticated token; 106 requests is well within 5000/hr limit.
- **Risk: Overlap detection quality** — Keyword-based overlap between issue titles/bodies and wiki page titles/summaries may miss semantic overlap or produce false matches. **Mitigation:** Overlap citations are manually verifiable in the shortlist report; false matches are cheap to dismiss during human review.
- **Risk: Dependency on #2236/#2238** — This ledger is *complementary to* but not *dependent on* #2236 (future promotion workflow) and #2238 (citation guardrail). Those issues govern what happens *after* a promotion decision; this ledger governs what *enters* promotion consideration. No blocking dependency.
- **Open: Composite score weights** — Should the four dimensions be equally weighted? `overlap_risk` is inverse (high overlap = lower promotion value). Default: methodology=0.30, durability=0.25, evidence=0.25, overlap_risk_penalty=0.20. Confirm during approval.
- **Open: Already-ingested source of truth** — The 5 previously-ingested issues from Class 11 are mentioned in prose in SOURCE_INVENTORY.md but their exact issue numbers are not listed. Implementation will need to cross-reference wiki page provenance (log.md or page frontmatter) to identify them. If not findable, flag as "possibly ingested — verify manually."
- **Open: Engineering-calculations-only scope** — Issue body says "first pass bounded to engineering-related issues only." Should `cat:engineering-calculations` issues be included in the same ledger (as implied by the issue body enumerating both labels) or split into a separate domain? Recommend: single ledger, tag-filtered views in the shortlist.

---

## Out of Scope

- **Actual wiki page creation or modification** — The ledger recommends; it does not execute promotion.
- **LLM-based semantic scoring** — V1 uses keyword heuristics only. LLM scoring can be a follow-up if heuristic quality is insufficient.
- **Skill-metadata promotion** — Covered by [#2042](https://github.com/vamseeachanta/workspace-hub/issues/2042), not this issue.
- **Post-closure workflow changes** — Covered by [#2236](https://github.com/vamseeachanta/workspace-hub/issues/2236).
- **Citation guardrail enforcement** — Covered by [#2238](https://github.com/vamseeachanta/workspace-hub/issues/2238).
- **Wiki strengthening scorecard** — Covered by [#2366](https://github.com/vamseeachanta/workspace-hub/issues/2366). Operates at wiki-page level, not issue-candidate level.
- **Non-engineering label scopes** — Only `cat:engineering` and `cat:engineering-calculations` are in scope per issue body.

---

## Dependencies

| Dependency | Type | Status | Impact if unmet |
|---|---|---|---|
| `gh` CLI authenticated | Runtime | Available (ace-linux-1) | Script cannot fetch issues |
| `knowledge/wikis/engineering/wiki/index.md` | Data | EXISTS (82 pages) | Overlap analysis has no target surface |
| `knowledge/wikis/engineering/wiki/log.md` | Data | EXISTS | Needed to identify already-ingested issues |
| `data/document-index/promotions/` dir | Convention | EXISTS | Precedent for promotion YAML schema |
| PyYAML | Library | Available via `uv` | YAML output |
| No blocking issues | — | — | #2236, #2238 are complementary, not blocking |

---

## Rollback

If the implementation proves problematic:
1. Delete `scripts/knowledge/build_closed_issue_promotion_ledger.py`
2. Delete `data/document-index/closed-issue-promotion-ledger.yaml`
3. Delete `docs/reports/closed-issue-promotion-shortlist.md`
4. Revert SOURCE_INVENTORY.md Class 11 count update
5. No other repo state is affected — the ledger is pure output, not wired into any pipeline or hook.

---

## Complexity: T2

**T2** — new standalone script with multiple files (script + tests + 2 generated outputs), keyword-based scoring logic, GitHub API integration, and YAML schema design. No multi-module architecture or standards-derivation complexity. Human-reviewable output keeps risk bounded.
