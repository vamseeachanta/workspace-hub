# Cross-Review — Codex (Stage 6, WRK-1093) — HARD GATE

Verdict: MAJOR findings (hard gate)

## HIGH Issues
- build_doc_mention_set grep produces false positives/negatives — needs token-boundary matching rules
- detect_staleness underspecified: too coarse, per-file git calls expensive at scale

## MEDIUM Issues
- auto_wrk emission risks churn without dedup + threshold guards
- Test scope insufficient — need CLI/integration test and matcher edge cases

## Resolution
- MAJOR: batched git log per repo (not per file); auto_wrk returns human-review candidates only
- Token-boundary matching documented in implementation notes
- Extra tests added: CLI argparse, missing-index graceful degradation, substring false positive
