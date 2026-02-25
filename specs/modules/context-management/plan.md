# Context-Efficient Subagent & Skills Management Plan

> Created: 2026-01-14
> Status: Planning
> Goal: Manage subagents and skills to effectively use task context without exceeding limits

## Executive Summary

This plan addresses context overflow prevention for the workspace-hub multi-repository management system. Based on analysis of last week's work (54 commits, Phase 1e validation across 27 repositories) and Claude's context management feedback, we implement a hierarchical agent structure with file-based state persistence.

---

## Part 1: Last Week's Work Summary (Jan 7-14, 2026)

### Completed Work

| Category | Achievement | Impact |
|----------|-------------|--------|
| **pytest Baseline** | Deployed to 7 repositories (Phase 2 Tier 3) | 491 tests across 15 repos |
| **Cross-Repo Validation** | 27/47 repos have pytest, 15/27 collect tests | Foundation for CI/CD |
| **Legacy Assets** | 1,229,875 files indexed from /mnt/ace | Knowledge base ready |
| **Git Commits** | 54 commits in workspace-hub | Significant progress |

### Blockers Requiring Attention

| Repository | Issue | Priority |
|------------|-------|----------|
| digitalmodel | Missing pytest.ini markers, ModuleNotFoundError | Tier 1 Critical |
| worldenergydata | RAG/knowledge system import errors | Tier 1 Critical |
| assetutilities | Unknown collection errors | Tier 1 Critical |
| teamresumes | Unknown collection errors | Tier 1 Critical |

### Timeline

- **Phase 1 Completion**: 3-5 days (Jan 17-19)
- **Phase 2 Start**: Jan 17-20, 2026

---

## Part 2: Context Management Implementation Plan

### Strategy 1: Skills as Compressed Knowledge (~500 tokens vs thousands)

**Implementation:**

Create focused skill files in `~/.claude/skills/context-management/`:

```
~/.claude/skills/context-management/
├── SKILL.md                    # Main context rules skill
├── response-format.md          # Output formatting rules
├── agent-coordination.md       # Hierarchical agent patterns
└── file-state-patterns.md      # File-based state workflows
```

**File: context_rules.md**
```markdown
## Response Format Rules
- Tables: max 10 rows, summarize if more
- Write large outputs to /outputs/, return path only
- End responses with: STATUS | NEXT_STEP | KEY_VALUES

## Prohibited Actions
- Echoing input data back
- Repeating previous findings unless asked
- Explanations >3 sentences unless requested
- Pasting raw file contents (use paths instead)

## Mandatory Patterns
- Summarize before returning
- Use file references not content
- Aggregate counts not lists
```

### Strategy 2: Summarization Checkpoints

**Implementation Pattern:**

After each major operation, create checkpoint summaries:

```yaml
checkpoint_workflow:
  - step: "Execute task"
    action: "Run agent with specific scope"

  - step: "Summarize findings"
    format: |
      ## Checkpoint: [TASK_NAME]
      **Status:** [complete|in_progress|blocked]
      **Key Findings:** [3-5 bullet points max]
      **Files Modified:** [paths only]
      **Next Action:** [single sentence]
      **Critical Values:** [key=value pairs]

  - step: "Persist to file"
    output: ".claude/checkpoints/[date]-[task].md"
```

**Checkpoint Template:**
```markdown
## Checkpoint: pytest-validation
**Status:** in_progress
**Key Findings:**
- 15/27 repos can collect tests (56% success)
- 12 repos need configuration fixes
- 491 total tests discovered
**Files Modified:** PHASE_1E_CROSS_REPO_VALIDATION_REPORT.md
**Next Action:** Fix Tier 1 blockers (4 repos)
**Critical Values:** success_rate=56%, total_tests=491, blocked=4
```

### Strategy 3: Hierarchical Agent Structure

**Architecture:**

```
┌─────────────────────────────────────────────┐
│           COORDINATOR AGENT                 │
│  - Minimal context (system + skills only)   │
│  - Receives summaries only                  │
│  - Orchestrates worker dispatch             │
└──────────────────┬──────────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ WORKER 1 │ │ WORKER 2 │ │ WORKER 3 │
│ Heavy    │ │ Heavy    │ │ Heavy    │
│ context  │ │ context  │ │ context  │
│ ────────▶│ ────────▶│ ────────▶│
│ Returns  │ │ Returns  │ │ Returns  │
│ summary  │ │ summary  │ │ summary  │
│ only     │ │ only     │ │ only     │
└──────────┘ └──────────┘ └──────────┘
```

**Implementation:**

```bash
# Coordinator pattern - spawn workers with summary-only return
./scripts/batchtools/batch_runner.sh \
  --parallel 5 \
  --output-format summary \
  --max-response-tokens 500 \
  < tasks.json
```

**Worker Response Contract:**
```json
{
  "worker_id": "pytest-validator-1",
  "status": "complete",
  "summary": "Validated 5 repos: 4 passed, 1 blocked (digitalmodel)",
  "output_file": ".claude/outputs/pytest-validation-batch1.json",
  "next_action": "Fix digitalmodel pytest.ini",
  "key_metrics": {
    "repos_validated": 5,
    "passed": 4,
    "blocked": 1
  }
}
```

### Strategy 4: File-Based State (Not Context)

**State Management Pattern:**

```
.claude/
├── state/
│   ├── current_task.json       # Active task state
│   ├── agent_results/          # Worker outputs
│   │   ├── worker-1-result.json
│   │   └── worker-2-result.json
│   └── aggregated_state.json   # Merged results
├── checkpoints/
│   ├── 2026-01-14-pytest.md
│   └── 2026-01-14-legacy.md
└── outputs/
    ├── reports/
    └── data/
```

**Workflow Example:**
```yaml
workflow:
  name: "pytest-validation"
  steps:
    - agent: "test-runner"
      scope: "digitalmodel"
      input_file: "config/repos.conf"
      output_file: ".claude/state/agent_results/digitalmodel.json"
      # Result saved to disk, NOT held in context

    - agent: "test-runner"
      scope: "worldenergydata"
      input_file: "config/repos.conf"
      output_file: ".claude/state/agent_results/worldenergydata.json"

    - agent: "aggregator"
      input_pattern: ".claude/state/agent_results/*.json"
      output_file: ".claude/state/aggregated_state.json"
      # Loads only summaries, not full results
```

### Strategy 5: Sliding Window with Persistent Memory

**ContextManager Implementation:**

```python
# .claude/tools/context_manager.py

class ContextManager:
    def __init__(self, max_tokens=80000, archive_threshold=60000):
        self.max_tokens = max_tokens
        self.archive_threshold = archive_threshold
        self.state_file = ".claude/state/context_state.json"
        self.archive_dir = ".claude/archives/"

    def should_archive(self, current_tokens):
        return current_tokens > self.archive_threshold

    def archive_exchanges(self, messages):
        """Archive older exchanges, keep recent 3"""
        archived = messages[:-3]
        summary = self.summarize_archived(archived)

        # Write to archive file
        archive_path = f"{self.archive_dir}/{timestamp()}.json"
        write_json(archive_path, archived)

        # Return summary reference
        return {
            "archived_count": len(archived),
            "archive_path": archive_path,
            "summary": summary
        }

    def trim_context(self, messages):
        """Keep: system prompt, skills, recent 3 exchanges"""
        essential = [m for m in messages if m.get("role") == "system"]
        recent = messages[-3:]
        return essential + recent
```

---

## Part 3: Implementation Tasks

### Phase A: Core Infrastructure (Day 1-2)

- [ ] 1. Create `~/.claude/skills/context-management/SKILL.md` with response format rules
- [ ] 2. Create `.claude/state/` directory structure for file-based state
- [ ] 3. Create `.claude/checkpoints/` for summarization checkpoints
- [ ] 4. Update `.claude/CLAUDE.md` with context management directives

### Phase B: Agent Coordination (Day 2-3)

- [ ] 5. Implement worker response contract (summary-only returns)
- [ ] 6. Update `scripts/batchtools/batch_runner.sh` with `--output-format summary`
- [ ] 7. Create aggregator agent pattern for merging worker results
- [ ] 8. Test hierarchical coordination with 3 workers

### Phase C: Workflow Patterns (Day 3-4)

- [ ] 9. Create file-based workflow templates in `.claude/workflows/`
- [ ] 10. Implement checkpoint automation after major operations
- [ ] 11. Add sliding window to existing Task tool invocations
- [ ] 12. Document patterns in `docs/modules/ai/CONTEXT_MANAGEMENT.md`

### Phase D: Integration & Testing (Day 4-5)

- [ ] 13. Apply to Tier 1 blocker fixes (digitalmodel, worldenergydata)
- [ ] 14. Validate context reduction (target: 50% reduction)
- [ ] 15. Update session-start-routine to include context health check
- [ ] 16. Create monitoring for context usage patterns

---

## Part 4: Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Context overflow incidents | Unknown | 0 per day | Manual tracking |
| Average response size | Large | <500 tokens for summaries | Token count |
| Worker return format | Full output | Summary only | JSON schema validation |
| State persistence | In context | File-based | File existence |
| Checkpoint coverage | 0% | 100% major ops | Checkpoint count |

---

## Part 5: Quick Wins (Immediate Actions)

1. **Don't paste raw data** - Use file paths instead
2. **Specific queries** - Ask for exactly what's needed
3. **Clear context between tasks** - Use TodoWrite to track, not repeat
4. **Chunk large files** - Process in segments, aggregate results
5. **End with status format** - `STATUS | NEXT_STEP | KEY_VALUES`

---

## Appendix: Bash Permissions Required

```yaml
allowedPrompts:
  - tool: Bash
    prompt: "create directories in .claude/"
  - tool: Bash
    prompt: "run pytest validation"
  - tool: Bash
    prompt: "execute batch runner scripts"
```
