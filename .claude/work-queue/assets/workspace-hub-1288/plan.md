# WRK-1295: Batch LLM Summaries — ace_standards + workspace_spec

## Plan (Route B)

### Phase 1: Unblock workspace_spec (Phase A indexing)
- Run Phase A indexing for workspace_spec source
- Verify records in index.jsonl (expected ≥1,587)

### Phase 2: Launch Phase B batch
- `bash scripts/data/document-index/launch-batch.sh 10 ace_standards`
- `bash scripts/data/document-index/launch-batch.sh 4 workspace_spec`
- Resume-safe: rerun to continue from interruption

### Phase 3: Validate & report
- Run phase_b_checkpoint.py for completion stats
- Spot-check 20 random docs for quality
- Report discipline distribution

## Budget
~$114 at Haiku rates (user approved)

## Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-23T14:00:00Z
decision: passed
