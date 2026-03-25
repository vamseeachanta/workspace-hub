# WRK-1363: LLM domain-tag riser-eng-job literature for digitalmodel cross-reference

## Goal

Classify ~15,000 PDF/DOC/DOCX files from 4 riser engineering project archives using LLM-based domain tagging, then create cross-reference index mapping each document to one or more digitalmodel domain categories.

## Source

`/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/`

| Project | Size | Literature Files |
|---------|------|-----------------|
| 2100-blk31-slor-design | 53G | 12,362 |
| 3824-containment-riser | 30G | 2,579 |
| 3836-hp1-riser | 7.4G | 167 |
| 3837-cdp2-fsr | 3.7G | 341 |

## Target Domains (digitalmodel)

Primary: `risers`, `riser_analysis`, `viv`, `structural`, `fatigue`, `mooring`
Secondary: `fem`, `catenary`, `connections`, `installation`, `metocean`, `pipe`, `subsea`

## Acceptance Criteria

1. **AC-1**: A classification script exists that takes a document path and returns domain tags
2. **AC-2**: All 15,449 literature files have been classified with at least one domain tag
3. **AC-3**: Classification results stored in a YAML/JSON index at `digitalmodel/docs/domain/subsea-risers/riser-eng-job/domain-index.yaml`
4. **AC-4**: Cross-reference symlinks or index entries created from digitalmodel domain dirs pointing to tagged files
5. **AC-5**: Classification accuracy >= 80% on a 50-file manual sample

## Pseudocode

```
1. SCAN source directory for PDF/DOC/DOCX files → file_list (15k entries)
2. For each file in file_list:
   a. EXTRACT metadata: filename, path, project subfolder, file size
   b. CLASSIFY using filename pattern matching (first pass):
      - Parse project code (2100/3824/3836/3837)
      - Parse document type from naming convention (RPT/TNE/DWG/etc.)
      - Map known prefixes to domains
   c. For ambiguous files, CLASSIFY using LLM:
      - Extract first 2 pages of PDF text (or doc text)
      - Send to Claude API with domain taxonomy prompt
      - Parse response into domain tags
3. AGGREGATE results into domain-index.yaml
4. CREATE cross-reference entries:
   - For each domain in digitalmodel, create index file listing matched documents
5. VALIDATE: sample 50 random files, compare automated vs manual classification
```

## Test Plan

| # | Test | Method |
|---|------|--------|
| T1 | Classification script handles PDF, DOC, DOCX file types | Unit test with sample files |
| T2 | Filename pattern matcher correctly identifies project codes and doc types | Unit test with known filenames |
| T3 | LLM classifier returns valid domain tags from taxonomy | Integration test with 10 sample PDFs |
| T4 | domain-index.yaml schema is valid and contains all files | Schema validation + count check |
| T5 | Cross-reference index entries point to existing files | Path validation script |
| T6 | 50-file manual sample achieves >= 80% accuracy | Manual review |

## Implementation Notes

- Start with filename-based classification (covers ~60-70% of files based on naming conventions)
- Use LLM only for ambiguous cases to control API cost
- Process in batches of 100 to manage memory and rate limits
- Store intermediate results per-project to allow incremental runs

## Plan Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-25T16:30:00Z
decision: passed
