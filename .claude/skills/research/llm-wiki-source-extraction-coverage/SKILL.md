---
name: llm-wiki-source-extraction-coverage
description: >-
  Doc-type-aware extraction contract for llm-wiki source ingestion with
  measurable coverage and source-anchored traceability. Use when (1) ingesting
  a PDF, DOCX, XLSX, PPTX, HTML, or scanned-image source into a wiki
  `sources/` page, (2) computing the pre-extraction estimate (what fraction of
  the source we expect to recover) and post-extraction yield (what fraction we
  actually recovered), (3) anchoring wiki claims back to specific page /
  paragraph / cell / slide positions in the source so a reviewer can re-verify
  or revise against the actual document, (4) deciding whether OCR fallback or
  manual transcription is needed. Codifies workspace-hub's existing OCR
  fallback chain and python-docx / openpyxl / trafilatura patterns into a
  format-specific routing table. Companion to research/llm-wiki-page-shape-contract
  (Rule 7 input-layer pages) and research/llm-wiki — this skill is the
  defense against silent extraction failure.
metadata:
  category: research
  related_skills:
    - research/llm-wiki
    - research/llm-wiki-page-shape-contract
    - research/llm-wiki-audit-feedback-loop
    - engineering/doc-extraction
    - productivity/ocr-and-documents
    - data/document-index-pipeline
  related_issues:
    - vamseeachanta/workspace-hub#2374
    - vamseeachanta/workspace-hub#2727
  references:
    - references/pdf-extraction.md
    - references/docx-extraction.md
    - references/xlsx-extraction.md
    - references/html-extraction.md
    - references/scanned-pdf-ocr-fallback.md
---

# llm-wiki source extraction coverage

Silent extraction failure is the highest-frequency wiki defect today. When
`pdftotext` returns 0 chars on an image-PDF, when `python-docx` skips
embedded objects, when `openpyxl` ignores hidden sheets — the resulting
wiki page looks complete but isn't. This skill closes the gap with two
measurements per extraction and an anchor format for every wiki claim
back to the source.

The pattern: **predict coverage, measure coverage, inventory the gap, anchor every claim.**

---

## When this skill applies

| Trigger | Action |
|---|---|
| Ingesting PDF / DOCX / XLSX / PPTX / HTML / image-only source via `llm_wiki.py ingest` | **APPLY** — pre + post extraction metrics required |
| Re-ingesting a source whose previous yield was < 1.0 | **APPLY** — record the upgrade attempt |
| Plain-text Markdown source (no binary processing) | Skip extraction metrics; yield = 1.0 implicit |
| Web page already in clean HTML | Light-touch; record `extraction_yield` only if non-trivial processing applied |
| LinkedIn post / blog post via WebFetch | Skip extraction metrics; the conversion is the WebFetch model's job per `feedback_webfetch_first_for_linkedin` |
| Hand-typed notes captured as markdown | Skip; yield = 1.0 |

---

## The two metrics

### `extraction_estimate` (pre-extraction)

Predicted upper-bound of what we expect to recover, **before** running the
extractor. Computed from cheap structural inspection of the source.

Frontmatter field on the resulting `sources/<slug>.md` page:

```yaml
extraction_estimate: 0.80
extraction_estimate_rationale: |
  PDF has 100 pages: 80 text-based (`pdffonts` shows embedded fonts), 20
  image-only (no embedded fonts, pixel-density consistent with scan). OCR
  fallback could lift toward 0.95 but baseline text-only is 0.80.
```

Range: `0.0` to `1.0`. A `0.0` estimate means "this source is unreadable
by current tooling without manual transcription".

### `extraction_yield` (post-extraction)

Actual measured fraction recovered, **after** running the extractor and
inspecting output.

```yaml
extraction_yield: 0.94
extraction_yield_method: pdftotext+OCR  # how it was measured
extraction_yield_lost: |
  Page 47 OCR garbled — table 4-2 numeric values unreadable.
  Page 73 figure caption truncated mid-sentence.
  Pages 91-95 dense math, KaTeX transcription deferred.
```

Range: `0.0` to `1.0`. **If `yield < estimate`, the lost-content
inventory is required** — a bullet list of what was lost.

### Measurement protocol per format

See format-specific references for exact commands. Common shape:

1. Count addressable units (pages / paragraphs / cells / slides)
2. Run extractor; count units with usable output
3. `yield = units_recovered / units_total`
4. Spot-check 5–10 random units against the source visually
5. List units that failed the spot-check in `extraction_yield_lost`

---

## Format-specific routing

| Format | Primary extractor | Fallback chain | Anchor format | Reference |
|---|---|---|---|---|
| PDF (text-based) | `pdftotext -layout` | `PyMuPDF` (`fitz`) → manual | `<slug>:p<page>:¶<paragraph>` | `references/pdf-extraction.md` |
| PDF (scanned image) | `PyMuPDF` render @ 300 DPI → `tesseract --psm 6` | manual transcription | `<slug>:p<page>:OCR` | `references/scanned-pdf-ocr-fallback.md` |
| DOCX | `python-docx` | `pandoc -f docx -t markdown` | `<slug>:¶<paragraph-id>` | `references/docx-extraction.md` |
| XLSX | `openpyxl` (visible cells) | `pandas.read_excel` (per sheet) | `<slug>:<sheet>!<cell>` | `references/xlsx-extraction.md` |
| PPTX | `python-pptx` | `pandoc -f pptx -t markdown` | `<slug>:slide<N>` | (extend `docx-extraction.md`) |
| HTML | `trafilatura` | `BeautifulSoup` + `readability-lxml` | `<slug>#<heading-slug>` | `references/html-extraction.md` |
| Plain text / Markdown | `cat` (yield = 1.0) | n/a | `<slug>:¶<paragraph>` | n/a |
| Image (PNG / JPG) | `tesseract --psm 6` | manual transcription | `<slug>:OCR` | (extend `scanned-pdf-ocr-fallback.md`) |

Existing implementation references:

- `feedback_pdf_ocr_fallback_chain` codifies the pdftotext → PyMuPDF → tesseract chain
- `productivity/ocr-and-documents` is the existing OCR skill (this skill cites, does not duplicate)
- `engineering/doc-extraction` is the engineering-specific extraction skill (used for technical PDFs)
- `data/document-index-pipeline` is the upstream ingestion pipeline that calls this skill

---

## Source-anchor traceability

Every claim on a compiled wiki page (`concepts/`, `standards/`,
`methodology/`) that derives from an extracted source must cite a
**precise location** in the source. This is the revisability contract:
a future reviewer can locate the original passage and verify or revise.

### Anchor formats by source type

| Source type | Anchor format | Example |
|---|---|---|
| PDF | `[[sources/<slug>]] :p<page>:¶<para-index>` | `[[sources/dnv-os-e301-2023]]:p47:¶2` |
| PDF OCR | `[[sources/<slug>]] :p<page>:OCR` (note: lower confidence) | `[[sources/api-rp-2sk-2008]]:p23:OCR` |
| DOCX | `[[sources/<slug>]] :¶<paragraph-id>` | `[[sources/project-basis-of-design]]:¶47` |
| XLSX | `[[sources/<slug>]] :<sheet>!<cell-range>` | `[[sources/mooring-results-export]]:Lines!C12:F12` |
| PPTX | `[[sources/<slug>]] :slide<N>:<element>` | `[[sources/conference-2024-paper]]:slide12:figure` |
| HTML | `[[sources/<slug>]] #<heading-slug>` | `[[sources/blog-post-yaw-moments]]#stability-analysis` |
| Plain text | `[[sources/<slug>]] :¶<paragraph>` | `[[sources/handoff-2026-05-20]]:¶3` |

### Anchor placement in compiled pages

In a `concepts/` or `standards/` page, anchors go at the **end of the
sentence** they support, in parentheses:

```markdown
The DNV-OS-E301 safety factor for ULS mooring conditions is **1.5**
([[sources/dnv-os-e301-2023]]:p47:¶2), reduced from the 2018 edition's
1.67 ([[sources/dnv-os-e301-2018]]:p41:¶3).
```

Multiple-source claims chain anchors:

```markdown
Empirical yield in deepwater mooring failures clusters around 14% of
nameplate MBL ([[sources/sintef-2019-mooring-survey]]:p12:Table-3;
[[sources/api-bulletin-2tl]]:p8:¶4).
```

### Anti-patterns

- Citing `[[sources/<slug>]]` without a sub-anchor → reviewer can't locate
- Anchor pointing at a page that lacks the claim (cut-and-paste error)
- Anchor in a section the extraction yield report flagged as lost
- Using anchor format for one source type on another (e.g., `:p47` on a DOCX)

---

## Pre-extraction protocol

Run **before** copying the binary into `wikis/<domain>/sources/`.

```bash
# 1. Identify format
file <source-path>

# 2. Cheap structural inspection (format-specific):
# PDF
pdfinfo <source-path>                            # pages, encrypted, etc.
pdffonts <source-path> | head                    # text-based vs scanned
# DOCX
unzip -l <source-path> | head                    # embedded objects, images
# XLSX
unzip -l <source-path> | grep sheet              # sheet count

# 3. Compute extraction_estimate (see format references for exact heuristics)
# 4. Record estimate in the source page frontmatter BEFORE extraction
```

For binaries >10 MB, do **not** copy into the wiki — create a ref pointer
per `llm-wiki-page-shape-contract` Rule 3:

```yaml
---
title: refs/<slug>
type: ref
external_path: /mnt/ace/<repo>/data/<file>.pdf
size: ~140 MB
extraction_estimate: 0.80                  # set even on ref pages
extraction_yield: null                      # filled in after compiled pages cite this ref
---
```

---

## Post-extraction protocol

After running the extractor:

1. **Measure**: count addressable units recovered vs total (see format
   references for exact commands).
2. **Spot-check**: 5–10 random samples against the source. Visual or
   programmatic comparison.
3. **Inventory loss**: list every unit that didn't extract cleanly with
   page/paragraph/cell anchor + one-line reason.
4. **Decide**: is the yield enough to proceed?
   - Yield ≥ 0.90 AND no critical content lost → proceed to compile
   - Yield 0.50–0.90 → proceed but file an audit per
     `research/llm-wiki-audit-feedback-loop` with the loss inventory,
     so future passes know what to revisit
   - Yield < 0.50 → defer ingest; the source is not extractable enough
     to be useful. Note this in `wikis/<domain>/CLAUDE.md` "Open research
     questions" with the path and the failed yield.
5. **Write frontmatter**: `extraction_yield`, `extraction_yield_method`,
   `extraction_yield_lost` go on the `sources/<slug>.md` page.

---

## Frontmatter required on `sources/<slug>.md`

```yaml
---
title: sources/<slug>
type: source                                       # input layer per page-shape Rule 7
source_format: pdf | docx | xlsx | pptx | html | image | text
source_url: https://...                            # if applicable
source_path: /path/to/local/copy.pdf               # if binary copied in
external_path: /mnt/ace/<repo>/<file>              # if ref pointer (>10 MB)
date: YYYY-MM-DD                                   # original publication
ingested: YYYY-MM-DD                               # when extracted into wiki

# Extraction coverage (this skill's required fields)
extraction_estimate: 0.80
extraction_estimate_rationale: |
  <one-paragraph reason — what's recoverable, what isn't, why>
extraction_yield: 0.94
extraction_yield_method: pdftotext+OCR
extraction_yield_lost: |
  - Page 47: OCR garbled, table 4-2 numerics unreadable
  - Page 73: figure caption truncated mid-sentence
  - Pages 91–95: dense KaTeX, transcription deferred

# Wiki-shape contract fields
sources: []                                        # this IS a source; empty for source pages
tags: [<tag>]
license: <license-shorthand>
---
```

---

## Decision tree per source

```
new source arrives
  │
  ├── plain text / Markdown ─────► yield = 1.0, no anchors needed beyond ¶
  │
  ├── HTML (clean) ──────────────► trafilatura; anchor by heading
  │
  ├── HTML (messy) ──────────────► trafilatura → BeautifulSoup fallback
  │
  ├── PDF
  │     ├── text-based ──────────► pdftotext -layout; anchor :p<page>:¶
  │     ├── mixed ───────────────► pdftotext + PyMuPDF where pdftotext = 0 chars
  │     └── scanned ─────────────► PyMuPDF render 300 DPI → tesseract --psm 6
  │
  ├── DOCX ──────────────────────► python-docx; fallback pandoc; anchor by ¶ id
  │
  ├── XLSX ──────────────────────► openpyxl per visible cell; anchor :<sheet>!<cell>
  │
  ├── PPTX ──────────────────────► python-pptx; anchor :slide<N>
  │
  └── image ─────────────────────► tesseract --psm 6; anchor :OCR
```

At every leaf: compute estimate before, yield after, write the inventory
if yield < estimate, record anchor format for downstream cites.

---

## Anti-patterns

- Writing a compiled page from a source whose `extraction_yield` was
  never recorded — invisible failure surface
- Yield = 1.0 claimed without spot-checking — overclaim
- Yield < 0.50 ingested anyway — pollutes the corpus
- Citing extracted content from a page whose lost-content inventory
  flagged that exact page → use the audit-feedback-loop to revise
- Reusing one source's anchor format on a different format (`:p47` on a
  DOCX makes no sense)
- Storing the binary in the wiki when it's >10 MB instead of using a ref
  pointer per `llm-wiki-page-shape-contract` Rule 3
- Re-extracting a source repeatedly without recording the attempted yield
  upgrades — wastes compute, loses learning

---

## What this skill is NOT

- Not a replacement for `productivity/ocr-and-documents` — that skill owns
  the OCR tooling specifics; this skill calls into it
- Not a replacement for `engineering/doc-extraction` — that's the
  engineering-domain extraction skill; this skill is the wiki-side contract
  for *recording* extraction quality
- Not a full RAG-replacement extractor — the extractor is the tool; this
  skill is the measurement and anchor contract
- Not for sources that are already plain text or clean HTML — those don't
  need pre/post metrics

## Related must-fire rules

- `feedback_pdf_ocr_fallback_chain` — pdftotext+PyMuPDF=0 chars → image-PDF; fall back PyMuPDF 300 DPI → tesseract --psm 6
- `feedback_runtime_base64_blocks_binary_roundtrip` — JS tool results blocked binary; download path or save_to_disk for binary capture
- `feedback_naive_secret_scan_false_positive_cascade` — extracted content can contain false-positive regex matches; trust the hardened pre-commit hook
- `feedback_subagent_write_phantom` — if a subagent runs the extractor, main session must verify `sources/<slug>.md` actually landed on disk
- `feedback_silent_verdict_flip_defect_class` — extracted standards pages need section+edition, not just code_id
