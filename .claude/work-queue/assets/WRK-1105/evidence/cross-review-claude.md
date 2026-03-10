## Verdict: MINOR

### Summary
WRK-1105 plan has been updated to address all P1 findings from the initial review: test count normalized to ≥16 across all references, migration pseudocode now uses a block-aware multi-line accumulator, idempotency contract defined for all three capture paths, career-learnings.yaml query path clarified via build-knowledge-index.sh normalization and index.jsonl fallback in query-knowledge.sh.

### Pseudocode Review
- [PASS] capture-wrk-summary.sh: flock, best-effort, explicit YAML guard, idempotency check
- [PASS] query-knowledge.sh: index.jsonl preferred, raw JSONL fallback, domain/keyword filter
- [PASS] migrate-memory-to-knowledge.sh: block-aware accumulator, dry-run, idempotency
- [PASS] build-knowledge-index.sh: normalizes all stores, flock, dedup, atomic write

### Findings
- [P2] compact-memory.py has 21 existing TDD tests (WRK-637). Phase 3 exit criteria should explicitly require those 21 tests pass after Phase 3.4 routing changes.
- [P2] career-learnings.yaml schema should be defined in Phase 1 ADR (fields: id, domain, skill_area, context, learned_at, source_wrk, legal_reviewed). Currently left implicit.
- [P3] knowledge-base/*.jsonl is gitignored runtime data with no backup mechanism. Consider noting this in the risks table and capturing a future-work item for cross-session sync.
- [P3] build-knowledge-index.sh nightly cron guard (flock) needs a corresponding test (currently covered by test_index_deduplicates but not concurrent-lock test).
