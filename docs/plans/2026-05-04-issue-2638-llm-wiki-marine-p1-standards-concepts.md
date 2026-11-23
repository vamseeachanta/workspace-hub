# Issue #2638: marine-engineering P1 standards/concepts backfill

> **Status:** plan-review
> **Date:** 2026-05-04
> **Complexity:** T2 — bounded wiki backfill
> **Review artifacts:** `scripts/review/results/2026-05-04-plan-2638-claude.md`, `scripts/review/results/2026-05-04-plan-2638-gemini.md`

## Problem Statement
Issue #2638 will execute W4-C marine P1 items: standards directory/template plus `motions-rao`, `station-keeping`, `dynamic-positioning`, and `spread-mooring` concept pages. It will preserve source stubs and avoid #2378/#2630 scope.

- `/mnt/ace` raw corpora will remain outside git; approved implementation will promote only curated summaries, metadata, cross-links, and provenance fields.
- No plan will self-approve, create approval markers, or move an issue to `status:plan-approved`; this plan will stop at `status:plan-review` for user approval.
- Codex adversarial review remains unavailable due #2479 unless verified fixed; this plan will not block solely on Codex.

## Resource Intelligence Summary
| Source | Evidence | Impact |
|---|---|---|
| Marine W4-C audit | Table G P1 identifies target standards/concept pages | Defines scope. |
| `knowledge/wikis/marine-engineering/CLAUDE.md` | `title`, `tags`, `added`, `last_updated`; `cross_links` optional; no required `summary` frontmatter | TDD follows current schema. |
| `docs/governance/llm-wiki-to-gtm-boundary.md` and #2205/#2207/#2209 references | Wiki promotion boundaries | Prevent raw/source promotion. |
| #2378/#2630 | Chunking/cross-link lanes | Index updates will be minimal listing only. |

## Scope
### In Scope
- Create `wiki/standards/TEMPLATE.md` summary/provenance-only template.
- Create four P1 concept pages.
- Optional minimal `wiki/index.md` listing update.

### Out of Scope
- Modifying `wiki/sources/`.
- #2378 chunking/pagination or #2630 cross-link regeneration.
- Standards text, `/mnt/ace` raw paths, source-stub bulk content, or client/project data.

## TDD Contract
```python
def test_marine_concept_schema(page):
    assert frontmatter_has(page, ["title", "tags", "added", "last_updated"])

def test_no_source_stub_mutation(diff):
    assert not any(p.startswith("knowledge/wikis/marine-engineering/wiki/sources/") for p in diff.modified_or_created)

def test_no_raw_copy(page):
    assert "/mnt/ace" not in page.text
    assert not contains_verbatim_raw_or_standard_clause_extracts(page.text)
```

## Files to Change
| Action | Path | Purpose |
|---|---|---|
| Create | `knowledge/wikis/marine-engineering/wiki/standards/TEMPLATE.md` | Summary/provenance-only standards-page template |
| Create | `knowledge/wikis/marine-engineering/wiki/concepts/motions-rao.md` | P1 motions/RAO concept page |
| Create | `knowledge/wikis/marine-engineering/wiki/concepts/station-keeping.md` | P1 station-keeping page |
| Create | `knowledge/wikis/marine-engineering/wiki/concepts/dynamic-positioning.md` | P1 DP page |
| Create | `knowledge/wikis/marine-engineering/wiki/concepts/spread-mooring.md` | P1 spread-mooring page |
| Optional update | `knowledge/wikis/marine-engineering/wiki/index.md` | Minimal listing only |

## Acceptance Criteria
- [ ] Standards template will state summary/provenance-only expectations.
- [ ] Concept pages will use current marine wiki frontmatter conventions.
- [ ] No `wiki/sources/` files will be created or modified.
- [ ] No `/mnt/ace`, raw-corpus identifiers, or verbatim raw standards/client text will appear.
- [ ] Any index update will not re-open #2378/#2630 work.

## Adversarial Review Summary
| Reviewer | Verdict | Notes |
|---|---|---|
| Claude internal | MAJOR → RESOLVED | Schema/governance/source-boundary/index findings resolved; artifact: `scripts/review/results/2026-05-04-plan-2638-claude.md`. |
| Gemini | UNAVAILABLE_NOT_BLOCKING | Rerun path in `scripts/review/results/2026-05-04-plan-2638-gemini.md`. |
| Codex | UNAVAILABLE | Codex remains unavailable due #2479. |

**Overall result:** APPROVAL-READY FOR USER REVIEW; stop at `status:plan-review`.
