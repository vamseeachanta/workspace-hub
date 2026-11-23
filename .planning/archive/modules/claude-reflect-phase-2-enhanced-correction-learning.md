---
title: Claude Reflect Phase 2 - Enhanced Correction Learning
description: Add file-type detection, correction chains, and edit context capture to the RAGS correction pipeline
version: 1.0.0
module: claude-reflect
session:
  id: 2026-01-28-morning
  agent: claude-opus-4.5
review:
  status: planning
  iterations: 0
---

# Reflect Phase 2 - Enhanced Correction Learning

## Summary

Extend the existing correction capture hook and RAGS pipeline with three features:
1. **Edit context capture** - What was changed (old/new string previews)
2. **Correction chain tracking** - Temporal sequences of edits (A -> B -> A patterns)
3. **File-type pattern detection** - Correction rates by file extension

## Files to Modify

| File | Lines | Change |
|------|-------|--------|
| `.claude/hooks/capture-corrections.sh` | 119 | Add all 3 features to hook output |
| `.claude/skills/coordination/workspace/claude-reflect/scripts/extract-corrections.sh` | 86 | Add file-type, chain, context aggregations |
| `.claude/skills/coordination/workspace/claude-reflect/scripts/analyze-trends.sh` | 165 | Add file-type trends + chain recommendations |
| `.claude/skills/coordination/workspace/claude-reflect/scripts/daily-reflect.sh` | 806 | Report new metrics in state YAML |

## New Files

| File | Purpose |
|------|---------|
| `scripts/tests/test-capture-corrections.sh` | Hook tests (6 tests) |
| `scripts/tests/test-extract-corrections.sh` | Extract pipeline tests (5 tests) |
| `scripts/tests/test-analyze-trends.sh` | Trend analysis tests (3 tests) |
| `scripts/tests/fixtures/` | JSONL + JSON test fixtures |

(Tests dir: `.claude/skills/coordination/workspace/claude-reflect/scripts/tests/`)

## Design Decisions

### Feature 1: Edit Context

**Approach**: Extract `old_string`/`new_string` from Edit tool input and `content` from Write tool input (already available via PostToolUse stdin JSON). Cap previews at 100 chars.

**Why not full prompt context?** Claude Code hooks only support `PreToolUse`/`PostToolUse`/`PreCompact`/`Stop` - no `PrePrompt` hook exists. The tool input is the best real-time proxy. The daily `analyze-conversations.sh` already parses full prompts and can be cross-referenced by timestamp in the pipeline.

### Feature 2: Correction Chains

**Approach**: Add `edit_sequence_id` (incrementing counter) to every edit in `.recent_edits`. When a correction is detected, scan `.recent_edits` for all edits within the 600s window to build the chain. Assign a `chain_id` linking related edits.

**Chain classification** (in extract-corrections.sh):
- `cascade` - 3+ unique files in chain
- `ping_pong` - 2 files bouncing
- `single_file_iteration` - same file repeatedly

### Feature 3: File-Type Detection

**Approach**: Three layers:
1. Hook: add `file_extension` field (`${FILE_PATH##*.}`)
2. Extract: group corrections by extension, compute per-type stats
3. Trends: track file-type correction rates across days

## Schema Changes

### Extended JSONL (backward compatible - new fields only)

```json
{
  "timestamp": "...",
  "file": "...",
  "basename": "...",
  "tool": "Edit",
  "correction_gap_seconds": 7,
  "diff_stat": "...",
  "type": "correction",
  "file_extension": "sh",
  "edit_context": {
    "old_string_preview": "first 100 chars...",
    "new_string_preview": "first 100 chars..."
  },
  "chain_id": "20260128_a1b2c3d4",
  "chain_position": 2,
  "chain_files": ["/path/a.py", "/path/b.py"],
  "edit_sequence_id": 42
}
```

### Extended .recent_edits (backward compatible)

```
timestamp|filepath|sequence_id     # new format
timestamp|filepath                 # old format still parseable
```

## Implementation Order (TDD)

| Step | Action | Details |
|------|--------|---------|
| 1 | Create test fixtures | Real-format JSONL + JSON fixtures |
| 2 | Write hook tests | 6 tests for capture-corrections.sh |
| 3 | Write extract tests | 5 tests for extract-corrections.sh |
| 4 | Write trends tests | 3 tests for analyze-trends.sh |
| 5 | Run tests (RED) | All fail - no implementation yet |
| 6 | Implement hook | Consolidate jq, add extension/context/chain |
| 7 | Run hook tests (GREEN) | Verify hook changes |
| 8 | Implement extract | Add 3 new jq aggregation blocks |
| 9 | Run extract tests (GREEN) | Verify pipeline changes |
| 10 | Implement trends | Add file_type_trends + chain recommendations |
| 11 | Run trends tests (GREEN) | Verify trend changes |
| 12 | Update daily-reflect.sh | Report new metrics |
| 13 | Integration test | Full pipeline with real state data |
| 14 | Performance test | Verify hook stays < 50ms |

## Key Implementation Details

### capture-corrections.sh Changes

**Consolidate jq calls** (lines 56-59) into one for performance:
```bash
eval $(echo "$INPUT" | jq -r '
  @sh "FILE_PATH=\(.tool_input.file_path // "")",
  @sh "TOOL_NAME=\(.tool_name // "Edit")",
  @sh "OLD_STRING=\(.tool_input.old_string // "" | .[0:100])",
  @sh "NEW_STRING=\(.tool_input.new_string // "" | .[0:100])",
  @sh "WRITE_CONTENT=\(.tool_input.content // "" | .[0:100])"
' 2>/dev/null)
```

**Add file extension** (after line 61):
```bash
FILE_EXTENSION="${FILE_PATH##*.}"
[[ "$FILE_EXTENSION" == "$FILE_BASENAME" ]] && FILE_EXTENSION="none"
```

**Add sequence counter + chain detection** (replace lines 63-81):
- Increment `$STATE_DIR/.edit_sequence_counter`
- On correction: scan `.recent_edits` for edits within 600s window
- Build `chain_id` = `YYYYMMDD_<hash>`, `chain_files` array

**Performance budget**: Single jq parse (~15ms) + chain scan of 50 lines (~10ms) + output jq (~10ms) = ~35ms. Safe under 50ms.

### extract-corrections.sh Changes

Add 3 new blocks to the jq pipeline (after line 71, before `learnings`):

1. `file_type_patterns` - group by `.file_extension`, count, avg gap, rank
2. `chain_patterns` - group by `.chain_id`, classify cascade/ping_pong/iteration
3. `context_patterns` - group by file, sample edit context previews

### analyze-trends.sh Changes

Add after line 112 (before `repo_engagement`):
1. `file_type_trends` - aggregate file_type_patterns across days, calculate per-type trends
2. New recommendation for chains > 5

## Risks

| Risk | Mitigation |
|------|------------|
| Hook exceeds 50ms | Consolidated jq; store epoch in .recent_edits if date parse slow |
| `date -d` unavailable on macOS | Use `gdate` fallback (existing pattern in codebase) |
| `md5sum` unavailable on macOS | Fall back to `shasum -a 256 \| cut -c1-8` |
| Old JSONL missing new fields | All jq queries use `// null` defaults; tested with legacy fixtures |

## Verification

1. **Unit tests**: Run all 3 test files - all pass
2. **Hook performance**: `time echo '{"tool_name":"Edit",...}' | bash capture-corrections.sh` < 50ms
3. **Pipeline integration**: `DRY_RUN=true REFLECT_DAYS=7 ./daily-reflect.sh` completes with new metrics in output
4. **Backward compat**: Process existing `session_20260128.jsonl` through updated extract - no errors
5. **New fields present**: `jq '.file_type_patterns' < patterns_*.json` returns data
