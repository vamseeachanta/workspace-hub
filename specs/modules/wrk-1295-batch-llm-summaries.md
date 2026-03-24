# WRK-1295: Batch LLM Summaries — ace_standards + workspace_spec

## Summary

Run Phase B (LLM classification) on ace_standards and workspace_spec documents using
the proven `phase-b-claude-worker.py` pipeline. Resume-safe, parallelized via `launch-batch.sh`.

## Pre-Conditions

1. workspace_spec must be indexed in Phase A first (currently 0 records in index.jsonl)
2. Budget approval needed: ~$114 at Haiku rates (not $9 as originally stated)

## Execution Plan (≤3 phases)

### Phase 1: Unblock workspace_spec (Phase A indexing)
- Run Phase A indexing for workspace_spec source
- Verify records appear in `data/document-index/index.jsonl`
- Expected: ~1,587 records indexed

### Phase 2: Launch Phase B batch
- `bash scripts/data/document-index/launch-batch.sh 10 ace_standards`
- `bash scripts/data/document-index/launch-batch.sh 4 workspace_spec`
- Monitor via logs: `data/document-index/logs/claude-shard-*.log`
- Resume-safe: rerun same command to continue from interruption

### Phase 3: Validate & report
- Run `phase_b_checkpoint.py` for completion stats
- Spot-check 20 random docs for summary quality
- Report classification distribution by discipline

## Acceptance Criteria

1. [ ] workspace_spec Phase A complete (≥716 records in index)
2. [ ] ace_standards Phase B complete (≥90% of indexed docs classified)
3. [ ] workspace_spec Phase B complete (≥90% of indexed docs classified)
4. [ ] Spot-check 20 random docs — summaries coherent and discipline correct
5. [ ] Total cost within approved budget

## Pseudocode — Key Operations

```
# Phase 1: Index workspace_spec
for file in workspace_spec_mount:
    extract_metadata(file)  # title, path, size, type
    write_to_index_jsonl(metadata)
verify_count(index, "workspace_spec") >= 716

# Phase 2: Batch classify
for source in [ace_standards, workspace_spec]:
    for shard in range(N_SHARDS):
        worker = spawn(phase-b-claude-worker.py, --shard=shard, --total=N_SHARDS, --source=source)
        # Each worker:
        for doc in shard_docs:
            if needs_llm(doc.sha):  # skip already classified
                text = extract_text(doc)  # og_sqlite | pdftotext_p3 | direct | metadata_only
                result = claude_haiku(text)  # {discipline, summary, keywords}
                write_summary_json(doc.sha, result)

# Phase 3: Validate
stats = phase_b_checkpoint()
assert stats.completion_pct >= 90
spot_check = random.sample(summaries, 20)
for s in spot_check:
    assert len(s.summary) <= 25_words
    assert s.discipline in VALID_DISCIPLINES
```

## Test Plan

| Test | Type | Expected |
|------|------|----------|
| Phase A indexes workspace_spec files | happy | ≥716 records in index.jsonl with source=workspace_spec |
| Phase B classifies ace_standards doc | happy | Summary JSON with valid discipline, ≤25 word summary, keywords[] |
| Phase B resumes after interruption | edge | Rerun skips already-classified docs, no duplicates |
| Phase B handles unreadable PDF | error | Falls back to metadata_only extraction, still produces classification |

## Scripts to Create

N/A — all scripts already exist and are production-ready:
- `phase-b-claude-worker.py` (423 lines, resume-safe)
- `launch-batch.sh` (parallel shard orchestrator)
- `phase_b_checkpoint.py` (completion reporter)

## Cost & Risk

| Item | Value |
|------|-------|
| Estimated cost | ~$114 (Haiku @ $0.002/doc × ~57,173 docs) |
| Risk | Low — pipeline proven on 26K og_standards docs (WRK-1188) |
| Blocker | workspace_spec Phase A indexing |
