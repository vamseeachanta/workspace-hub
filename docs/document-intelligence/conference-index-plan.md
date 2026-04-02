# Conference Collection Indexing Plan (#1608)

**Scope:** 38,526 files across 30 collections, 28 GB total  
**Objective:** Index all conference documents into the document-intelligence pipeline  
**Created:** 2026-04-02  
**Status:** Plan — ready for execution  

---

## 1. Collection Inventory

| # | Collection | Files | Size | Priority | Notes |
|---|-----------|-------|------|----------|-------|
| 1 | OMAE | 13,126 | 8.2 GB | P1 — High | Largest. Core offshore engineering papers |
| 2 | OTC | 8,500 | 7.8 GB | P1 — High | Offshore Technology Conference — high value |
| 3 | DOT | 7,516 | 2.3 GB | P2 — Medium | Deep Offshore Technology |
| 4 | ISOPE | 4,516 | 3.0 GB | P2 — Medium | International ocean & polar engineering |
| 5 | UK Conference Folder | 2,725 | 2.0 GB | P3 — Low | Mixed UK conferences, needs triage |
| 6 | NACE | 561 | 670 MB | P1 — High | Corrosion engineering — targeted domain |
| 7 | Flow Induced Vibration | 229 | 98 MB | P1 — High | Direct riser/VIV relevance |
| 8 | Arctic Technology Conference | 216 | 145 MB | P2 — Medium | Specialized domain |
| 9 | Subsea Tieback | 214 | 799 MB | P1 — High | Subsea engineering |
| 10 | SPE | 129 | 117 MB | P2 — Medium | Society of Petroleum Engineers |
| 11 | Offshore West Africa | 125 | 226 MB | P3 — Low | Regional conference |
| 12 | TOD | 101 | 100 MB | P2 — Medium | Technology of the Deep |
| 13 | SNAME | 99 | 146 MB | P2 — Medium | Naval architecture & marine engineering |
| 14 | Coiled Tubing & Well Intervention | 68 | 112 MB | P3 — Low | Specialized |
| 15 | TO SORT | 67 | 72 MB | P4 — Triage | Needs manual classification first |
| 16 | Rio Oil & Gas | 66 | 32 MB | P3 — Low | Regional conference |
| 17 | DeepGulf | 43 | 113 MB | P2 — Medium | Deepwater focus |
| 18 | ISO 9001 | 37 | 88 MB | P3 — Low | Quality management — tangential |
| 19 | Subsea Survey IMMR | 34 | 1.3 GB | P2 — Medium | Large files (survey data?) |
| 20 | Robert Restore | 24 | 68 MB | P3 — Low | Reference papers |
| 21 | Euroforum Offshore Risers | 23 | 126 MB | P1 — High | Direct riser engineering |
| 22 | Unlocking Deepwater Potential | 20 | 37 MB | P2 — Medium | Mumbai conference |
| 23 | Subsea Houston | 20 | 164 MB | P2 — Medium | Subsea technology |
| 24 | IMarEST Offshore Oil & Gas | 20 | 46 MB | P3 — Low | Marine engineering |
| 25 | EUCI | 20 | 24 MB | P3 — Low | Regulatory focus |
| 26 | IADC International Deepwater | 15 | 20 MB | P2 — Medium | Deepwater drilling |
| 27 | Pipeline Pigging & Integrity | 5 | 67 MB | P2 — Medium | Pipeline integrity |
| 28 | Dry Tree Forum | 5 | 5.3 MB | P1 — High | Direct dry tree riser relevance |
| 29 | SUT | 1 | 3.5 MB | P3 — Low | Society for Underwater Technology |
| 30 | JPT | 1 | 860 KB | P3 — Low | Journal of Petroleum Technology |

---

## 2. File Type Breakdown & Extraction Strategy

| Extension | Count | % of Total | Extraction Strategy |
|-----------|-------|-----------|-------------------|
| .pdf / .PDF | 21,996 | 57.1% | pdfplumber → text/tables. OCR fallback for scanned docs (#1617) |
| .html / .htm | 5,283 | 13.7% | HtmlParser (existing pipeline) |
| .gif | 2,522 | 6.5% | Skip — conference navigation images |
| .cfs | 1,571 | 4.1% | Skip — Lucene compound file segments (search index artifacts) |
| .jpg / .png | 642 | 1.7% | Skip — images (or OCR if engineering drawings) |
| .wmz / .emz | 481 | 1.2% | Skip — Windows metafile compressed images |
| .txt / .TXT | 302 | 0.8% | Plain text extraction (trivial) |
| .dll / .DLL / .exe | 337 | 0.9% | Skip — binary executables (conference CD software) |
| .js / .css / .xml | 262 | 0.7% | Skip — web assets |
| .ppt | 57 | 0.1% | python-pptx (may need conversion from .ppt binary) |
| .doc | 45 | 0.1% | python-docx (may need conversion from .doc binary) |
| Numeric (1-9) | 873 | 2.3% | Skip — Lucene index segments |
| .api / .tvf / .PFB/.pfm/.otf | ~700 | 1.8% | Skip — fonts, API files, term vectors |
| Other | ~3,400 | 8.8% | Case-by-case; default skip |

**Indexable files (PDF + HTML + TXT + PPT + DOC):** ~27,683 (71.9%)  
**Skip files (images, binaries, web assets, index artifacts):** ~10,843 (28.1%)

---

## 3. Execution Approach

### 3.1 Batch Processing Strategy

- **Batch size:** 100 files per batch
- **Parallel workers:** 4 (one per CPU core, disk I/O bound)
- **Estimated throughput:** ~2-5 files/sec for text PDFs, ~0.3 files/sec for OCR
- **Checkpoint:** Save progress after each batch (resumable on failure)

### 3.2 Execution Phases

**Phase 1 — High-Priority Small Collections (P1, <500 files)**  
Collections: Dry Tree Forum, Euroforum Offshore Risers, Flow Induced Vibration,
             NACE, Subsea Tieback  
Files: ~1,032 | Est. size: ~1.8 GB | Est. time: 15-30 minutes  

**Phase 2 — High-Priority Large Collections (P1, >500 files)**  
Collections: OMAE, OTC  
Files: ~21,626 | Est. size: ~16 GB | Est. time: 4-8 hours (PDF-heavy, likely scanned)  

**Phase 3 — Medium-Priority Collections (P2)**  
Collections: DOT, ISOPE, Arctic Technology, SPE, TOD, SNAME, DeepGulf,
             Subsea Survey IMMR, Unlocking Deepwater, Subsea Houston,
             IADC, Pipeline Pigging  
Files: ~12,893 | Est. size: ~8.2 GB | Est. time: 3-6 hours  

**Phase 4 — Low-Priority & Triage (P3, P4)**  
Collections: UK Conference Folder, TO SORT, remaining small collections  
Files: ~2,975 | Est. size: ~2.6 GB | Est. time: 1-2 hours  

### 3.3 Total Estimated Time

| Phase | Files | Est. Time | Cumulative |
|-------|-------|-----------|------------|
| Phase 1 | 1,032 | 15-30 min | 0.5 hr |
| Phase 2 | 21,626 | 4-8 hr | 5-8.5 hr |
| Phase 3 | 12,893 | 3-6 hr | 8-14.5 hr |
| Phase 4 | 2,975 | 1-2 hr | 9-16.5 hr |

**Total: 9-17 hours** (depends heavily on scanned PDF ratio)

---

## 4. Output Format

Each processed file produces a manifest YAML:
```
data/document-index/conferences/<collection>/<filename>.manifest.yaml
```

Manifest format matches existing pipeline (DocumentManifest schema):
- version, tool, domain
- metadata (filename, format, size, pages, checksum)
- sections (heading, level, text, source)
- tables (title, columns, rows, source)
- figure_refs (caption, figure_id, source)
- extraction_stats, errors

### 4.1 Index Registry

After all batches, generate:
```
data/document-index/conference-registry.yaml
```
Containing: file path, collection, year, domain tags, extraction status.

---

## 5. Quality Checks

After each batch:
1. **Completeness:** Verify manifest exists for each processed file
2. **Non-empty:** At least 1 section OR 1 table in each manifest (else flag)
3. **OCR detection:** Count scanned PDFs per collection for reporting
4. **Sample validation:** Manually spot-check 3 manifests per collection
5. **Error rate:** Track and report extraction errors per collection
6. **Duplicate detection:** Hash-based dedup across collections

---

## 6. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Disk space for manifests | Medium | Medium | Est. ~500 MB for 28K manifests. Check df before starting |
| Memory on large scanned PDFs | High | High | OCR with pdf2image at 300dpi can use 500MB+ per page. Limit to 1 OCR worker |
| Old conference CD format (.cfs, Lucene) | Certain | Low | Skip entirely — these are search index artifacts |
| Corrupt/password-protected PDFs | Medium | Low | Graceful error handling already in pipeline |
| Scanned PDFs needing OCR | High | Medium | OMAE/OTC likely 30-50% scanned. Use OCR parser (#1617) |
| Very large files (>50MB) | Low | Medium | XLSX limit raised to 50MB (#1619). PDFs have no hard limit |
| Network mount latency (/mnt/ace) | Medium | Medium | Copy batch to local SSD before processing |
| Encoding issues in filenames | Medium | Low | Use pathlib for safe path handling |

---

## 7. Prerequisites

- [x] OCR parser for scanned PDFs (#1617)
- [x] XLSX formula extraction limit raised to 50MB (#1619)
- [ ] tesseract-ocr installed on execution machine
- [ ] poppler-utils installed (for pdf2image)
- [ ] Sufficient disk space (~500 MB for manifests)
- [ ] /mnt/ace mount accessible from execution environment

---

## 8. Naming Conventions Observed

- **OMAE:** `OMAE{year}-{paper_id}.pdf` or descriptive titles
- **OTC:** `{year}OTC_*.pdf`, `otc-{number}.pdf`
- **DOT:** `ID {number} Abstract.pdf`, varied
- **ISOPE:** `{year}-{code}-{number}.pdf` (e.g., `2004-jwc-01.pdf`)
- **SPE:** `spe{number}.pdf`
- **NACE:** `NACE {number} {TITLE}.pdf`
- **SNAME:** `SNAME_OS{year}_{number}.pdf`

Collections have year-based subdirectories (e.g., `OMAE/OMAE 2002/`, `OTC/OTC2010/`).
Some include conference CD artifacts (help files, navigation HTML, search indexes).

---

## 9. Companion Script

See: `scripts/document-intelligence/index-conferences.sh`  
Stub script with parameterized batch processing loop.
