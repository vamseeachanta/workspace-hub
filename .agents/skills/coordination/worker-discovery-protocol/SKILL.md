---
name: worker-discovery-protocol
description: Protocol for workers to capture and propagate discoveries back to the orchestrator and shared knowledge base. Phase 3 of orchestrator/worker context enforcement (#2020).
version: 1.0.0
category: coordination
tags: [worker, knowledge, discovery, propagation, learning, orchestrator]
related_skills:
  - artifact-verification
  - comprehensive-learning-wrapper
  - agent-memory-bridge
  - extract-learnings-to-issues
issue_ref: "#2020"
---

# Worker Discovery Protocol

When a worker discovers something important during execution -- a bug, a pattern,
a convention, a tool quirk, a performance insight -- that knowledge must not die
with the worker's session. This skill defines how workers capture discoveries and
how orchestrators propagate them to the shared knowledge base.

## Why This Exists

Workers operate with fresh context and encounter the codebase without assumptions.
This makes them excellent at discovering:
- Undocumented conventions ("this file uses tabs, not spaces")
- Hidden dependencies ("module A silently imports module B at runtime")
- Tool quirks ("pytest requires --no-header flag for clean output here")
- Bug patterns ("this function fails silently when input is empty")
- Performance insights ("this query takes 30s without the index")

Without a capture protocol, these discoveries vanish when the worker session ends.
The next worker (or the same orchestrator in a future session) rediscovers the same
things, wasting time and tokens.

## Worker Responsibilities

### During Execution: Append to Discovery Log

When a worker encounters something noteworthy, it appends to a discovery log file
in the planning directory:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
DISCOVERY_FILE="$REPO_ROOT/.planning/discoveries/$(date +%Y-%m-%d)-worker.jsonl"
mkdir -p "$(dirname "$DISCOVERY_FILE")"

# Append one JSON line per discovery
echo '{"ts":"'"$(date -Iseconds)"'","issue":"#NNN","category":"bug","summary":"function X fails silently on empty input","detail":"src/module.py:42 returns None instead of raising ValueError","severity":"medium","source":"worker-codex-1"}' >> "$DISCOVERY_FILE"
```

### Discovery Categories

| Category | When to log | Example |
|----------|------------|---------|
| `bug` | Found a bug not in the issue scope | Silent failure, race condition, edge case |
| `convention` | Found an undocumented code convention | Naming pattern, import order, config format |
| `dependency` | Found a hidden or undocumented dependency | Runtime import, implicit file requirement |
| `quirk` | Found a tool or environment quirk | Flag requirement, version sensitivity |
| `performance` | Found a performance-relevant insight | Slow query, expensive operation, caching opportunity |
| `security` | Found a security-relevant issue | Exposed credential path, missing validation |
| `pattern` | Found a reusable code or workflow pattern | Helper function, test fixture, config template |

### At Session End: Summary Block

Before the worker session ends, it writes a summary block at the end of its
output or commit message:

```
## Worker Discoveries

- [bug] `src/parser.py:87` — silent failure on malformed input (not in scope, logged)
- [convention] Tests in this module use `@pytest.fixture(autouse=True)` pattern
- [quirk] `uv run` requires `--no-project` flag when running from subdirectory
```

## Orchestrator Responsibilities

### After Worker Returns: Triage Discoveries

The orchestrator reads the worker's discovery log and triages:

| Action | When | How |
|--------|------|-----|
| **Create issue** | Bug or security finding outside current scope | `gh issue create` with discovery details |
| **Update skill** | Convention or pattern that should be codified | Edit relevant SKILL.md or create new one |
| **Update KNOWLEDGE.md** | Quirk or insight that affects future sessions | Append to `.claude/memory/KNOWLEDGE.md` |
| **Update memory** | Correction to agent behavior or preference | Add to auto-memory via conversation |
| **Discard** | Already known or one-off observation | No action needed |

### Propagation Targets

| Discovery type | Primary target | Secondary target |
|---------------|---------------|-----------------|
| Bug | GitHub issue | None (tracked in issue) |
| Convention | Relevant SKILL.md | `.claude/rules/` if universal |
| Dependency | Module docstring or README | KNOWLEDGE.md |
| Quirk | KNOWLEDGE.md | `.claude/memory/topics/` |
| Performance | KNOWLEDGE.md | GitHub issue if actionable |
| Security | GitHub issue (priority:high) | KNOWLEDGE.md |
| Pattern | New or existing SKILL.md | `docs/methodology/` |

### Monthly Consolidation

The nightly comprehensive-learning pipeline (`scripts/cron/comprehensive-learning-nightly.sh`)
processes `.planning/discoveries/*.jsonl` files automatically. Orchestrators do not
need to manually process old discovery logs.

## Integration with Existing Systems

### Comprehensive Learning Pipeline

The discovery JSONL format is compatible with the session signals format used by the
comprehensive-learning pipeline. Discovery files in `.planning/discoveries/` are
picked up during the nightly knowledge harvesting phase.

### Agent Memory Bridge

Cross-agent propagation uses the existing `agent-memory-bridge` skill. When a
discovery applies to all agents (not just the discovering worker's provider):

1. Update `.claude/memory/KNOWLEDGE.md` (Claude Code picks this up)
2. Use `agent-memory-bridge` skill to sync to Hermes, Codex, and Gemini

### Extract Learnings to Issues

The `extract-learnings-to-issues` skill can process discovery logs and create
GitHub issues for actionable findings, preventing duplicate issue creation.

## Anti-Patterns

1. **Worker modifies knowledge files directly.** Workers should LOG discoveries,
   not update shared knowledge. The orchestrator triages and routes.

2. **Orchestrator ignores discovery log.** If the orchestrator does not triage,
   discoveries are lost until the nightly pipeline runs (which may not extract
   the same insights an orchestrator would).

3. **Logging everything.** Not every observation is a discovery. Workers should
   log only things that would save time for future workers or prevent future bugs.

4. **Logging without category.** Uncategorized discoveries are harder to triage.
   Always include the category field.

## Quick Reference

### Worker (during execution)
```
1. Encounter something noteworthy
2. Append to .planning/discoveries/YYYY-MM-DD-worker.jsonl
3. Include in session-end summary block
```

### Orchestrator (after worker returns)
```
1. Read .planning/discoveries/*.jsonl from today
2. Triage each discovery: issue / skill / knowledge / memory / discard
3. Execute the routing action
4. Mark discovery as processed (optional — nightly pipeline handles cleanup)
```

## References

- Comprehensive learning: `.claude/skills/coordination/comprehensive-learning-wrapper/SKILL.md`
- Agent memory bridge: `.claude/skills/coordination/agent-memory-bridge/SKILL.md`
- Extract learnings: use `/learn-extended` skill
- Orchestrator-worker methodology: `docs/methodology/orchestrator-worker.md`
- Session governance: `docs/governance/SESSION-GOVERNANCE.md`
