# Plan for #2372: feat(knowledge): add canonical source-title aliasing for wiki source pages

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2372
> **Review artifacts (planned):** scripts/review/results/2026-04-27-plan-2372-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` (~1,465 lines) — canonical wiki CLI. Per `grep -n 'title' scripts/knowledge/llm_wiki.py`, current title handling is concentrated in three places:
  - `_record_to_slug()` at line 972 — derives slug from `slug | title | filename | id | record-<index>` priority order; lowercases, replaces non-alphanumerics with hyphens, truncates to 80 chars. **No alias logic.**
  - `_build_source_page()` at line 994 — line 1000: `title = record.get("title") or record.get("filename") or slug`. The fallback chain explains the current corpus pattern: when batch-ingest had only the filename, `title` was set to the filename. There is no canonical-title or alias derivation today.
  - `_update_index_for_batch_ingest()` at line ~1170 — line 1177: writes `| [[{title}]](sources/{slug}.md) | {summary} | {now_date} |` rows into the wiki `index.md`. The `[[{title}]]` link surface IS the discoverability label that the issue calls out as broken.
- Found: `FRONTMATTER_REQUIRED = {"title", "tags", "added", "last_updated"}` and `FRONTMATTER_RECOMMENDED = {"sources"}` (line 30). Neither set declares `canonical_title` or `title_aliases` today; **adding aliasing to source-page frontmatter is a strictly additive change** to the recommended/optional set, not a breaking change to the required set.
- Found: `data/document-index/conference-paper-catalog.yaml` — 30 collection entries with `name`, `path`, `total_files`, `pdf_count`, `primary_domain`, `secondary_domains`, `sample_files`, `priority`. **No per-paper title field**; this catalog is collection-level only.
- Found: `data/document-index/conference-registry.yaml` — 30 collection entries with `files`, `size_mb`, `extensions` per collection. Also collection-level only.
- Found: `data/document-index/summaries/sha256:<hex>.json` — 3 files exist (live count: `ls data/document-index/summaries/ | wc -l` returned 3). Each has `path`, `sha256`, `source`, `title`, `discipline`, `domain`, `summary`, `text_preview`, `extraction_method`, `issue`, `downstream_issue`, `ready_for_2227`, `blocker`. **`title` field is populated from extraction** (e.g., `"CSA Z276.18 LNG Production, Storage, and Handling"` for the LNG sample). This is the L2 evidence the issue alludes to with "extracted titles", but the corpus is currently 3 documents — the cross-reference layer for 19k pages is essentially empty today.
- Found: `data/document-index/promotions/2026-04-16-standards-promotion.yaml` — `- title: "CSA Z276.2-19 — Near-Shoreline FLNG Facilities"` and similar entries; this surface holds curated standards titles, not paper titles.
- Found: `data/document-index/index.jsonl` (~1.03M records) — per-document JSON-Lines surface with `path`, `host`, `source`, `content_hash`, `org`, `doc_number`, `domain`, `path_category`, `path_subcategory`, `provenance[]`. **No `title` field on the inspected lines** (live `head -3` confirmed). This is the per-document registry but it has not had titles back-populated.
- Found: existing wave-1 plan at `docs/plans/2026-04-26-issue-2363-wiki-refs-reverse-lookup.md` — sets the L3→L2 back-link pattern this plan deliberately mirrors. Confirms `index.jsonl` is the per-document L2 surface (not `registry.yaml`, which is aggregate stats).
- Gap: `grep -rn 'canonical_title\|title_aliases' scripts/ docs/ data/` returned empty — **no alias mechanism exists anywhere** in the repo today. This issue creates the contract from scratch.
- Gap: `grep -rln 'aliases' knowledge/wikis/` returned only two unrelated files (`engineering/raw/papers/network_machines.md`, `engineering/raw/papers/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`) — no frontmatter alias mechanism in any existing wiki page.

### Standards
Not applicable — this is a knowledge-management/data-shape issue. No standards-derived constants are emitted, so `.claude/rules/calc-citation-contract.md` does not bind for emission. **However, the deny-list clause does bind for downstream consumer guidance**: pages under `knowledge/wikis/*/wiki/sources/` are vendor-derivative per the rule. This plan adds aliasing TO those pages so they remain navigable, but the runbook will reiterate that calc modules should still cite `wiki/standards/` and `wiki/concepts/` pages, not source pages, even after aliases land.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/sources/22035.md` — verified frontmatter shape: `title: "22035.pdf"`, `slug: 22035`, `domain: marine-engineering`, `added`, `last_updated`, `ingested`, `tags: []`. Body has a `## Metadata` table with `collection: Arctic Technology Conference`, `filename: 22035.pdf`, `path: /mnt/ace/docs/conferences/Arctic Technology Conference/2011/data/papers/22035.pdf`, `extension: .pdf`, `size_bytes`, `year: 2011`. **Crucial finding**: the `collection` and `path` fields ARE evidence available for deterministic alias derivation today, even though no canonical paper title is present.
- `knowledge/wikis/marine-engineering/wiki/sources/spe143317.md` — same shape: `title: "spe143317.pdf"`, `slug: spe143317`, `collection: Coiled Tubing & Well Intervention Conference 2011`, `path: /mnt/ace/docs/conferences/Coiled Tubing & Well Intervention Conference 2011/pdfs/spe143317.pdf`. The `spe143317` slug encodes a real-world citation alias — SPE paper number 143317 is the canonical citation for any user of the corpus. Slug-as-citation-alias is the second deterministic alias source.
- `knowledge/wikis/marine-engineering/wiki/sources/001.md` — same shape: `title: "001.PDF"`, `slug: 001`, `collection: NACE`, `path: /mnt/ace/docs/conferences/NACE/2001/PDFFILES/PAPERS/001.PDF`, `year: 2001`. Confirms `NACE 2001 paper 001` is the implicit human-readable label, derivable from `collection + year + filename-stem`.
- `knowledge/wikis/marine-engineering/wiki/index.md` — frontmatter `page_count: 19189`, `source_count: 19161` (live read 2026-04-27). The "## Entities" section uses `[[Anode]](entities/anode.md)` and `[[CadQuery]](entities/cadquery.md)` — human-readable wiki-link labels with the slug filename embedded. The "## Sources" section (per `_update_index_for_batch_ingest`) emits `[[{title}]](sources/{slug}.md)` rows. Today, those rows render as `[[22035.pdf]](sources/22035.md)` — opaque. Replacing the label with `canonical_title` (with filename preserved as alias) immediately fixes the navigation surface.
- `knowledge/wikis/engineering/CLAUDE.md` — engineering wiki frontmatter authority (referenced via the wave-1 plan's prior verification).

### Documents consulted
- Issue #2372 body — confirms 19,159 source pages in marine-engineering, 19,137 use filename-style titles, 1,458 use purely numeric titles. Live `ls knowledge/wikis/marine-engineering/wiki/sources/ | wc -l` returned **19,162** — within rounding of the issue body's 19,159 figure (3-page drift is plausible from incremental ingest after issue creation). Issue's deliverables: aliasing strategy, backfill pass, updated index/search generation, ambiguity report.
- Issue #2205 (CLOSED) — parent operating model. Defines the L2→L3 promotion pyramid; this plan operates within that contract by treating the alias as L3-frontmatter metadata (durable knowledge) and the alias-resolution index as an L2 sidecar (denormalized for query). Boundary rule: "L3 owns authoritative metadata, L2 owns reverse indexes."
- Issue #2207 (CLOSED) — provenance/reuse contract. Section 4 establishes `wiki_refs` as L2-materialized back-link from L3 citations. **Same architectural pattern applies here**: alias resolution is a back-link (alias → page) materialized at L2 from L3-emitted alias frontmatter. The plan reuses the precedent rather than inventing new architecture. `wiki_refs` plan from #2363 was deliberately sized to depend on #2360 (frontmatter `doc_key` declaration); that dependency does NOT block this plan because the source-page frontmatter already declares `title` and `slug` today, and `path`/`collection` are already in body metadata.
- Issue #2363 (OPEN) — wiki_refs reverse lookup, planned 2026-04-26 (wave-1). The plan at `docs/plans/2026-04-26-issue-2363-wiki-refs-reverse-lookup.md` is the immediate sibling and provides the L3→L2 sidecar pattern this plan adopts. **Wave-1 lesson incorporated**: that plan documented a `doc_key` vs `source_doc_key` semantic confusion. For this plan, the analogous distinction is `title` (filesystem-derived label, current frontmatter field) vs `source_title` (canonical paper/standard title, new optional field) vs `title_aliases[]` (list of alternate citation strings). The plan locks all three semantically before designing.
- `.claude/rules/calc-citation-contract.md` lines 1-19 — sources/ deny-list clause (line 15). Calc modules must NOT cite `knowledge/wikis/*/wiki/sources/` pages; they must cite `wiki/standards/<code-id>.md` or `wiki/concepts/<concept>.md`. **This rule is a CONSUMER-side citation rule, not an alias-emission rule.** Aliasing the source pages does not violate the deny-list — the deny-list still holds that consumers prefer standards/concepts pages — but aliases make the source corpus navigable as the audit-trail surface it was always meant to be.
- Sibling issues from #2372 "Related" footer: #2363 wiki-refs (planned wave-1), #2368 faceted portals, #2369 conference-summary promotion, #2207 provenance contract.

### Gaps identified
- No `canonical_title`, `source_title`, or `title_aliases` field anywhere in the repo (verified via grep).
- No alias-resolution index — given `"SPE 143317"` or `"22035.pdf"`, no script returns the citing source page(s) without grep.
- `_build_source_page()` line 1000 silently produces filename-titled pages when no extracted `title` is available — there is no deterministic-derivation pass that produces `Conference + Year + Paper-Number` style aliases from the metadata that IS available (`collection`, `year`, `filename` stem).
- The 19,161 marine-engineering source pages all need a backfill pass; the current `summaries/` corpus is only 3 files, so the backfill must derive aliases from body-metadata fields (`collection`, `path`, `year`, `filename`, `slug`) rather than relying on `summaries/<sha256>.json`.
- `wiki/index.md` "## Sources" rows render the opaque filename as the link label. Without an index-regeneration step, even after frontmatter aliases land, the user-facing index still looks broken.
- No ambiguity report — when alias derivation cannot deterministically produce a human-readable title (e.g., body `path` is missing or collection-only), the operator has no surface to triage.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-27 via `gh issue view`):
- `#2372` — OPEN — "feat(knowledge): add canonical source-title aliasing for wiki source pages"
- `#2205` — CLOSED — parent operating model
- `#2207` — CLOSED — provenance/reuse contract
- `#2363` — OPEN — wiki_refs reverse lookup (wave-1 planned)

**File existence** (live 2026-04-27):
- EXISTS: `scripts/knowledge/llm_wiki.py` (~51 KB, 1,465 lines)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/sources/` (19,162 `.md` files; live count from `ls | wc -l`)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/sources/22035.md`, `spe143317.md`, `001.md` (all three sampled with `head -25`)
- EXISTS: `knowledge/wikis/marine-engineering/wiki/index.md` (`page_count: 19189`, `source_count: 19161` per live frontmatter read)
- EXISTS: `data/document-index/conference-paper-catalog.yaml` (30 collection entries, collection-level only)
- EXISTS: `data/document-index/conference-registry.yaml` (30 collection entries, collection-level only)
- EXISTS: `data/document-index/summaries/sha256:*.json` (3 files; live `ls | wc -l` returned 3)
- EXISTS: `data/document-index/promotions/2026-04-16-standards-promotion.yaml` (curated standards titles)
- EXISTS: `data/document-index/index.jsonl` (~1.03M lines per #2363 plan; per-document, no `title` field on sampled lines)
- EXISTS: `docs/plans/2026-04-26-issue-2363-wiki-refs-reverse-lookup.md` (wave-1 sibling)
- EXISTS: `.claude/rules/calc-citation-contract.md` (sources/ deny-list at line 15)
- MISSING (this plan creates): `scripts/knowledge/source_title_aliaser.py`, `scripts/knowledge/alias_lookup.py`, `scripts/knowledge/backfill_source_aliases.py`, `scripts/knowledge/tests/test_source_aliases.py`, `scripts/knowledge/tests/fixtures/source-aliases/`, `data/document-index/source-alias-index.jsonl` (sidecar), `docs/document-intelligence/source-title-aliasing.md` (runbook), `docs/reports/source-alias-ambiguity-<date>.md` (ambiguity report).

**Line excerpts** (`scripts/knowledge/llm_wiki.py`):
```
30:FRONTMATTER_REQUIRED = {"title", "tags", "added", "last_updated"}
1000:    title = record.get("title") or record.get("filename") or slug
1014:title: "{title}"
1177:    new_rows += f"| [[{title}]](sources/{slug}.md) | {summary} | {now_date} |\n"
```

**Frontmatter shape** (`head -10 knowledge/wikis/marine-engineering/wiki/sources/22035.md`):
```
---
title: "22035.pdf"
slug: 22035
domain: marine-engineering
added: 2026-04-07
last_updated: 2026-04-07
ingested: 2026-04-07 10:31 UTC
tags: []
---
```

**Body metadata available for alias derivation** (`head -25 knowledge/wikis/marine-engineering/wiki/sources/spe143317.md`):
```
| collection | Coiled Tubing & Well Intervention Conference 2011 |
| filename | spe143317.pdf |
| path | /mnt/ace/docs/conferences/Coiled Tubing & Well Intervention Conference 2011/pdfs/spe143317.pdf |
| year | 2011 |
```

**Gap proofs**:
- `grep -rn 'canonical_title\|title_aliases' scripts/ docs/ data/` → empty → confirms no alias mechanism exists today.
- `grep -rln 'aliases' knowledge/wikis/` → only `engineering/raw/papers/network_machines.md` and `WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` (both unrelated to frontmatter aliasing) → confirms no wiki-frontmatter alias contract exists.
- `head -3 data/document-index/index.jsonl` returned three records, none with a `title` field → confirms the L2 per-document surface has no canonical title to read from today.
- `ls data/document-index/summaries/ | wc -l` returned 3 → confirms the L2 summaries corpus is 3 documents, not anywhere near 19,161; backfill cannot rely on it.

**Source count verification:** Issue #2372 body + parent #2205 + sibling #2207 + wave-1 #2363 plan + 3 wiki source pages (`22035.md`, `spe143317.md`, `001.md`) + wiki `index.md` + `conference-paper-catalog.yaml` + `conference-registry.yaml` + 1 sampled summary JSON + `promotions/2026-04-16-standards-promotion.yaml` + `index.jsonl` + `.claude/rules/calc-citation-contract.md` + `_template-issue-plan.md` = **13 distinct sources**, far above the ≥3 minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2372-source-title-aliasing.md` (when promoted from /tmp staging) |
| Aliaser helper module | `scripts/knowledge/source_title_aliaser.py` (new) |
| Alias lookup CLI | `scripts/knowledge/alias_lookup.py` (new) |
| Bounded backfill tool | `scripts/knowledge/backfill_source_aliases.py` (new) |
| `llm_wiki.py` integration | `scripts/knowledge/llm_wiki.py` — modify `_build_source_page()` and `_update_index_for_batch_ingest()` to emit + render alias fields |
| Tests | `scripts/knowledge/tests/test_source_aliases.py` (new) |
| Test fixtures | `scripts/knowledge/tests/fixtures/source-aliases/` (synthetic source pages + catalog rows) |
| L2 sidecar — alias resolution index | `data/document-index/source-alias-index.jsonl` (new) |
| Runbook | `docs/document-intelligence/source-title-aliasing.md` (new) |
| Ambiguity report (per backfill run) | `docs/reports/source-alias-ambiguity-<date>.md` (new) |
| Plan index update | `docs/plans/README.md` (add row when plan is promoted) |
| Plan review — Claude | `scripts/review/results/2026-04-27-plan-2372-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-27-plan-2372-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-27-plan-2372-gemini.md` |

**Why a JSONL sidecar at L2 (matching #2363):** the alias-resolution path needs a fast `alias-string → page-paths` query without grepping 19k frontmatter blocks. Mutating `index.jsonl` (1.03M rows, written by the indexer) creates merge contention; a separate `source-alias-index.jsonl` keyed by lower-cased alias string is write-isolated, cheap to rebuild from L3 frontmatter, and consistent with #2207 Section 4's "L2 owns reverse indexes" rule. The runbook names this file as the canonical alias-resolution surface; the L3 frontmatter is the authoritative source.

---

## Semantic contract — title vs source_title vs title_aliases

To pre-empt the wave-1 #2363 doc_key vs source_doc_key confusion, this plan locks the field semantics before designing:

| Field | Layer | Purpose | Example | Backward-compat |
|---|---|---|---|---|
| `title` | L3 frontmatter (existing — required) | Display label the wiki renderer / index.md uses | `"22035.pdf"` (today) → `"OTC 22035 — Arctic Sea-Ice Loading on Subsea Structures"` (post-backfill, when derivable) | Field stays required; value is upgraded in place when alias derivation is deterministic. |
| `source_title` | L3 frontmatter (new — optional, recommended) | Canonical paper / standard title as published, when known | `"OTC 22035 — Arctic Sea-Ice Loading on Subsea Structures"` | Optional; only emitted when extracted from `summaries/` JSON or curated `promotions/` YAML. Never derived from filename/slug alone. |
| `title_aliases` | L3 frontmatter (new — optional) | Sorted list of all known alternate citation strings (filename, slug, conference+year+paper-number, citation-style abbreviations) | `["22035.pdf", "OTC 22035", "OTC-22035-2011", "Arctic Technology Conference 2011 paper 22035"]` | Optional; the original raw filename is always preserved as one alias for stability per issue acceptance criterion 3. |
| `alias_provenance` | L3 frontmatter (new — optional) | Per-alias source tag so reviewers can audit whether an alias is `filename`, `slug`, `derived:collection+year+stem`, `summary:sha256:...`, or `curated:promotions/<file>.yaml` | `{"OTC 22035": "derived:collection+year+stem", "22035.pdf": "filename"}` | Optional; populated whenever the aliaser writes. |

**Key semantic rules:**
1. `title` is the rendered label; `source_title` is the authoritative scholarly/standards citation; `title_aliases` is the discovery surface. They are **three distinct concerns** and must not collapse into one field.
2. The aliaser only sets `title = source_title` if `source_title` is derived deterministically from a high-confidence source (extracted summary JSON, curated promotion YAML, or a strict `collection + year + paper-number` rule that produces an unambiguous string). If alias derivation is ambiguous, `title` stays as filename and the page is reported in the ambiguity log.
3. The original raw filename is **always** in `title_aliases` (per issue criterion 3: "raw filenames are preserved as aliases for stability").
4. Slug-style aliases (e.g., `spe143317`) are emitted into `title_aliases` only when the slug encodes a real-world citation pattern (regex match: `^(spe|otc|isope|ipc|nace|imeche|ieee|asce|asme|api|dnv)[-_]?\d+$`); pure-numeric slugs (e.g., `001`, `22035`) are NOT emitted as standalone aliases because they collide across collections — they are only emitted with collection-disambiguation prefix.

---

## Deliverable

A canonical-title aliasing path for wiki source pages, comprising:
1. A `source_title_aliaser` helper module that, given a wiki source page (or a record on its way to becoming one), derives `source_title` (when deterministic), `title_aliases[]`, and `alias_provenance{}` from the four available evidence sources (extracted-summary JSON, curated promotion YAML, body-metadata `collection`+`year`+`filename`, slug pattern).
2. Integration into `scripts/knowledge/llm_wiki.py` so newly batch-ingested pages emit alias fields up front, and the index renderer (`_update_index_for_batch_ingest`) prefers `title` (which may now be the upgraded canonical title) over `slug`.
3. An `alias_lookup.py` CLI returning citing source pages for a given alias string with deterministic exit codes.
4. A bounded `backfill_source_aliases.py` tool that walks existing source pages with `--domains` and `--limit` flags, derives aliases from available evidence, writes the L2 sidecar `data/document-index/source-alias-index.jsonl`, and emits an ambiguity report listing pages that could not be safely upgraded.
5. A runbook documenting the alias contract, derivation rules, deny-list interaction, and operational cadence.
6. Backfill execution scoped to the marine-engineering corpus first (19k pages, the issue's stated start point), with engineering and naval-architecture as smaller follow-on waves.

---

## Scope boundaries (explicit)

- **In scope:** alias emission for `knowledge/wikis/marine-engineering/wiki/sources/*.md` first wave; aliaser module reusable for engineering, naval-architecture, maritime-law on later waves.
- **In scope:** `source_title` derivation only when a deterministic source exists. The four evidence sources, in priority order:
  1. **Extracted summary JSON** — `data/document-index/summaries/<content_hash>.json` `title` field. High confidence. Currently covers ~3 documents; will grow as #2227 / extraction work lands.
  2. **Curated promotion YAML** — `data/document-index/promotions/*.yaml` curated `title:` strings. High confidence; small surface (~10s of standards).
  3. **Body-metadata derivation** — combine `collection`, `year`, filename-stem from the wiki source page body's `## Metadata` table to produce a `<Collection> <Year> paper <stem>` style canonical. Medium confidence; produces unambiguous label only when collection name + year + stem are all present and the stem looks like a paper number.
  4. **Slug-pattern derivation** — when slug matches a known citation prefix (`spe`, `otc`, `isope`, etc.), emit `<PREFIX> <NUMBER>` as an alias. Medium confidence; safe because the prefix is a well-known venue identifier.
- **In scope (first L2 surface):** `data/document-index/source-alias-index.jsonl` (new sidecar, JSONL, line shape `{"alias": "<lowercased>", "alias_raw": "<original>", "source_pages": [...], "provenance": {...}}`).
- **In scope:** `wiki/index.md` "## Sources" row regeneration so the link label uses the upgraded `title` rather than slug-based filename label. Implemented as a single-pass renderer that reads each source page's frontmatter and rewrites the row.
- **Out of scope:** human-curated alias entry. v1 ships only deterministic derivation. A future issue can add a `data/document-index/curated-source-aliases.yaml` for cases that need manual override.
- **Out of scope:** PDF re-extraction. Backfill reads existing wiki frontmatter + existing summaries/promotions only. No new PDF parsing.
- **Out of scope:** unrenaming wiki source files. The filesystem path stays at `<slug>.md`. Only frontmatter and the index-rendered label change. This preserves all existing inbound links per issue criterion 4 ("preserves stable links").
- **Out of scope:** alias materialization for `wiki/standards/`, `wiki/concepts/`, `wiki/entities/` — those pages already have human-readable titles by construction; the issue is specifically about source pages.
- **Out of scope:** real-time alias re-derivation on every `git rm` or external file change (deferred per "Open Questions"); the periodic backfill handles staleness.

---

## Pseudocode

### Aliaser (derives alias fields from evidence)

```
PRIORITY_SOURCES = ["summary_json", "curated_promotion", "body_metadata", "slug_pattern"]
SLUG_VENUE_RE = re.compile(r"^(spe|otc|isope|ipc|nace|imeche|ieee|asce|asme|api|dnv|iso)[-_]?(\d+)$", re.I)

def derive_aliases(page_path):
    fm = parse_frontmatter(page_path)
    body_meta = extract_metadata_table(page_path)   # {collection, filename, path, year, ...}
    slug = fm["slug"]
    raw_title = fm["title"]                          # current value (often filename)

    # Always preserve raw filename as an alias for stability.
    aliases = {raw_title: "filename"}                # dict to track provenance per alias

    source_title = None
    title_to_render = raw_title

    # 1. Extracted summary JSON (highest confidence).
    sha = lookup_content_hash(body_meta.get("path"))   # via index.jsonl
    if sha and (summary := load_summary_json(sha)):
        if t := summary.get("title"):
            source_title = t
            title_to_render = t
            aliases[t] = f"summary:{sha}"

    # 2. Curated promotion YAML.
    if not source_title:
        for promo_file in iter_promotions():
            if t := match_promotion_title(body_meta, promo_file):
                source_title = t
                title_to_render = t
                aliases[t] = f"curated:{promo_file.name}"
                break

    # 3. Body-metadata derivation.
    if collection := body_meta.get("collection"):
        year = body_meta.get("year", "")
        stem = Path(body_meta.get("filename", "")).stem
        if collection and year and stem:
            derived = f"{collection} {year} paper {stem}"
            if not source_title:
                title_to_render = derived
            aliases[derived] = "derived:collection+year+stem"

    # 4. Slug-pattern derivation.
    if m := SLUG_VENUE_RE.match(slug):
        prefix, number = m.group(1).upper(), m.group(2)
        venue_alias = f"{prefix} {number}"
        aliases[venue_alias] = "derived:slug+venue-pattern"
        # If no other source produced source_title, this becomes a candidate label.
        if not source_title and not body_meta.get("collection"):
            title_to_render = venue_alias
            source_title = venue_alias

    return AliasResult(
        title=title_to_render,
        source_title=source_title,            # may still be None
        title_aliases=sorted(aliases.keys()),
        alias_provenance=aliases,
        is_ambiguous=(source_title is None),
    )
```

### Aliaser write path (mutates one page atomically)

```
def apply_aliases(page_path, result, dry_run=False):
    if dry_run:
        log(f"DRY-RUN would update {page_path}: title→{result.title}, aliases={len(result.title_aliases)}")
        return

    fm, body = read_page(page_path)
    fm["title"] = result.title
    if result.source_title:
        fm["source_title"] = result.source_title
    fm["title_aliases"] = result.title_aliases
    fm["alias_provenance"] = result.alias_provenance
    fm["last_updated"] = today_iso()
    atomic_write(page_path, render(fm, body))      # tempfile + rename
    update_sidecar(SIDECAR, page_path, result)     # under file lock
```

### L2 sidecar (alias-resolution index)

```
SIDECAR = data/document-index/source-alias-index.jsonl
LOCKDIR = data/document-index/.locks/

def update_sidecar(sidecar_path, page_path, result):
    with file_lock(LOCKDIR / "source-alias-index.lock"):
        index = load_jsonl_as_index(sidecar_path)   # {alias_lower: {alias_raw, pages_set, provenance}}
        rel_path = repo_relative(page_path)
        # remove any prior entries that pointed at this page
        for alias_lower, entry in list(index.items()):
            entry["source_pages"].discard(rel_path)
            if not entry["source_pages"]:
                del index[alias_lower]
        # add new entries
        for alias_raw, prov in result.alias_provenance.items():
            key = alias_raw.lower()
            entry = index.setdefault(key, {"alias_raw": alias_raw, "source_pages": set(), "provenance": {}})
            entry["source_pages"].add(rel_path)
            entry["provenance"][rel_path] = prov
        atomic_write_jsonl(sidecar_path, index)     # sorted by alias_lower for deterministic diffs
```

### Alias lookup CLI (mirrors `doc-key-lookup.py` shape)

```
def lookup(alias_string, json_out=False):
    key = alias_string.strip().lower()
    if not key:
        sys.exit(2)                                  # malformed
    sidecar = load_jsonl_as_index(SIDECAR)
    entry = sidecar.get(key)
    if not entry:
        sys.exit(3)                                  # valid input, no hits
    pages = sorted(entry["source_pages"])
    print_pages(pages, json_out, alias_raw=entry["alias_raw"], provenance=entry["provenance"])
    sys.exit(0)
```

Exit codes (mirror existing convention): `0` = ≥1 hit; `2` = empty/malformed input; `3` = valid input but no hits.

### Bounded backfill

```
def backfill(domains=None, limit=500, dry_run=False):
    counts = {"visited": 0, "upgraded": 0, "ambiguous": 0,
              "summary_json_hit": 0, "promotion_hit": 0,
              "body_meta_hit": 0, "slug_pattern_hit": 0}
    ambiguous_pages = []
    for page in iter_source_pages(domains):
        counts["visited"] += 1
        if limit and counts["visited"] > limit and limit != 0:
            break
        result = derive_aliases(page)
        if result.is_ambiguous:
            counts["ambiguous"] += 1
            ambiguous_pages.append(page)
        else:
            counts["upgraded"] += 1
        increment_provenance_counters(counts, result)
        apply_aliases(page, result, dry_run=dry_run)
    write_ambiguity_report(f"docs/reports/source-alias-ambiguity-{today}.md",
                           ambiguous_pages, counts)
    write_index_regeneration_log(...)
```

### Index renderer change (`_update_index_for_batch_ingest`)

```
# Current (line ~1177):
new_rows += f"| [[{title}]](sources/{slug}.md) | {summary} | {now_date} |\n"

# After:
display = entry.get("source_title") or entry.get("title") or slug
new_rows += f"| [[{display}]](sources/{slug}.md) | {summary} | {now_date} |\n"
```

The change is one line in the existing function; the upstream `entry` dict is widened to carry `source_title` when the aliaser produced one.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/source_title_aliaser.py` | helper module: derive `source_title` + `title_aliases` + provenance |
| Create | `scripts/knowledge/alias_lookup.py` | reverse query CLI: alias-string → source pages |
| Create | `scripts/knowledge/backfill_source_aliases.py` | bounded backfill |
| Modify | `scripts/knowledge/llm_wiki.py` | (a) call aliaser from `_build_source_page()` so new pages emit alias fields; (b) widen `_update_index_for_batch_ingest` to render `source_title` when present; (c) extend `FRONTMATTER_RECOMMENDED` to include `source_title`, `title_aliases`, `alias_provenance` |
| Create | `scripts/knowledge/tests/test_source_aliases.py` | TDD coverage for aliaser + CLI + backfill + integration |
| Create | `scripts/knowledge/tests/fixtures/source-aliases/` | synthetic source pages + summary JSON + promotion YAML |
| Create | `data/document-index/source-alias-index.jsonl` | L2 sidecar; written by backfill on first run |
| Create | `docs/document-intelligence/source-title-aliasing.md` | runbook + alias contract + deny-list interaction note + cadence |
| Create | `docs/reports/source-alias-ambiguity-<date>.md` | ambiguity report (one per backfill run; first run on marine-engineering only) |
| Update | `docs/plans/README.md` | add this plan row when promoted from /tmp |

Tooling and data ship in **separate** PRs to keep review surfaces clean: PR-A introduces the aliaser/CLI/backfill/tests/runbook (no frontmatter mutation). PR-B runs `--dry-run` over marine-engineering and commits the dry-run report only. PR-C runs the bounded marine-engineering backfill (default `--limit 500`) and commits the resulting frontmatter delta + sidecar + ambiguity report. PR-D extends to the full 19k corpus only after the bounded run is reviewed.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_aliaser_summary_json_priority` | summary-JSON title wins over body-metadata derivation | fixture: page + matching summary JSON | `source_title` = summary's title; `alias_provenance` records `summary:<sha>` |
| `test_aliaser_promotion_yaml_priority` | curated promotion title wins over body-metadata when no summary | fixture: page + promotion YAML row | `source_title` = promotion title; provenance `curated:<file>.yaml` |
| `test_aliaser_body_metadata_derivation` | `<collection> <year> paper <stem>` produced when collection+year+stem all present | fixture: page with collection=Arctic, year=2011, filename=22035.pdf | `title_aliases` includes `"Arctic Technology Conference 2011 paper 22035"`; provenance `derived:collection+year+stem` |
| `test_aliaser_slug_pattern_spe` | slug `spe143317` emits `SPE 143317` alias | fixture | alias `"SPE 143317"` present; provenance `derived:slug+venue-pattern` |
| `test_aliaser_slug_pattern_pure_numeric_skipped` | pure-numeric slug `22035` does NOT emit standalone alias | fixture | no `"22035"` standalone in aliases (only `22035.pdf` raw filename) |
| `test_aliaser_filename_always_preserved` | raw filename is in `title_aliases` regardless of other sources | every fixture | `title_aliases` always contains the original `title` value |
| `test_aliaser_ambiguous_when_no_evidence` | page with empty body metadata, no summary, slug not a venue pattern | fixture: bare page | `is_ambiguous=True`; `title` stays as filename; reported in ambiguity list |
| `test_aliaser_idempotent` | re-running aliaser on already-aliased page yields identical output | fixture | second invocation produces zero dirty writes (hash compare) |
| `test_aliaser_concurrent_writes_serialize` | two backfill processes serialize via file lock | fork two backfill invocations | sidecar contains both updates; no lost write |
| `test_apply_aliases_atomic_write` | apply_aliases uses temp+rename; partial-write does not corrupt page | inject crash mid-write | original page intact; no `.tmp` file left behind |
| `test_apply_aliases_preserves_existing_frontmatter_fields` | non-alias fields (`tags`, `slug`, `domain`, `added`) untouched | fixture | frontmatter retains all original fields except `last_updated` and the new alias fields |
| `test_alias_lookup_returns_pages` | `SPE 143317` returns the spe143317.md path | fixture | exit 0; one path on stdout |
| `test_alias_lookup_case_insensitive` | `spe 143317` and `SPE 143317` both hit | fixture | identical output |
| `test_alias_lookup_no_hits_exits_3` | unknown alias returns exit 3 | `"Nonexistent Paper"` | exit 3, empty stdout |
| `test_alias_lookup_malformed_exits_2` | empty input | `""` | exit 2 |
| `test_alias_lookup_json_output_shape` | `--json` returns parseable JSON matching `doc-key-lookup.py` shape | fixture | `json.loads(stdout)` succeeds; keys include `alias_raw`, `pages`, `provenance` |
| `test_backfill_dry_run_writes_nothing` | `--dry-run` does not mutate frontmatter or sidecar | fixture (10 pages) | byte-identical inputs after run; ambiguity report still written |
| `test_backfill_bounded_by_limit` | `--limit 5` stops after 5 pages | fixture (20 pages) | exactly 5 visited, 15 untouched |
| `test_backfill_unbounded_only_with_explicit_zero` | `--limit 0` required for unbounded | default invocation on 30-page fixture | default runs at most 500; only `--limit 0` triggers full sweep |
| `test_backfill_ambiguity_report_shape` | report has all telemetry counters + per-page rows | fixture | report file contains `visited`, `upgraded`, `ambiguous`, per-source-hit counters, list of ambiguous page paths |
| `test_backfill_does_not_rename_files` | filesystem path stays at `<slug>.md` | fixture | no `git mv`-like operation; only frontmatter changes |
| `test_index_renderer_uses_source_title_when_present` | `_update_index_for_batch_ingest` renders `source_title` over `title` over `slug` | fixture: entry dict with `source_title="OTC 22035 ..."`, `title="22035.pdf"`, `slug="22035"` | rendered row label is `[[OTC 22035 ...]](sources/22035.md)` |
| `test_index_renderer_falls_back_to_title_when_no_source_title` | `source_title` absent → uses `title` | fixture | label is `[[<title>]]` |
| `test_index_renderer_falls_back_to_slug_when_neither` | both absent → uses slug | fixture | label is `[[<slug>]]` |
| `test_deny_list_unaffected` | aliasing source pages does NOT cause anything to cite them as authoritative | runbook scrape | runbook explicitly states the `.claude/rules/calc-citation-contract.md` deny-list is unchanged |
| `test_deterministic_sidecar_ordering` | sidecar JSONL is byte-identical across two backfill runs | fixture | byte-identical output |
| `test_filename_alias_stability_after_rerun` | re-running backfill never drops the raw filename alias | fixture: prior run + new run | filename alias persists |

All tests run via `uv run pytest scripts/knowledge/tests/test_source_aliases.py -v`. Full regression: `uv run pytest scripts/knowledge/tests/ -v`.

---

## Acceptance Criteria

Mirroring issue #2372 acceptance criteria, with given/when/then phrasing:

- [ ] **Given** a wiki source page with derivable alias evidence, **when** the operator runs `uv run scripts/knowledge/backfill_source_aliases.py --domains marine-engineering --limit 500 --dry-run`, **then** the page's frontmatter would be upgraded with `source_title` (when derivable), `title_aliases[]` containing at least the raw filename plus all derivable aliases, and `alias_provenance{}` recording the source of each alias.
- [ ] **Given** an alias string (e.g., `"SPE 143317"` or `"22035.pdf"`), **when** the operator runs `uv run scripts/knowledge/alias_lookup.py "<alias>"`, **then** the citing source page paths are returned (one per line, lexicographically sorted) with exit 0, without invoking grep — satisfies issue criterion 1 ("source pages can be discovered by canonical title or known alias rather than only raw filename").
- [ ] **Given** the marine-engineering corpus of 19,161 source pages, **when** the bounded backfill runs with default `--limit 500`, **then** at most 500 pages are processed in the first pass; `--limit 0` is the only path to a full-corpus sweep, completes in under five wall-clock minutes on the reference machine, and the resulting frontmatter delta is reviewable in a single PR.
- [ ] **Given** a page that the aliaser cannot deterministically upgrade (no summary, no promotion match, no usable body metadata, no venue-pattern slug), **when** backfill processes it, **then** the page is logged in `docs/reports/source-alias-ambiguity-<date>.md` with the reason for skip, and its `title` field is left untouched — satisfies issue's "explicit ambiguity report" deliverable.
- [ ] **Given** every source page that the aliaser DID upgrade, **when** the operator inspects the page, **then** the raw filename appears in `title_aliases` — satisfies issue criterion 3 ("raw filenames are preserved as aliases for stability").
- [ ] **Given** the wiki `index.md` "## Sources" section, **when** the index regeneration step runs after backfill, **then** rows render with `source_title` (or upgraded `title`) as the link label, and the link itself still points at `sources/<slug>.md` — satisfies issue criterion 4 ("wiki index/search surfaces prefer readable titles without breaking links").
- [ ] **Given** a calc module wiring per `.claude/rules/calc-citation-contract.md`, **when** a reviewer audits the runbook, **then** the runbook explicitly reaffirms the sources/ deny-list (consumers cite `wiki/standards/` / `wiki/concepts/`, not source pages) and clarifies that aliasing does not change consumer-side citation rules.
- [ ] All new tests pass: `uv run pytest scripts/knowledge/tests/test_source_aliases.py -v`.
- [ ] No regression: `uv run pytest scripts/knowledge/tests/ -v` passes.
- [ ] Review artifacts present at `scripts/review/results/2026-04-27-plan-2372-{claude,codex,gemini}.md` with non-`MAJOR` final verdicts.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (cross-review dispatch follows plan promotion from `/tmp/overnight-plans/wave-3/` to `docs/plans/`).

---

## Risks and Open Questions — adversarial pre-emption

- **Risk: "Title vs source_title vs title_aliases is confusing — same wave-1 #2363 mistake."** Mitigation: the "Semantic contract" table above locks the three fields to three distinct purposes (rendered label, authoritative citation, discovery surface). Tests `test_aliaser_filename_always_preserved`, `test_index_renderer_uses_source_title_when_present`, `test_aliaser_summary_json_priority` lock the precedence. Runbook restates the contract.

- **Risk: "Alias derivation produces wrong canonical titles for ambiguous pages."** Mitigation: derivation is **strictly conservative** — `source_title` is only set when a high-confidence source produced it, and the rules table is explicit about which sources count as high-confidence. Pure-numeric slugs are NEVER promoted to standalone aliases (test `test_aliaser_slug_pattern_pure_numeric_skipped`). Pages without high-confidence sources stay at filename-title and land in the ambiguity report — no silent guessing.

- **Risk: "Filesystem rename will break links."** This plan **does not rename files**. Frontmatter `title` upgrades and `index.md` label upgrades only. Filesystem path stays at `sources/<slug>.md`. Test `test_backfill_does_not_rename_files`. Issue criterion 4 ("preserves stable links") is satisfied by construction.

- **Risk: "19k pages is a backfill liability."** Mitigation: (a) default `--limit 500`; (b) `--limit 0` (unbounded) is opt-in; (c) backfill is read-only at the filesystem level (no PDF re-extraction); (d) ambiguity report flags pages that need follow-up; (e) bounded-then-extend PR sequencing (PR-B dry-run, PR-C bounded, PR-D full).

- **Risk: "What if the aliaser disagrees with itself across runs?"** Mitigation: derivation is deterministic given identical evidence. Tests `test_aliaser_idempotent` and `test_deterministic_sidecar_ordering` lock byte-identical output across runs. The aliaser does not call the network or any randomized source.

- **Risk: "Concurrent backfill / `llm_wiki.py` ingest writes corrupt the sidecar."** Mitigation: emitter and backfill share the same `data/document-index/.locks/source-alias-index.lock` file lock, mirroring the wave-1 #2363 plan. Test `test_aliaser_concurrent_writes_serialize` covers a fork-fork scenario.

- **Risk: "Sources/ deny-list violation."** Per `.claude/rules/calc-citation-contract.md` line 15, calc modules must NOT cite `knowledge/wikis/*/wiki/sources/`. This plan adds aliases TO source pages but does NOT add any new emission point that cites them. The runbook explicitly reiterates the consumer-side deny-list. Aliases make audit-trail navigation work without changing the citation rule. Test `test_deny_list_unaffected` documents this in the runbook.

- **Risk: "Plan describes proposed work as committed artifacts."** Per memory `feedback_plan_past_tense_artifact_claims.md`, this plan uses future tense throughout. Verification: re-read — the plan only describes what *will* exist (aliaser, CLI, backfill, tests, runbook, sidecar, ambiguity report), never claims they exist now.

- **Risk: "Mock vs. live invocation divergence."** Per memory `feedback_mock_vs_live_invocation_divergence.md`. The TDD fixtures use synthetic pages and synthetic summary JSON. Before plan-approval close-out, run a live invocation: pick `sources/spe143317.md` (high-confidence slug-pattern case), run `--dry-run` over it, verify the alias derivation produces `["SPE 143317", "spe143317.pdf", "Coiled Tubing & Well Intervention Conference 2011 paper spe143317"]`, then revert. Capture the live shell session in the runbook.

- **Risk: "llm-wiki hyphen-path pattern."** Per memory `feedback_llm_wiki_hyphen_module_path_pattern.md`. The path `scripts/knowledge/llm_wiki.py` uses underscore (verified: `grep -n title scripts/knowledge/llm_wiki.py` succeeded). No hyphenated module path is referenced in this plan; new files use underscore (`source_title_aliaser.py`, `alias_lookup.py`, `backfill_source_aliases.py`). Smell-check: `grep -n 'llm-wiki\.' <plan>` returns empty.

- **Risk: "Sidecar growth at 19k pages."** Each page contributes ~3-5 alias entries at ~150 bytes per JSONL line → ~10-15 MB sidecar. Below the 200 MB embed-vs-spinout trigger from memory `project_llm_wiki_stays_embedded.md`. Acceptable for v1.

- **Open: should `source_title` be promoted to `FRONTMATTER_REQUIRED`?** Proposal: stay optional/recommended for v1 because not every page can derive it. Promoting to required would break ingest for ambiguous pages. Flag for user.

- **Open: pre-commit-hook integration.** Proposal: CLI-only for v1; flag for user. A pre-commit hook would catch source pages that land without alias frontmatter, but adds latency to every commit and the periodic backfill is sufficient.

- **Open: when `body_meta.get("path")` references `/mnt/ace/...` paths that aren't readable on the current machine.** The aliaser doesn't actually OPEN the source PDF — it just looks up `content_hash` in `index.jsonl`. So machine-mount differences shouldn't bite. Verify on dispatch.

- **Open: behavior when a wiki source page has no body `## Metadata` table at all (legacy/hand-written page).** Proposal: skip body-metadata derivation, fall through to slug-pattern only, mark as ambiguous if neither produces evidence. Flag for user.

- **Open: do we materialize aliases for promotion-derived standards pages under `wiki/standards/`?** Out of scope per the issue (issue is about `wiki/sources/`), but the aliaser module is reusable. Future issue can extend.

- **Open: git-merge-race when two branches each touch the sidecar.** JSONL with disjoint alias keys merges cleanly; same-alias divergence requires conflict-marker resolution. Proposal: document in runbook; rebuild sidecar from scratch via backfill if a merge produces conflicts. Same handling as wave-1 #2363.

---

## Complexity: T2

Adds one helper module + one CLI + one backfill tool + one runbook + one ambiguity-report shape + ~26 TDD tests; modifies one existing module (`llm_wiki.py`) at three small touch points (`_build_source_page` aliaser hook, `_update_index_for_batch_ingest` label fallback, `FRONTMATTER_RECOMMENDED` extension); creates one new sidecar data file. No new architecture: the L3-frontmatter / L2-sidecar pattern is already established by #2207 contract and #2363 wave-1 plan; this plan applies it to alias resolution. The 19,161-page corpus is bounded by `--limit` rather than re-architected. Not T3 because there is no new data-model surface beyond a denormalized index of frontmatter that already exists, no migration of `index.jsonl`, no public interface change to existing CLIs (`doc-key-lookup.py` unaffected), and no PDF re-extraction. Not T1 because more than one new module + tests + runbook + integration into an existing 1,465-line module + a 19k-page backfill exceeds trivial scope.
