# Issue #2639: marine-engineering P2 entities/overview backfill

> **Status:** plan-review
> **Date:** 2026-05-04
> **Complexity:** T2 — bounded wiki backfill
> **Review artifacts:** `scripts/review/results/2026-05-04-plan-2639-claude.md`, `scripts/review/results/2026-05-04-plan-2639-gemini.md`

## Problem Statement
Issue #2639 will intentionally bundle W4-C Table G P2 items 4–6: `stability-in-waves`, core offshore platform entity pages, and live-count regeneration for `overview.md`. The batch will not touch raw/source-stub provenance or project-specific corpora such as SESA, Woodfibre, ACMA, or Doris.

- `/mnt/ace` raw corpora will remain outside git; approved implementation will promote only curated summaries, metadata, cross-links, and provenance fields.
- No plan will self-approve, create approval markers, or move an issue to `status:plan-approved`; this plan will stop at `status:plan-review` for user approval.
- Codex adversarial review remains unavailable due #2479 unless verified fixed; this plan will not block solely on Codex.

## Resource Intelligence Summary
| Source | Evidence | Impact |
|---|---|---|
| Marine W4-C audit | Table G items 4–6 identify stability-in-waves, platform entities, and stale overview refresh | Defines bundled P2 scope. |
| `overview.md` | Existing counts are stale | Overview will re-derive live counts at execution time. |
| Issue #2630 | Dedicated cross-link regeneration lane | This batch will defer cross-link regeneration. |
| Issue #2638 | P1 may land before/after this issue | Overview counts must be race-tolerant. |

## Scope
### In Scope
- Create `concepts/stability-in-waves.md`.
- Create `fpso.md`, `flng.md`, `semisubmersible.md`, `spar.md`, `jack-up.md`, `tlp.md`, `jacket.md`.
- Refresh `overview.md` from live tree counts.

### Out of Scope
- Copying `/mnt/ace` raw data or source-stub bodies.
- Project-specific facts from SESA, Woodfibre, ACMA/31522, Doris, or similar internal corpora.
- #2630 cross-link regeneration.
- Editing `wiki/sources/` or #2638 deliverables except to count already-landed files.

## TDD Contract
```python
RESERVED_PROJECT_TERMS = ["SESA", "Woodfibre", "ACMA", "31522", "Doris", "Doris University"]

def test_no_project_or_raw_leakage(page):
    assert "/mnt/ace" not in page.text
    assert not any(term in page.text for term in RESERVED_PROJECT_TERMS)
    assert not contains_verbatim_source_stub_or_raw_text(page.text)

def test_overview_uses_live_counts(repo_tree):
    counts = count_current_wiki_tree(repo_tree)
    assert overview_mentions_counts(counts)
    assert not overview_contains_stale_literal("5 concept pages / 8 entity pages / 7 standards pages / 20 source pages")
```

## Files to Change
| Action | Path | Purpose |
|---|---|---|
| Create | `knowledge/wikis/marine-engineering/wiki/concepts/stability-in-waves.md` | P2 stability concept page |
| Create | `knowledge/wikis/marine-engineering/wiki/entities/fpso.md` | FPSO entity page |
| Create | `knowledge/wikis/marine-engineering/wiki/entities/flng.md` | FLNG entity page |
| Create | `knowledge/wikis/marine-engineering/wiki/entities/semisubmersible.md` | Semisubmersible entity page |
| Create | `knowledge/wikis/marine-engineering/wiki/entities/spar.md` | Spar entity page |
| Create | `knowledge/wikis/marine-engineering/wiki/entities/jack-up.md` | Jack-up entity page |
| Create | `knowledge/wikis/marine-engineering/wiki/entities/tlp.md` | TLP entity page |
| Create | `knowledge/wikis/marine-engineering/wiki/entities/jacket.md` | Jacket entity page |
| Modify | `knowledge/wikis/marine-engineering/wiki/overview.md` | Live-count overview refresh |

## Acceptance Criteria
- [ ] Plan will explicitly cover W4-C Table G P2 items 4–6.
- [ ] P2 pages will use current marine wiki schema and high-level summaries only.
- [ ] New pages will not contain `/mnt/ace`, SESA, Woodfibre, ACMA/31522, Doris, or verbatim source-stub/raw text.
- [ ] `overview.md` will be regenerated from live tree counts and will be race-tolerant with #2638.
- [ ] Cross-link regeneration will remain in #2630 or a separately approved follow-up.

## Adversarial Review Summary
| Reviewer | Verdict | Notes |
|---|---|---|
| Claude internal | MAJOR → RESOLVED | Scope/project-leakage/overview-race/#2630 findings resolved; artifact: `scripts/review/results/2026-05-04-plan-2639-claude.md`. |
| Gemini | UNAVAILABLE_NOT_BLOCKING | Rerun path in `scripts/review/results/2026-05-04-plan-2639-gemini.md`. |
| Codex | UNAVAILABLE | Codex remains unavailable due #2479. |

**Overall result:** APPROVAL-READY FOR USER REVIEW; stop at `status:plan-review`.
