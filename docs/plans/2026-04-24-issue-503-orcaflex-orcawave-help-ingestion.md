# Plan for #503: Ingest OrcaFlex/OrcaWave online help into LLM-accessible format

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-24
> **Issue:** https://github.com/vamseeachanta/digitalmodel/issues/503
> **Review artifacts:** scripts/review/results/2026-04-24-plan-503-claude.md | ...-codex.md | ...-gemini.md

> **Scope boundary (from Explorer intel):** Parent ingestion pipeline ONLY. Specific page selection (Environment/Waves/Current, etc.) is out of scope and will be driven by sibling issue #507 once this pipeline lands. Papers/PDF ingestion already handled by the existing `ingest-orcina.py` is flagged as a `[TRADEOFF FOR USER]` below, not assumed in-scope.

> **GATE — READ FIRST:** This plan is PAUSED at section "Risks and Open Questions" pending USER resolution of the Licensing/ToS tradeoff. No implementation commitment below that point can be locked in until the gate clears — the storage-surface choice (which rewrites most of the "Files to Change" table) flows from the licensing decision.

---

## Resource Intelligence Summary

### Existing repo code

- **Found (primary competitor A):** `scripts/data/llm-wiki/ingest-orcina.py:1-636` — full live-crawl implementation. Parses MadCap Flare `Toc.xml`, iterates topic pages with `User-Agent: workspace-hub-llm-wiki/1.0` + 0.3s polite delay, BeautifulSoup HTML→markdown, writes `index.json` + per-product dirs. Also ingests supplementary Orcina resource pages and PDFs via `pdftotext`. References issue #2088. Untested.
- **Found (primary competitor B):** `digitalmodel/scripts/ingest_orcina_help.py:1-349` — second live-crawl implementation in the digitalmodel subrepo. Uses `markdownify` + `requests`, hardcoded `PRIORITY_PAGES` per product, local-html cache fallback at `/tmp/orcina_html`, writes `docs/domains/{orcaflex,orcawave,orcfxapi}/reference/<slug>.md` + `INDEX.md`. Untested. DIFFERENT OUTPUT PATH, DIFFERENT DEP SET from competitor A.
- **Found (consumer contract):** `scripts/data/llm-wiki/search-wiki.py:1-183` — retrieval surface that reads whatever schema competitor A emits. Any consolidation must preserve or explicitly migrate this consumer.
- **Found (path resolver):** `scripts/data/llm-wiki/resolve_wiki_path.py:1-67` — canonical output-root resolver (env → config → `data/llm-wiki` → `knowledge/wikis`). Competitor A uses this; competitor B does not. Parent pipeline MUST adopt the resolver.
- **Found (canonical wiki CLI):** `scripts/knowledge/llm_wiki.py:1-60` — `init/ingest/query/lint/status/batch-ingest` over `knowledge/wikis/<domain>/`. Defines L3 frontmatter schema (`title, tags, added, last_updated` required; `sources` recommended).
- **Found (nightly cadence pattern):** `scripts/knowledge/wiki-ingest-cron.sh:1-367` — marker-file + git-safe-commit + alert-issue pattern this pipeline should mirror for idempotent re-ingest.
- **Found (quarterly cadence dependent):** `scripts/cron/external-doc-reingest.sh` + `tests/cron/test_external_doc_reingest.py` — #2318 declares dm#503 as its upstream; current cadence reports "index not yet initialized" until this plan lands.
- **Gap:** No ZIP-based fetch path anywhere in repo; issue body specifies ZIP-based pipeline but neither existing script implements it.
- **Gap:** No chunking stage in either competitor — both emit one markdown file per topic.
- **Gap:** No frontmatter emission — both competitors write raw markdown with HTML-comment source URL only.
- **Gap:** No tests for either competitor.
- **Gap:** No WebHelp root entries (`/webhelp/OrcaFlex/Default.htm`, `/webhelp/OrcaWave/Default.htm`, `/webhelp/OrcFxAPI/Default.htm`) in `online-resource-registry.yaml` — only the landing `/resources/documentation/` page is registered. #2318 cadence cannot diff WebHelp changes until the WebHelp roots are registered as L2 provenance.

### Standards

Not applicable — doc-ingestion pipeline is not engineering-class. No API/DNV/ASME/ISO standards apply.

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/SCHEMA.md:1-80` — defines `raw/` (immutable) vs. `wiki/{entities,concepts,sources,standards,workflows,index.md,log.md}` layout and frontmatter conventions. Target surface if Orcina output is promoted to L3.
- `knowledge/wikis/engineering/raw/` — only `papers/` subdir today; no vendor-docs raw storage exists yet. Creating `raw/orcina-webhelp/` (or equivalent) is a gap this plan must either fill or explicitly route elsewhere (e.g., `/mnt/ace/` per issue body).

### Documents consulted

- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md:1-80` (#2205, amended 2026-04-19) — authoritative 6-layer architecture. Orcina spans L1 (raw HTML/ZIP) → L2 (registry + content hash) → L3 (wiki pages). Explicitly delegates llm-wiki ingestion implementation to #2034; #503 is the digitalmodel-side driver that must CONFORM, not invent.
- `docs/plans/2026-04-11-issue-2205-multi-machine-llm-wiki-resource-doc-intelligence-operating-model.md` — parent operating-model plan. Orcina pages MUST pass GUARD-1 (no "between-layer" classifications).
- `docs/plans/2026-04-16-issue-2206-pyramid-conformance-checks.md` — conformance lint set that will check Orcina output.
- `docs/plans/2026-04-16-issue-2207-standards-codes-provenance-reuse-contract.md` — provenance contract: L3 pages need `sources:` list with vendor URL + fetch timestamp + content hash.
- `docs/plans/2026-04-16-issue-2209-durable-vs-transient-knowledge-boundary.md` — Orcina WebHelp is durable reference material → L3 placement is correct per this boundary rule.
- `docs/plans/2026-04-17-issue-2318-external-doc-reingest.md` — explicitly names dm#503 as the manifest source this cadence diffs against.
- `docs/plans/2026-04-15-issue-2293-wiki-ingest-idempotent-and-push-status-truthful.md` — incremental-ingest idempotency contract this pipeline must honor (re-runnable without page-count drift or spurious commits).
- `docs/plans/2026-04-20-issue-2398-llm-wiki-spinout-vs-embedded-architecture.md` — OPEN architectural question whether llm-wiki lives embedded or as separate repo. Affects long-term home of this pipeline's code and output.
- `docs/reports/external-doc-reingest-2026-Q2.md` — first sample cadence report; Orcina row empty pending dm#503.
- Issue body for #503 (see `/tmp/orca-batch-2026-04-24/issue-503.json`) — specifies ZIP-based fetch, `markitdown` converter, `/mnt/ace/digitalmodel/docs/orcaflex-help/` storage, llm-wiki retrieval skill, and agent-skill updates.
- Sibling issue #507 — concrete driver for Environment/Waves/Current pages; explicitly OUT OF SCOPE for this parent plan.

### Gaps identified

1. **Fetch strategy unresolved** — issue says "download ZIPs"; both competitors live-crawl. No ZIP-fetch code exists.
2. **Converter tool drift** — issue says `markitdown`; competitor A uses BeautifulSoup; competitor B uses `markdownify`. Three candidates, no cross-validation.
3. **No chunking** — neither competitor chunks; issue names chunking as a pipeline step. No chunk-size target, boundary rule, or manifest schema defined.
4. **No frontmatter emission** — neither competitor writes the `title/tags/added/last_updated/sources` frontmatter that `scripts/knowledge/llm_wiki.py` requires for L3 promotion.
5. **Storage-surface decision is open and load-bearing** — four candidate locations (`docs/domains/...`, `data/llm-wiki/`, `knowledge/wikis/engineering/`, `/mnt/ace/...`). Pick ONE; reconcile with #2205 + #2398.
6. **L2 registry gap** — WebHelp roots not registered in `online-resource-registry.yaml`.
7. **No idempotency marker / re-ingest policy** — mirror `wiki-ingest-cron.sh`'s `.last-ingest-timestamp` pattern.
8. **Duplicate-pipeline consolidation** — competitor A and competitor B both in-repo, different schemas.
9. **Papers/PDF scope** — competitor A also ingests papers; #503 titles WebHelp only. Decide.
10. **Skill surface** — llm-wiki retrieval skill + orcaflex/orcawave agent-skill updates are deliverables in the issue body but neither exists. Scope in or defer to a child.
11. **Tests** — both competitors untested.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-24 via issue JSON at `/tmp/orca-batch-2026-04-24/issue-503.json` — this Planner pod is network-off; gh-based re-verification required at adversarial review):

- `#503` — OPEN — "Ingest OrcaFlex/OrcaWave online help into LLM-accessible format" (confirmed via issue JSON)
- `#507` — referenced in intel as first concrete driver (Environment/Waves/Current pages); status to be confirmed at review
- `#2088` — referenced from `ingest-orcina.py` header comment; status to be confirmed
- `#2205` — operating model parent (amended 2026-04-19 per intel)
- `#2318` — external-doc-reingest cadence; explicitly depends on dm#503
- `#2034` — delegated llm-wiki-ingestion implementation per #2205
- `#2398` — open spinout-vs-embedded architecture question
- `#2293` — idempotent wiki-ingest contract

**File existence** (verified 2026-04-24 via `ls -la`):

- EXISTS: `scripts/data/llm-wiki/ingest-orcina.py` (21,770 bytes, mtime 2026-04-16)
- EXISTS: `digitalmodel/scripts/ingest_orcina_help.py` (16,984 bytes, mtime 2026-04-10)
- EXISTS: `data/document-index/online-resource-registry.yaml` (152,258 bytes, mtime 2026-04-16)
- EXISTS: `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` (27,099 bytes, mtime 2026-04-19)
- EXISTS: `scripts/knowledge/llm_wiki.py`, `scripts/knowledge/wiki-ingest-cron.sh`, `scripts/data/llm-wiki/resolve_wiki_path.py`, `scripts/data/llm-wiki/search-wiki.py` (per intel)
- MISSING (this plan will create or modify, pending gate resolution): the single canonical pipeline entry point + chunk manifest schema + frontmatter emitter + idempotency marker + registry rows + tests.

**Line excerpts** (from `/mnt/local-analysis/workspace-hub/scripts/data/llm-wiki/ingest-orcina.py` header):

```
#!/usr/bin/env python3
"""
Ingest Orcina product documentation (OrcaFlex, OrcaWave, OrcFxAPI) into llm-wiki.

Crawls the MadCap Flare online help via TOC XML, fetches each topic page,
```

**Gap proofs**:

- `grep -c orcina data/document-index/online-resource-registry.yaml` → 29 matches, but manual inspection confirms NO rows for `/webhelp/OrcaFlex/Default.htm`, `/webhelp/OrcaWave/Default.htm`, `/webhelp/OrcFxAPI/Default.htm`. Registered rows cover `/resources/documentation/`, `/resources/examples/`, `/resources/papers/` — not the WebHelp roots this plan ingests. Gap: 3 registry rows must be added.
- `ls scripts/data/llm-wiki/tests/` → only `test_resolve_wiki_path.py`; no `test_ingest_orcina.py` → confirms competitor A is untested.
- `ls digitalmodel/scripts/tests/` (per intel) → no ingester tests → confirms competitor B is untested.

<!-- Verification: distinct sources consulted: issue body (1), competitor A code (2), competitor B code (3), #2205 operating model (4), #2318 cadence plan (5), #2293 idempotency plan (6), #2398 spinout plan (7), online-resource-registry.yaml (8), engineering/SCHEMA.md (9), scripts/knowledge/llm_wiki.py (10). Count: 10. Minimum 3 satisfied. -->

---

## Artifact Map

<!-- Entries marked (gated) are conditional on the Licensing/ToS and Storage-surface tradeoffs being resolved. -->

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-24-issue-503-orcaflex-orcawave-help-ingestion.md |
| Canonical ingestion entry point (gated) | `scripts/data/llm-wiki/orcina/ingest.py` (consolidation target — see Files to Change) |
| Chunk + manifest schema (gated) | `scripts/data/llm-wiki/orcina/manifest.py` + `manifest.schema.json` |
| Tests — TOC parse, HTML→md golden, idempotency, manifest, frontmatter | `scripts/data/llm-wiki/tests/orcina/` (new package) |
| L2 registry rows | `data/document-index/online-resource-registry.yaml` (3 new entries: OrcaFlex/OrcaWave/OrcFxAPI WebHelp roots) |
| Cadence integration | `scripts/cron/external-doc-reingest.sh` (reads new registry rows — no code change unless output schema changes) |
| llm-wiki retrieval skill (gated — may defer) | `.claude/skills/workspace-hub/llm-wiki/orcina-help/SKILL.md` |
| Agent-skill cross-references (gated — may defer) | `digitalmodel/.claude/agents/orcaflex/...`, `digitalmodel/.claude/agents/orcawave/...` |
| Competitor A retire/merge | `scripts/data/llm-wiki/ingest-orcina.py` (action TBD by consolidation tradeoff) |
| Competitor B retire/merge | `digitalmodel/scripts/ingest_orcina_help.py` (action TBD by consolidation tradeoff — cross-repo commit) |
| Plans index update | `docs/plans/README.md` |
| Plan review — Claude | scripts/review/results/2026-04-24-plan-503-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-24-plan-503-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-24-plan-503-gemini.md |

---

## Deliverable

A single canonical Orcina WebHelp ingestion pipeline (fetch → extract → convert → chunk → frontmatter-wrap → manifest → store) that (a) replaces the two existing competing scripts per the consolidation tradeoff, (b) conforms to the #2205 L1→L2→L3 layer model with registry rows and content-hash provenance, (c) is idempotent per the #2293 contract, (d) emits a manifest the #2318 cadence can diff, and (e) is covered by TDD tests. Storage surface and ingestion method are locked by the licensing and consolidation gates before any code is written.

---

## Pseudocode

```
# Stage 1 — Fetch (method chosen by Ingestion-Method tradeoff)
function fetch_orcina_source(product):
    if method == "ZIP":
        download https://www.orcina.com/webhelp/{product}/{product}Help.zip with ETag + robots.txt check
        verify content-hash against registry baseline (if any)
        extract into staging dir
        return staging dir + new content-hash
    elif method == "LIVE-CRAWL":
        reuse competitor-A TOC-driven crawler with polite delay + User-Agent + robots.txt check
        write each topic to staging dir
        return staging dir + per-topic content-hashes

# Stage 2 — Convert (converter chosen by Converter tradeoff; default markitdown per issue body)
function html_to_markdown(html_path):
    strip MadCap chrome (nav, breadcrumb, footer)
    apply converter (markitdown | markdownify | BeautifulSoup-custom)
    normalize links: vendor-URL-absolute (never repo-relative)
    return markdown_text, extracted_title

# Stage 3 — Chunk
function chunk_page(markdown_text, title):
    split on H2/H3 section boundaries
    cap each chunk at ~1500 tokens (target LLM context efficiency)
    if chunk > cap: sub-split on H4 or paragraph boundary
    return [{chunk_id, heading_path, text, token_count}, ...]

# Stage 4 — Frontmatter + write (schema from scripts/knowledge/llm_wiki.py)
function emit_wiki_page(product, topic_slug, chunks, source_url, fetch_ts, content_hash):
    frontmatter = {
        title: extracted_title,
        tags: [product, "vendor-doc", "orcina"],
        added: fetch_ts (first-seen),
        last_updated: fetch_ts (current),
        sources: [{url: source_url, fetched_at: fetch_ts, content_hash: content_hash, license: "orcina-vendor-copyright"}],
    }
    write to <storage-surface>/<product>/<topic_slug>.md (path from Storage-surface tradeoff)
    append row to manifest.json

# Stage 5 — Manifest + idempotency
function update_manifest(rows):
    load existing manifest.json
    for row in rows:
        if row.content_hash == existing.content_hash: skip (idempotent no-op per #2293)
        else: update last_updated, bump revision
    write manifest.json
    touch .last-ingest-timestamp

# Stage 6 — Registry sync (L2)
function sync_registry():
    ensure online-resource-registry.yaml has rows for OrcaFlex/OrcaWave/OrcFxAPI WebHelp roots
    update each row's last_checked + content_hash
```

---

## Files to Change

> **All "Create" and "Modify" rows are gated.** Final paths depend on the Storage-surface tradeoff; consolidation strategy determines which competitor rows become Delete vs. Merge. This table encodes option (A) "merge into canonical pipeline under `scripts/data/llm-wiki/orcina/`" as the planner's recommended default; swap in option (B) or (C) after the user picks.

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/llm-wiki/orcina/__init__.py` | Package init for consolidated pipeline |
| Create | `scripts/data/llm-wiki/orcina/ingest.py` | Canonical entry point (orchestrates fetch→convert→chunk→write) |
| Create | `scripts/data/llm-wiki/orcina/fetch.py` | Fetch stage (ZIP or live-crawl per tradeoff) + robots.txt + ETag |
| Create | `scripts/data/llm-wiki/orcina/convert.py` | HTML→markdown (tool per tradeoff) |
| Create | `scripts/data/llm-wiki/orcina/chunk.py` | Section-boundary chunker |
| Create | `scripts/data/llm-wiki/orcina/manifest.py` + `manifest.schema.json` | Idempotency + diff surface for #2318 cadence |
| Create | `scripts/data/llm-wiki/tests/orcina/test_toc_parse.py` | Fixture-based TOC.xml parser test |
| Create | `scripts/data/llm-wiki/tests/orcina/test_html_to_markdown.py` | Golden-file HTML→md regression test |
| Create | `scripts/data/llm-wiki/tests/orcina/test_chunker.py` | Chunk-boundary + size-cap test |
| Create | `scripts/data/llm-wiki/tests/orcina/test_idempotency.py` | Re-ingest without drift (#2293 contract) |
| Create | `scripts/data/llm-wiki/tests/orcina/test_manifest_schema.py` | Manifest conforms to schema |
| Create | `scripts/data/llm-wiki/tests/orcina/test_frontmatter_emission.py` | Emitted frontmatter validates against `llm_wiki.py` schema |
| Modify | `data/document-index/online-resource-registry.yaml` | Add 3 WebHelp-root rows (OrcaFlex, OrcaWave, OrcFxAPI) with ETag + content-hash baseline |
| Delete OR Merge | `scripts/data/llm-wiki/ingest-orcina.py` | Consolidation action (tradeoff-dependent) |
| Delete OR Merge | `digitalmodel/scripts/ingest_orcina_help.py` | Consolidation action (tradeoff-dependent); CROSS-REPO — separate commit on `digitalmodel/` |
| Modify (optional) | `scripts/data/llm-wiki/search-wiki.py` | Only if output schema migration is needed; otherwise unchanged |
| Create (gated) | `.claude/skills/workspace-hub/llm-wiki/orcina-help/SKILL.md` | Retrieval skill (deliverable in issue body — scope-in or child issue per tradeoff) |
| Modify (gated, cross-repo) | `digitalmodel/.claude/agents/orcaflex/...`, `...orcawave/...` | Agent-skill cross-references (deliverable in issue body — scope-in or child) |
| Update | `docs/plans/README.md` | Index this plan |
| Update (post-land) | `docs/reports/external-doc-reingest-2026-Q2.md` | Populate Orcina row once first ingest succeeds |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_toc_parse_nominal | Parses MadCap `Toc.xml` into ordered topic list | fixture `tests/fixtures/orcina/OrcaFlex-Toc.xml` | Topic list with N entries, hierarchy preserved |
| test_toc_parse_empty | Handles empty/malformed TOC safely | empty `<CatapultToc/>` | Empty list, no crash |
| test_fetch_zip_extract | ZIP fetch path extracts expected HTML files | local fixture `OrcaFlexHelp.zip` | Expected file tree in staging |
| test_fetch_robots_respected | Live-crawl path honors robots.txt | mock robots.txt disallowing `/webhelp/` | RuntimeError or skip, no GET |
| test_fetch_etag_304 | Re-fetch with unchanged ETag returns cached | mock server returns 304 | Uses cached copy, no re-convert |
| test_html_to_markdown_golden | Conversion matches golden reference for representative page | fixture `tests/fixtures/orcina/General.html` | Matches `tests/fixtures/orcina/General.md` |
| test_html_to_markdown_madcap_chrome_stripped | MadCap nav/breadcrumb/footer removed | HTML with `<nav class="mc-breadcrumbs">...` | Output contains no MadCap chrome |
| test_chunker_section_boundaries | Splits on H2/H3 | markdown with 3 H2 + 5 H3 | 3 top-level chunks, nested sub-chunks |
| test_chunker_size_cap | Large section sub-splits | 5000-token H2 section | Multiple chunks each ≤1500 tokens |
| test_frontmatter_emission_schema | Emitted frontmatter validates against `llm_wiki.py` required keys | ingested page | Has `title, tags, added, last_updated, sources[].url, sources[].content_hash` |
| test_frontmatter_tags_include_product | Tags include product + `vendor-doc` + `orcina` | OrcaFlex page | `tags == ["orcaflex", "vendor-doc", "orcina"]` |
| test_manifest_schema_valid | Manifest conforms to `manifest.schema.json` | ingested manifest | jsonschema validation passes |
| test_idempotency_no_drift | Re-running pipeline on unchanged source emits no new rows | same source ingested twice | Second run: 0 new pages, 0 updates, same page count (#2293 contract) |
| test_idempotency_hash_driven_update | Changed content triggers `last_updated` bump only | change 1 page, re-ingest | 1 updated row, 0 new rows, `added` unchanged |
| test_registry_entry_present | 3 WebHelp-root entries exist in registry post-ingest | registry.yaml | Rows for `/webhelp/OrcaFlex/Default.htm`, `/webhelp/OrcaWave/Default.htm`, `/webhelp/OrcFxAPI/Default.htm` |
| test_consumer_search_wiki_compat | `search-wiki.py` continues to resolve pages post-consolidation | ingested output | Query returns matches; no schema regression |

---

## Acceptance Criteria

- [ ] Licensing/ToS gate cleared by user with recorded decision (see Risks).
- [ ] Consolidation tradeoff chosen by user; losing script(s) deleted (cross-repo commit if digitalmodel/ competitor retired).
- [ ] Ingestion-method tradeoff chosen; fetch stage implemented for chosen method only.
- [ ] Converter tradeoff chosen; single converter adopted repo-wide.
- [ ] Storage-surface tradeoff chosen; output under that surface only.
- [ ] All new tests pass: `uv run pytest scripts/data/llm-wiki/tests/orcina/ -v`.
- [ ] No regression: `uv run pytest scripts/` passes; `scripts/data/llm-wiki/tests/test_resolve_wiki_path.py` + `scripts/knowledge/tests/test_llm_wiki.py` + `tests/cron/test_external_doc_reingest.py` all green.
- [ ] Registry has 3 WebHelp-root rows with initial content-hash baseline.
- [ ] First successful ingest emits a manifest the #2318 cadence reads without error.
- [ ] Emitted pages pass #2206 GUARD-1 (no "between-layer" classifications) and the #2207 provenance contract (sources[] with URL + fetch timestamp + content hash).
- [ ] Idempotency verified: re-run of pipeline on unchanged source produces 0 commits (per #2293).
- [ ] Plan review artifacts posted (3 providers, scripts/review/results/2026-04-24-plan-503-{claude,codex,gemini}.md).
- [ ] `docs/plans/README.md` updated.
- [ ] `docs/reports/external-doc-reingest-2026-Q2.md` Orcina row populated post-first-ingest.

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE / MINOR / MAJOR | _placeholder — pending adversarial review_ |
| Codex | APPROVE / MINOR / MAJOR | _placeholder — pending adversarial review_ |
| Gemini | APPROVE / MINOR / MAJOR | _placeholder — pending adversarial review_ |

**Overall result:** _placeholder — PASS / FAIL (re-draft required)_

Revisions made based on review:

- _placeholder — list any changes made to the plan after adversarial review_

---

## Risks and Open Questions

### [TRADEOFF FOR USER — GATING] Licensing / Terms of Service (blocks all else)

Orcina's WebHelp content and downloadable ZIPs are vendor-copyrighted. Re-hosting converted markdown outside a licensee-controlled surface may violate Orcina's ToS and the digitalmodel team's license agreement. The issue body's `/mnt/ace/digitalmodel/docs/orcaflex-help/` destination (non-git-tracked) is already an implicit signal that raw reproduction belongs off-repo.

**Decision options:**

- **(L-1) Authorize non-git-tracked storage on ace drive.** Ingest full content to `/mnt/ace/...`; keep only manifest + metadata in repo. Full pipeline proceeds; L3 wiki pages emit as excerpts or stubs with links to the ace-drive copies.
- **(L-2) Pivot to reference-only (no copy).** Ingest TOC + titles + URLs + section anchors only. No full-text re-host. Storage can be git-tracked. Significantly narrower deliverable; the LLM retrieval surface links out rather than grounds on local text. Likely undercuts the issue's stated "spec generation accuracy" goal.
- **(L-3) Excerpt-for-interoperability.** Ingest only derived artifacts (YAML examples, property lists, numeric constants) plus short normative excerpts. Middle path — stays inside typical fair-use/interop clauses but requires per-topic judgment.
- **(L-4) Review Orcina's footer + `terms.htm` first.** User defers choice until someone confirms the redistribution clause. Planner recommends this as the FIRST action — but cannot perform the web fetch from inside this pod (`DO NOT fetch anything from Orcina's site` is a hard forbid).

**GATE:** Until the user picks one, the storage-surface tradeoff below is undecidable and most of "Files to Change" cannot be finalized. The two existing competitors may ALREADY have created ToS exposure — the plan recommends the user decide whether to also retire/rewrite them as part of the gate response.

### [TRADEOFF FOR USER] Consolidation approach for two competing scripts

Two ingesters already live in-repo. A third parallel implementation is explicitly forbidden by the Explorer pod.

- **(C-A) Merge competitor A + competitor B into a single canonical pipeline under `scripts/data/llm-wiki/orcina/`**; deprecate both legacy files. Planner default — preserves the TOC-driven approach from A and the hardcoded-priority fallback from B as a CLI flag. Crosses a repo boundary (digitalmodel/).
- **(C-B) Retire both; write fresh per the issue body's ZIP/markitdown pipeline.** Cleanest architecture; most code written from scratch; loses A's supplementary-papers + PDF handling and B's local-cache fallback unless re-implemented.
- **(C-C) Adopt one, absorb the other's features, retire the other.** E.g., adopt competitor A as the base (it already uses `resolve_wiki_path` + references #2088); absorb B's `markdownify` conversion + priority-page config; delete B. Minimum diff, minimum risk; still requires cross-repo commit.

Recommended: **C-C with A as base** if licensing gate resolves to L-1 or L-3 (reuses the live-crawl infrastructure); **C-B fresh** if gate resolves to L-2 (narrow scope makes rewrite cheap).

### [TRADEOFF FOR USER] Ingestion method — ZIP vs. live-crawl

- **(M-1) ZIP-based (issue body preference).** Reproducible snapshots, version-pinnable, offline re-ingest, polite by construction. New code path — neither competitor implements this. Stale between ZIP drops.
- **(M-2) Live-crawl (both competitors' approach).** Auto-follows Orcina updates; brittler; requires robots.txt + polite-delay + ETag discipline. Existing code.
- **(M-3) Hybrid.** ZIP as primary seed; live-crawl diff for incremental updates. Most complex; highest upkeep cost.

Recommended: **M-1 ZIP** if the issue body's "reproducibility" stance is load-bearing; **M-2 live-crawl** if #2318 quarterly cadence wants fresh data every quarter; **M-3** only if both matter and we budget the complexity.

### [TRADEOFF FOR USER] Converter — `markitdown` vs. `markdownify` vs. BeautifulSoup-custom

- **(K-1) `markitdown`.** Issue body preference; already in repo venv. Not yet benchmarked on MadCap Flare markup.
- **(K-2) `markdownify`.** Competitor B's choice. Known-to-work on Orcina HTML.
- **(K-3) BeautifulSoup-custom (competitor A).** Most control; most code to maintain.

Recommended: run a one-day benchmark against 20 representative MadCap pages (fixture set), pick the converter with the best fidelity + lowest chrome-leakage before writing production code. This benchmark is a sub-deliverable inside Stage 2.

### [TRADEOFF FOR USER] Storage surface (flows from Licensing gate)

- **(S-1) `/mnt/ace/digitalmodel/docs/orcaflex-help/`** (issue body preference; non-git-tracked) — default if L-1 is chosen. Raw HTML + converted markdown live off-repo; repo carries only manifest + registry rows + pointers. Honors the "no re-host in git" reading of ToS.
- **(S-2) `knowledge/wikis/engineering/` or new `knowledge/wikis/orcaflex-help/` domain** (git-tracked) — #2205 L3 canonical surface. Requires licensing authorization to re-host.
- **(S-3) `data/llm-wiki/` (env-var-resolved via `resolve_wiki_path.py`)** — competitor A's default. Config-swappable between git-tracked and non-git-tracked per machine.
- **(S-4) `docs/domains/{orcaflex,orcawave,orcfxapi}/reference/`** (competitor B's default) — NOT recommended; bypasses #2205 layer model and puts vendor reference prose inside engineering-doc surface where #2206 conformance linter will flag it.

Recommended: S-1 if L-1 wins; S-2 if L-3 wins (excerpts are defensible as fair use); S-1 also the safe default if L-2 wins (manifest-only storage still benefits from ace-drive colocation with the raw copies team already has).

### [TRADEOFF FOR USER] Papers/PDF scope

Competitor A also ingests Orcina's published papers via `pdftotext`. Issue #503's title is "online help" only.

- **(P-1) In-scope.** Preserve papers ingestion in the consolidated pipeline; register papers URLs in registry.
- **(P-2) Out-of-scope; spin to child issue.** Keep #503 WebHelp-only; open a follow-up for papers.
- **(P-3) Delete papers ingestion entirely.** Only if a user decision confirms papers were never in-scope.

Recommended: **P-2** (spin to child issue) to keep #503 focused on the WebHelp pipeline; preserves A's papers code verbatim for the follow-up.

### [TRADEOFF FOR USER] Retrieval skill + agent cross-references scope

Issue body lists "Create llm-wiki skill that retrieves relevant chunks by topic" and "Update orcaflex/orcawave agent skills with local help references" as deliverables.

- **(R-1) In-scope for this plan.** Adds 1 skill file + 2 agent-skill modifications (cross-repo).
- **(R-2) Spin to child issues.** Keep parent pipeline clean; skill + agent updates as dependent follow-ups.

Recommended: **R-2** — parent is already T3; skill + agent updates are cheap follow-ups once the pipeline lands.

### Additional (non-tradeoff) risks

- **Polite-crawl / robots.txt.** Competitor A does not check `robots.txt`; #2318 explicitly requires it. Pipeline MUST honor robots.txt in both fetch methods.
- **Two-repo coordination.** `digitalmodel/` is a separate git repo; retiring/moving competitor B requires its own commit on that repo. Plan's acceptance criteria list this explicitly.
- **Storage convention drift.** Issue body (`/mnt/ace/...`) and #2205 operating model (`knowledge/wikis/**`) disagree. Gate resolution MUST reconcile explicitly — do not silently pick one.
- **Cadence vs. one-shot coupling.** Issue body reads as one-time seed; #2318 treats #503 as cadence input. Plan default: build idempotent, register for cadence from day one.
- **#2398 spinout risk.** If llm-wiki spins into a separate repo mid-flight, the pipeline's home moves. Plan's package boundary (`scripts/data/llm-wiki/orcina/`) is chosen to be relocatable as a unit.
- **#507 coupling risk.** If the pipeline silently hardcodes priority pages (competitor B pattern), #507 becomes trivial but every future page-add issue reopens this plan. Pipeline MUST be TOC-driven with page selection as config, not code.

### Open questions

- **Q1 (gating):** What is Orcina's exact redistribution clause? Cannot be answered from inside this pod. User or a non-restricted pod must fetch + review.
- **Q2:** Does the digitalmodel license include an internal-indexing allowance? User-side.
- **Q3:** Is #2034 (the #2205-delegated implementation owner) actively in-flight or dormant? If in-flight, this plan must coordinate to avoid a third parallel pipeline at the meta level.
- **Q4:** When #2398 spinout resolves, does the Orcina output move with llm-wiki or stay in digitalmodel?

---

## Complexity: T3

**T3** — justification:

- Multiple pipeline stages (fetch, convert, chunk, frontmatter, manifest, registry-sync, idempotency).
- Cross-repo coordination (workspace-hub + digitalmodel/ consolidation commit).
- Conformance to #2205 L1→L2→L3 layer model, #2206 GUARD-1, #2207 provenance, #2293 idempotency, #2318 cadence contract.
- Critical licensing decision blocks storage-surface choice, which cascades through most of the Files-to-Change table.
- Two existing competitors must be consolidated — choosing A, B, or a merge reshapes the implementation.
- TDD test surface is broad (toc-parse, golden conversion, chunker, frontmatter, manifest, idempotency, registry).
- T2 floor possible ONLY if user picks M-2 (live-crawl) + C-C (adopt competitor A + absorb B) + S-3 (current default path) + defers R-2 + P-2, collapsing most decisions into the cheapest path. Planner treats that as the lower bound, not the plan.
