---
name: doc-extraction-yield-reality-wrk-1246-corpus-assessment
description: 'Sub-skill of doc-extraction: Yield Reality (WRK-1246 Corpus Assessment).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Yield Reality (WRK-1246 Corpus Assessment)

## Yield Reality (WRK-1246 Corpus Assessment)


WRK-1246 assessed deep extraction yield across 420K+ text-extractable documents.
Only two content types have proven extraction yield from the current parsers:

| Content type | Yield | Status |
|-------------|-------|--------|
| tables | 69-93% | **Production-ready** — primary extraction target |
| figure_refs | 1-52% | **Partial** — metadata only, varies by stratum |
| equations | 0% | Not yet implemented — parsers do not reliably detect |
| constants | 0% | Not yet implemented — parsers do not reliably detect |
| procedures | 0% | Not yet implemented — parsers do not reliably detect |
| worked_examples | 0% | Not yet implemented — parsers do not reliably detect |

These content types are NOT currently extractable from the corpus — they exist in the
manifest schema (documented below) but the parsers do not reliably detect them. The
schema is retained for future parser development.
