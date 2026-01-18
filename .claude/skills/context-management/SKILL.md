# Context Management Skill

> Version: 1.1.0
> Created: 2026-01-14
> Updated: 2026-01-17
> Purpose: Prevent context overflow through efficient response patterns

## Quick Reference

```
%ctx = (current_tokens / 80000) * 100
Alert: >60% = archive older exchanges
Critical: >80% = trim to essentials only
```

## Response Format Rules

### Output Constraints
- **Tables**: Maximum 10 rows, summarize remainder with counts
- **Code blocks**: Maximum 50 lines, split larger into files
- **Lists**: Maximum 15 items, aggregate beyond that
- **Large outputs**: Write to `.claude/outputs/`, return path only

### Mandatory Response Ending
Every response MUST end with status line:
```
STATUS: [complete|in_progress|blocked] | NEXT: [single action] | KEY: [metric=value pairs]
```

Example:
```
STATUS: complete | NEXT: Run pytest on digitalmodel | KEY: repos=5, passed=4, blocked=1
```

## Prohibited Actions

1. **No Echo**: Never repeat input data back to user
2. **No Redundancy**: Don't repeat previous findings unless explicitly asked
3. **No Over-Explanation**: Keep explanations ≤3 sentences unless requested
4. **No Raw Content**: Use file paths instead of pasting file contents
5. **No Unbounded Lists**: Always cap with "and N more..."

## Mandatory Patterns

### Summarize Before Returning
```python
# BAD: Return full list
return all_test_results  # 500 items

# GOOD: Summarize
return {
    "total": 500,
    "passed": 480,
    "failed": 20,
    "details_file": ".claude/outputs/test_results.json"
}
```

### Use File References
```python
# BAD: Paste content
print(open("large_file.py").read())

# GOOD: Reference
print("See: src/module/large_file.py:45-120")
```

### Aggregate Counts
```python
# BAD: List all
["repo1", "repo2", "repo3", ... "repo25"]

# GOOD: Aggregate
"25 repositories (15 Work, 10 Personal)"
```

## Context Checkpoints

After major operations, create checkpoint:
```markdown
## Checkpoint: [TASK_NAME]
**Status:** [complete|in_progress|blocked]
**Key Findings:** [3-5 bullets max]
**Files Modified:** [paths only]
**Next Action:** [single sentence]
**Critical Values:** [key=value pairs]
```

Save to: `.claude/checkpoints/YYYY-MM-DD-task-name.md`

## Recovery Patterns

### Recovery from High Context (>60%)
When context exceeds threshold:
1. Create checkpoint immediately with current state
2. Write active task details to `.claude/outputs/session-state.json`
3. Clear verbose history from working memory
4. Continue with checkpoint reference only

```python
# Recovery state structure
{
  "checkpoint": "YYYY-MM-DD-task-name.md",
  "active_task": "description",
  "files_in_scope": ["path1", "path2"],
  "pending_actions": ["action1"],
  "critical_values": {"key": "value"}
}
```

### Auto-Archive Triggers
| Threshold | Action |
|-----------|--------|
| 60% | Archive completed task summaries to checkpoint |
| 70% | Compress repeated file reads to line references |
| 80% | Emergency trim - retain only current task essentials |
| 90% | Force checkpoint, request fresh context from user |

### Context Recovery Commands
```bash
# Resume from checkpoint
"Resume from checkpoint: .claude/checkpoints/YYYY-MM-DD-task.md"

# Load minimal context
"Continue task [name] - checkpoint saved, load essentials only"
```

### Subagent Output Enforcement
Worker outputs MUST:
- Return ≤500 chars to coordinator
- Write full results to `.claude/outputs/<task-id>.json`
- Include file path in summary response
- Never echo input parameters back

## Session Metrics
Track in STATUS line for monitoring:
```
KEY: files_read=N, tools_called=N, subagents=N, outputs_written=N, %ctx=N
```

## Worker Response Contract

When spawning subagents, enforce summary-only returns:
```json
{
  "worker_id": "string",
  "status": "complete|failed|blocked",
  "summary": "1-2 sentence result",
  "output_file": "path to detailed results",
  "next_action": "recommended next step",
  "key_metrics": {"metric": "value"}
}
```

## Context Health Indicators

| %ctx | Status | Action |
|------|--------|--------|
| 0-40% | 🟢 Healthy | Normal operation |
| 40-60% | 🟡 Elevated | Consider summarizing |
| 60-80% | 🟠 High | Archive older exchanges |
| 80-100% | 🔴 Critical | Trim to essentials |

## Integration

### With TodoWrite
- Track tasks, don't describe them
- Mark complete immediately after finishing
- One in_progress at a time

### With Task Tool
- Spawn workers with `--output-format summary`
- Workers return JSON contract, not full output
- Coordinator aggregates summaries only

### With File Operations
- Write large outputs to `.claude/outputs/`
- Return file path, not content
- Use relative paths from workspace root

---

## Version History

- **1.1.0** (2026-01-17): Add recovery patterns, auto-archive triggers, session metrics
- **1.0.0** (2026-01-14): Initial context management skill
