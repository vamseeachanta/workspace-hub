# Issue #2637: engineering classification-society entity pages

> **Status:** plan-review
> **Date:** 2026-05-04
> **Complexity:** T2 — bounded wiki backfill
> **Review artifacts:** `scripts/review/results/2026-05-04-plan-2637-claude.md`, `scripts/review/results/2026-05-04-plan-2637-gemini.md`

## Problem Statement
Issue #2637 will backfill missing engineering wiki entity pages for DNV, ABS, Lloyd’s Register, and Bureau Veritas. This is entity backfill only, not standards extraction.

- `/mnt/ace` raw corpora will remain outside git; approved implementation will promote only curated summaries, metadata, cross-links, and provenance fields.
- No plan will self-approve, create approval markers, or move an issue to `status:plan-approved`; this plan will stop at `status:plan-review` for user approval.
- Codex adversarial review remains unavailable due #2479 unless verified fixed; this plan will not block solely on Codex.

## Resource Intelligence Summary
| Source | Evidence | Impact |
|---|---|---|
| Engineering wiki gap audit | Table C item 8 names DNV/ABS/LR/BV as missing classification-society entities | Defines non-duplicate scope. |
| `knowledge/wikis/engineering/CLAUDE.md` | Required frontmatter: `title`, `tags`, `added`, `last_updated` | TDD follows actual schema. |
| Public org pages | `dnv.com`, `eagle.org`, `lr.org`, `bureauveritas.com` | Pages will use authoritative public organization grounding. |
| #2590/#2594 | Adjacent standards lanes | Entity pages will not summarize standards content. |

## Scope
### In Scope
- Create `dnv.md`, `abs.md`, `lr.md`, `bv.md` under `knowledge/wikis/engineering/wiki/entities/`.
- Add public source links and short organization identity/role/scope summaries.
- Update `knowledge/wikis/engineering/wiki/index.md` minimally and append `knowledge/wikis/engineering/wiki/log.md`.

### Out of Scope
- Standards summaries/rules.
- `/mnt/ace` paths, raw standards/client text, or raw corpus identifiers.

## TDD Contract
```python
def test_schema(page):
    assert frontmatter_has(page, ["title", "tags", "added", "last_updated"])

def test_entity_not_standard_summary(page):
    assert describes_org_identity_role_and_engineering_relevance(page)
    assert "/mnt/ace" not in page.text
    assert not contains_raw_standard_clause_extracts(page)
```

## Files to Change
| Action | Path | Purpose |
|---|---|---|
| Create | `knowledge/wikis/engineering/wiki/entities/dnv.md` | DNV entity page |
| Create | `knowledge/wikis/engineering/wiki/entities/abs.md` | ABS entity page |
| Create | `knowledge/wikis/engineering/wiki/entities/lr.md` | Lloyd’s Register entity page |
| Create | `knowledge/wikis/engineering/wiki/entities/bv.md` | Bureau Veritas entity page |
| Update | `knowledge/wikis/engineering/wiki/index.md` | Minimal link/index update |
| Update | `knowledge/wikis/engineering/wiki/log.md` | Change-log entry |

## Acceptance Criteria
- [ ] All four entity pages will exist with canonical engineering wiki frontmatter.
- [ ] Each page will cite public authoritative organization sources.
- [ ] Pages will describe organization identity/role/scope only.
- [ ] Pages will not contain `/mnt/ace`, raw corpus identifiers, or verbatim raw standards/client text.

## Adversarial Review Summary
| Reviewer | Verdict | Notes |
|---|---|---|
| Claude internal | MAJOR → RESOLVED | Schema/source/log/raw-boundary findings resolved; artifact: `scripts/review/results/2026-05-04-plan-2637-claude.md`. |
| Gemini | UNAVAILABLE_NOT_BLOCKING | Rerun path in `scripts/review/results/2026-05-04-plan-2637-gemini.md`. |
| Codex | UNAVAILABLE | Codex remains unavailable due #2479. |

**Overall result:** APPROVAL-READY FOR USER REVIEW; stop at `status:plan-review`.
