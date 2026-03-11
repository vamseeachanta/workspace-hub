confirmed_by: vamsee
confirmed_at: 2026-03-11T21:15:00Z
decision: passed

# WRK-1132 Plan — Multi-Code Standards Semantic Search

User approved this plan with "Implement the following plan" at session start.

## Architecture
- PyMuPDF (fitz) page-level PDF extraction
- BM25Okapi (rank_bm25) sub-second queries, no GPU/API required
- chunks.jsonl + bm25.pkl local offline index
- query-standards.sh bash CLI with --code/--topic/--limit flags
