# Marine Subdomain Taxonomy — Final Classification Report

> **Issue:** #1653
> **Date:** 2026-04-05
> **Classifier:** V2 — keyword + standard number mapping + folder hints

## Executive Summary

The marine corpus contains **217,117 documents**. Of these:

| Category | Count | % | Action |
|---|---|---|---|
| **CAD Drawings (DWG/DXF)** | 195,687 | **90.1%** | Separate CAD metadata pipeline needed |
| **Classified by V2** | 10,900 | **5.0%** | Tagged with subdomain |
| **Standards needing content scan** | 10,530 | **4.8%** | DNV/OnePetro docs — need PDF text extraction |
| **Total** | 217,117 | 100.0% | |

**The "33% unclassified" figure from the original issue was measured against a 32K marine subset and included CAD drawings in the unclassified count. The actual text-based classification challenge is smaller: ~10K out of ~21K non-CAD docs (48%).**

## Subdomain Distribution (V2 classified docs only)

| Subdomain | Count | % of classified |
|---|---|---|
| Hydrodynamics | 2,221 | 20.4% |
| Risers & Umbilicals | 1,800 | 16.5% |
| Subsea & Pipelines | 1,620 | 14.9% |
| Vessels & Floaters | 1,132 | 10.4% |
| Marine Operations | 1,081 | 9.9% |
| Mooring | 1,077 | 9.9% |
| Other | 848 | 7.8% |
| Installation | 401 | 3.7% |
| VIV & Fatigue | 350 | 3.2% |

## Why 10,530 Remain Unclassified

These fall into 3 categories:

**A. DNV/Classification Standards (~6K)**
- Filenames like `DNV_OS_304_Risk_Based_Verification_of_Offshore_Structures.pdf`
- These are comprehensive classification rules that cover MULTIPLE domains
- Cannot be cleanly assigned to one subdomain without reading content
- Example: DNV OS J101 (Design of offshore wind turbines) touches structural, hydrodynamics, vessels

**B. Conference Papers with OTC Numbers (~3K)**
- Filenames like `OTC-7325-MS.pdf`, `OTC-25992-MS.pdf`
- No topic information in the filename
- Need PDF title/abstract extraction to classify

**C. Generic/Administrative (~1.5K)**
- Quality manuals, guidelines, wave energy reports, general technical notes
- Some genuinely belong in "other" marine category
- Some are not engineering documents at all

## Classifier Details

**Script:** `scripts/data/classify_marine_v2.py`

**Method:** Three-tier classification:
1. **Standard number mapping** — 80+ API/DNV/ABS/ISO codes mapped to subdomains
2. **Keyword scoring** — 200+ domain-specific keywords across 9 subdomains
3. **Folder path hints** — project discipline folder as fallback

**Confidence:** Standard number matches get score=10, keyword matches get weighted score by keyword length, folder hints get score=1

## File Locations

| File | Description |
|---|---|
| `scripts/data/classify_marine_v2.py` | V2 classifier script |
| `data/document-index/marine-subdomain-tags.yaml` | Compact taxonomy output |
| `data/document-intelligence/marine-subdomain-taxonomy.md` | Original taxonomy plan |
| `docs/document-intelligence/marine-taxonomy-classification-report.md` | This report |

## Recommendation for Issue Closure

The keyword-based taxonomy classifier is built, tested, and has classified what can be classified from metadata alone. The remaining 10K docs require PDF content reading (title/abstract extraction) which is a separate workstream from taxonomy design.

**This issue is closed — taxonomy design is complete. The V2 classifier handles the classification step.** The remaining unclassified docs are flagged for the Phase B summarization pipeline (#1769) to handle as part of content processing.

## What's Next (Dependencies)

1. **Phase B Summarization (#1769):** When summarizing docs, extract subdomain tags from summary text — this will classify the remaining 10K as summaries are generated
2. **Digitalmodel Integration:** Subdomain tags can drive which `digitalmodel` modules get enriched from which documents
3. **CAD Pipeline (separate):** 195K DWG/DXF files need AutoCAD metadata extraction to classify
