# Plan for #2368: feat(knowledge): generate faceted portal pages for large LLM-wiki domains

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2368
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2368-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/llm_wiki.py` (1465 lines) — canonical LLM-wiki CLI with `init`/`ingest`/`query`/`lint`/`status`/`batch-ingest` subcommands, `REPO_ROOT`-anchored path resolution, YAML frontmatter parsing helpers, and `WIKIS_DIR = REPO_ROOT / "knowledge" / "wikis"`. The frontmatter schema constants (`FRONTMATTER_REQUIRED`, `FRONTMATTER_RECOMMENDED`, `FRONTMATTER_OPTIONAL`) already cover `title`, `tags`, `sources`, `domain`, `added`, `last_updated`.
- Found: `scripts/knowledge/wiki-cross-links.py` and `scripts/knowledge/wiki-cross-links.sh` — prior wiki-side generated artifact proving the pattern "scripted, reproducible, non-hand-edited output linked from index pages" (precedent for the portal generator).
- Gap: no portal/facet generator subcommand or standalone script exists under `scripts/knowledge/`. Verified by `ls scripts/knowledge/ | grep -i -E 'portal|facet'` returning no results.

### Standards
Not applicable — `cat:documentation` issue; no engineering standards are exercised by this plan.

### LLM Wiki pages consulted
- `knowledge/wikis/marine-engineering/wiki/index.md` — 21,611 lines; flat page tables (Entities/Concepts/Sources); target of first generated portal.
- `knowledge/wikis/marine-engineering/wiki/` — tree organized as `entities/` (15 pages), `concepts/` (11 pages), `sources/` (19,161 pages), `comparisons/`, `visualizations/`.
- `knowledge/wikis/marine-engineering/CLAUDE.md` — binding frontmatter schema: `title`, `tags`, `added`, `last_updated` required; `sources`, `domain`, `cross_links` recommended/optional. Portal must consume these fields read-only.
- `knowledge/wikis/engineering/wiki/index.md` (121 lines) and `knowledge/wikis/naval-architecture/wiki/index.md` (77 lines) — small domains do NOT warrant faceted portals; this plan constrains scope to large domains only.

### Documents consulted
- Issue body — acceptance criteria: generated portal for marine-engineering; linked from wiki/domain navigation; reproducible generation; does not replace canonical `index.md`.
- `docs/document-intelligence/intelligence-accessibility-map.md` line 180 — explicitly names marine-engineering as "19K pages with no curated entry beyond the index"; this issue directly addresses the line-180 weakness.
- `docs/document-intelligence/README.md` lines 28-33 — points humans at each domain's `wiki/index.md`; identified as the secondary navigation surface to link from.
- Related: `docs/plans/2026-04-13-issue-2096-intelligence-accessibility-map.md` — accessibility-map plan (closed, completed); this is its follow-on enhancement.
- Related: #2366 strengthening scorecard (from issue body) — portal is an *input signal* to prioritization, not a dependency.

### Gaps identified
- No existing faceted/portal generator — must be built.
- No generator-output convention inside `knowledge/wikis/*/wiki/` — must define portal filenames and idempotent regeneration contract.
- No "large-domain threshold" rule to decide which domains get portals — must specify and enforce.
- No linking convention in `docs/document-intelligence/README.md` or domain `wiki/index.md` for portal pages — must define.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2368` — OPEN — "feat(knowledge): generate faceted portal pages for large LLM-wiki domains"
- `#2096` — CLOSED — "feat(knowledge): intelligence accessibility map for llm-wikis and document/resource intelligence"
- `#2205` — OPEN — parent operating-model
- `#2366` — referenced in issue body; treated as downstream consumer, not blocker

**File existence** (`ls -la` 2026-04-23):
- EXISTS: `knowledge/wikis/marine-engineering/wiki/index.md` (21,611 lines)
- EXISTS: `scripts/knowledge/llm_wiki.py` (1,465 lines)
- EXISTS: `knowledge/wikis/engineering/wiki/index.md` (121 lines)
- EXISTS: `knowledge/wikis/naval-architecture/wiki/index.md` (77 lines)
- EXISTS: `docs/document-intelligence/intelligence-accessibility-map.md` (521 lines)
- EXISTS: `docs/document-intelligence/README.md` (57 lines)
- MISSING (new — this plan creates): `scripts/knowledge/generate_wiki_portal.py`
- MISSING (new — this plan creates): `knowledge/wikis/marine-engineering/wiki/portal.md`
- MISSING (new — this plan creates): `scripts/knowledge/tests/test_generate_wiki_portal.py`

**Line excerpts** (accessibility map, line 180):
```
| Marine-engineering wiki | L3 | `knowledge/wikis/marine-engineering/wiki/` | `CLAUDE.md` per wiki, `wiki/index.md`, `docs/README.md` | Agent + Human | **Discoverable** | Now linked from `docs/README.md`; 19K pages with no curated entry beyond the index |
```

**Gap proofs**:
- `ls scripts/knowledge/ | grep -i -E 'portal|facet'` → empty → confirms no prior portal generator.
- `grep -n "portal" knowledge/wikis/marine-engineering/wiki/index.md | head -3` → no matches → confirms no existing portal linkage.

**Source count verification:** 3 distinct sources (issue body + accessibility-map + llm_wiki.py codebase) — minimum met.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2368-faceted-portal-pages.md` |
| Implementation | `scripts/knowledge/generate_wiki_portal.py` |
| Tests | `scripts/knowledge/tests/test_generate_wiki_portal.py` |
| First generated portal | `knowledge/wikis/marine-engineering/wiki/portal.md` |
| Portal design doc | `docs/document-intelligence/llm-wiki-portal-design.md` |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2368-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2368-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2368-gemini.md` |
| Navigation update 1 | `knowledge/wikis/marine-engineering/wiki/index.md` (add portal link) |
| Navigation update 2 | `docs/document-intelligence/README.md` (add portal link under marine-engineering row) |

---

## Deliverable

A `scripts/knowledge/generate_wiki_portal.py` generator that, when invoked for a large wiki domain (initial: marine-engineering), will produce an idempotent `wiki/portal.md` faceting the domain by page type, tags/subdomain, standards/tools, and top-entry pages — linked from `wiki/index.md` and `docs/document-intelligence/README.md`, with a design doc spelling out the extend-vs-create rule for future domains.

---

## Pseudocode

```
function generate_wiki_portal(domain, out_path="wiki/portal.md", threshold=500):
    wiki_root = REPO_ROOT / "knowledge" / "wikis" / domain / "wiki"
    pages = enumerate all *.md under wiki_root, excluding index.md and portal.md itself
    if len(pages) < threshold and not --force:
        print "domain too small; skipping"; exit 0

    parsed = [parse_frontmatter(p) for p in pages]   # reuses llm_wiki.py helpers

    facets = {
        "by_page_type": group_by_parent_dir(parsed),      # entities / concepts / sources / comparisons / visualizations
        "by_tag": group_by_frontmatter_tag(parsed),       # top-N tags only, configurable
        "by_standard": filter_where_source_matches_standard_regex(parsed),
                                                          # e.g. ^(api|dnv|iso|astm|nace)-
        "top_entries": rank_by_inbound_link_count(parsed, wiki_root),
                                                          # count [[page]] wiki-links pointing at each page
    }

    rendered = render_portal_markdown(domain, facets, generated_at=utcnow())
    write_atomic(wiki_root / out_path, rendered)          # temp + rename

    return counts_per_facet                                # used by tests
```

Idempotency contract: re-running the generator against the same inputs must yield byte-identical output except for a single `last_generated` line in the YAML frontmatter. This is enforced via a test that runs the generator twice and diffs everything except that one line.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/generate_wiki_portal.py` | main implementation (CLI + library functions) |
| Create | `scripts/knowledge/tests/test_generate_wiki_portal.py` | TDD test suite |
| Create | `knowledge/wikis/marine-engineering/wiki/portal.md` | generated artifact (committed for reviewability; regenerated, not hand-edited) |
| Create | `docs/document-intelligence/llm-wiki-portal-design.md` | portal design + extend-vs-create guidance |
| Modify | `knowledge/wikis/marine-engineering/wiki/index.md` | add "Curated portal" link near top |
| Modify | `docs/document-intelligence/README.md` | add portal column/link for large domains |
| Update | `docs/plans/README.md` | add index row for this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_generates_portal_for_marine_domain` | happy path produces portal.md with expected top-level section headers | `domain=marine-engineering` | `wiki/portal.md` exists; contains `## By page type`, `## By tag`, `## By standard`, `## Top entries` |
| `test_skips_small_domain_without_force` | small domain (engineering, 77-121 pages) is not portalized unless `--force` | `domain=engineering` | stdout says "skipping"; no file written |
| `test_idempotent_regeneration` | second run differs only in `last_generated` YAML field | run twice | diff excluding `last_generated:` is empty |
| `test_ignores_portal_self` | generator does not treat portal.md as an input page | portal.md present | no self-entry in any facet |
| `test_top_entries_ranked_by_inbound_links` | inbound-link ranking is correct on a fixture | fixture with known `[[page]]` graph | ordered list matches expected |
| `test_frontmatter_tag_facet_respects_top_n` | `--top-tags N` limits tag facet size | fixture with 20 tags | at most N tag groups emitted |
| `test_corrupt_frontmatter_does_not_abort` | one bad page logs warning and is skipped | fixture with invalid YAML | generator exits 0; warning logged |
| `test_portal_link_not_duplicated_in_index` | re-running the linker twice on `wiki/index.md` does not double-insert the portal link | modified index.md | exactly one "Curated portal" link |

All tests run via `uv run pytest scripts/knowledge/tests/test_generate_wiki_portal.py -v`.

---

## Acceptance Criteria

- [ ] `scripts/knowledge/generate_wiki_portal.py` exists and is invoked as `uv run scripts/knowledge/generate_wiki_portal.py <domain>`
- [ ] All tests pass: `uv run pytest scripts/knowledge/tests/test_generate_wiki_portal.py -v`
- [ ] No regression: `uv run pytest scripts/knowledge/tests/ -v` (full knowledge-scripts suite) passes
- [ ] `knowledge/wikis/marine-engineering/wiki/portal.md` exists with the four facet sections
- [ ] `knowledge/wikis/marine-engineering/wiki/index.md` links to the portal in a single "Curated portal" line near the top
- [ ] `docs/document-intelligence/README.md` shows a portal link for marine-engineering
- [ ] `docs/document-intelligence/llm-wiki-portal-design.md` contains the **extend-vs-create** rule, default threshold, and regeneration contract
- [ ] Generated portal does NOT replace `wiki/index.md` — `index.md` remains the canonical contents table
- [ ] Idempotency test passes (same inputs → same output modulo `last_generated`)
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | — |
| Codex | PENDING | — |
| Gemini | PENDING | — |

**Overall result:** PENDING (r1 cross-review will be dispatched immediately after this file is pushed)

---

## Risks and Open Questions

- **Risk:** 19,161 `sources/` pages may produce an unwieldy "By page type" group. Mitigation: `sources/` will be summarized as a single aggregate row with a count, not enumerated.
- **Risk:** Frontmatter parser resilience — wiki pages may have malformed YAML. Mitigation: `test_corrupt_frontmatter_does_not_abort`; generator must log and continue.
- **Risk:** Threshold choice (proposed 500 pages) is a design knob. If set wrong, small domains get unnecessary portals or marine-engineering is the only beneficiary forever. Mitigation: threshold is CLI-configurable; design doc documents the 500-page default and rationale.
- **Risk:** Committing the generated portal creates a regenerate-drift risk. Mitigation: post-closeout CI check (out of scope for this issue — tracked as follow-up) to ensure committed portal matches re-generated output at HEAD.
- **Open:** Should the portal be auto-regenerated nightly via `config/scheduled-tasks/schedule-tasks.yaml`? Deferred: initial issue is analysis-producing; cadence decision left to a follow-up after the first portal lands.
- **Open:** Should the design doc formally define "large domain" (proposal: page_count ≥ 500 OR wiki/index.md line count ≥ 2000)? Flag for user during approval.

---

## Complexity: T2

New module + tests + one generated artifact + two navigation-surface edits + one design doc. Not architectural (no schema changes; reads existing frontmatter only). TDD required because the output is committed and must be deterministic.
