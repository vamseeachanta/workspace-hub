# Adversarial Plan Review — Hermes Parallel Review

Issue: #2402
Verdict: MAJOR

## Major findings
1. The plan depends on L3 wiki `doc_key` coverage that is not present in the current repo state, so the intended corpus build would skip most/all target wiki content.
2. The query design promises excerpt-bearing results, but the planned storage schema does not preserve chunk text needed to return excerpts.
3. The single-authoritative-tier design removes shared derived-artifact behavior without a workable cross-machine replacement for queryable retrieval artifacts.

## Minor findings
1. The acceptance target for initial row count is not grounded in the current corpus evidence.

## Operational conclusion
Revise the canonical plan, then rerun adversarial review before user approval.
