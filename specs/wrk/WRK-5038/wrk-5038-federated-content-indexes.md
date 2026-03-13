# WRK-5038: build-doc-intelligence.py + Federated Content Indexes

## Mission
Build federated index builder that reads all WRK-5037 manifests and produces 8 content-type JSONL indexes.

## Architecture
Manifests (YAML) -> classifiers.py (heuristic) -> 6 content-type JSONL + tables CSV + curves index + manifest-index.

## Files Created
- `scripts/data/doc_intelligence/classifiers.py` — 6 heuristic classifiers
- `scripts/data/doc_intelligence/index_builder.py` — core builder
- `scripts/data/doc-intelligence/build-doc-intelligence.py` — CLI
- Tests: 50 total (26 classifier + 24 index builder)

## Key Decisions
- Priority: requirements > worked_examples > constants > equations > procedures > definitions
- Incremental via manifest checksum
- Atomic writes (tmpfile + os.replace)
- Path traversal defense via _sanitize_ref()

## Plan Confirmation
confirmed_by: vamsee
confirmed_at: 2026-03-13T04:15:00Z
decision: passed
