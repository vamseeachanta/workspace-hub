---
session: gemini-overnight-batch-20260406
date: 2026-04-06
model: claude-opus-4-6
status: complete
---

# Gemini Overnight Batch — Session Exit Report

## What Was Done

### Session 1: Gemini Backlog Cleanup (33 issues)
**Duration:** ~2 hours, 90 tool calls
**Result:** ALL 33 `agent:gemini` issues closed (100%)

Key deliverables:
- **Conference indexing** (#1608): 27,735 files across 30 collections cataloged → conference-index.jsonl
- **Standards processing** (#1651): 424/425 standards → done (99.8%) across 10 domains
- **Research literature** (#1623): 174 files across 12 domains indexed (747 MB)
- **Engineering-refs catalog** (#1616): 53 files cataloged (124 MB)
- **tesseract-ocr installed** + OCR validated (2 conference PDFs, ~25s each, clean output)
- **XLSX stress test** (#1644): 2/3 files pass, <116MB memory
- **va-hdd-2 triage** (#1774): No engineering content (vocab audio + personal certs)
- **Schema bug fixed**: DocumentManifest missing version/tool/domain args in pdf.py line 122
- **9 follow-up issues created**: #1954-#1962

Commits: 5 pushed (9751d4fb, 45002bf9, eb4f1688, 7cf2d6d6, 75985abd, c04ef59c)

### Session 2: Session Continuation
- Updated gemini-batch-execution skill with overnight learnings
- Verified conference registry (27,735 files, 30 collections)
- Confirmed all 9 follow-up issues exist

## Critical Pitfalls Discovered

### 1. `uv run` suppresses ALL stdout
Scripts run via `uv run python script.py` produce NO stdout output in the terminal sandbox. Print statements vanish completely. This caused 2+ hours of debugging a "silent" script.

**Workaround:** Write to log files and use `read_file` to check progress.
```python
with open("/tmp/log.txt", "a") as f: f.write(f"Progress: {i}/{total}\n")
```
Then: `read_file("/tmp/log.txt")`

### 2. Process isolation matters
Long-running scripts should use `process(action="wait", background=true)` NOT inline `terminal()` with huge timeout. Background processes with `follow_output=true` work correctly.

### 3. `uv run python` inside `subprocess.run` hangs
Nested `uv run` calls cause hanging. Use direct Python import instead:
```python
from scripts.data.doc_intelligence.orchestrator import extract_document
manifest = extract_document(filepath, domain="conference", output="/tmp/out.yaml", doc_ref=None)
```

## Follow-up Issues Created

| # | Title | Priority | Notes |
|---|-------|----------|-------|
| #1954 | Full text extraction of 27,735 conference files | HIGH | Script at scripts/document-intelligence/batch-extract-conferences.py. 357/479 Phase 1 done. Manifests in /tmp/manifests/ |
| #1955 | Phase B: Summarize 27K conference docs at scale | MED | Depends on #1954 |
| #1956 | Deep scan 3,879 .xls binary workbooks | MED | Needs xlrd install |
| #1957 | DWG/DXF parser implementation | MED | ezdxf + ODA File Converter |
| #1958 | Slim-hole well engineering module | MED | Research done in #1, ready to implement |
| #1959 | OpenTURNS fatigue reliability module | MED | Research done in #187 |
| #1960 | Seakeeping 6-DOF module | MED | RAO-based motion response |
| #1961 | Nightly gemini-batch cron auto-processor | HIGH | #1962 | OpenGeoSys geomechanics module | LOW | Research done in #185 |

## Files of Note

| File | Description |
|------|-------------|
| scripts/document-intelligence/batch-extract-conferences.py | Batch extractor for conference files (calls extract_document directly) |
| data/document-index/conference-index.jsonl | Lightweight catalog of 27,735 conference files |
| data/document-index/conference-registry.yaml | Per-collection metadata |
| docs/gemini-overnight-batch-report-2026-04-06.md | Full session report |
| /tmp/manifests/ | 357 extraction manifests (need to move to repo) |
| /tmp/batch_extract_phase1.log | Phase 1 extraction progress log |
| /tmp/run_phase1.py | Phase 1 runner script (has checkpoint support) |

## What Needs User Attention

1. **Move /tmp/manifests/ to repo** — 357 YAML manifests need to be committed
2. **Resume Phase 1 extraction** — NACE was at 338/436, Subsea Tieback untouched
3. **Phase 2-4** — These are huge (OMAE 10K, OTC 5.7K, ISOPE 4.2K files). Recommend overnight cron runs
4. **DocumentManifest schema fix** — The extract-document.py pipeline now works, needs to run at scale

## Cost Analysis
- Gemini usage: Still low (~0-5% of $20/mo quota). The overnight batch was actually mostly Claude/Codex execution with Gemini-labeled issues.
- Recommendation: For actual Gemini web research tasks, use `h-router-gemini` as documented in the skill.
- The most efficient pattern: use Claude/Codex for code execution, Gemini for research/literature gathering with 1M context.
