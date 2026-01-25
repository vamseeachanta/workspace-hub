# Best Practices Integration: everything-claude-code → workspace-hub

**Version:** 1.0.0
**Module:** claude-infrastructure
**Session ID:** curious-moseying-minsky
**Agent:** Claude Opus 4.5

---

## Summary

Integrate selected best practices from [everything-claude-code](https://github.com/affaan-m/everything-claude-code) into workspace-hub. Focus on gaps only—workspace-hub already has strong foundations (86 agents, 282 skills, 2 hooks).

## What Already Exists (Skip)

| Feature | Existing Location | Status |
|---------|-------------------|--------|
| TDD Workflow | `.claude/skills/development/tdd-obra/SKILL.md` | ✅ Complete (175 lines) |
| Context Management | `.claude/skills/context-management/SKILL.md` | ✅ Exists |
| Session Logging | `.claude/hooks/session-logger.sh` | ✅ Implemented (165 lines) |
| Orchestrator Pattern | `.claude/docs/orchestrator-pattern.md` | ✅ Documented |
| Context Limits | `.claude/docs/CONTEXT_LIMITS.md` | ✅ Enforced |

---

## Phase 1: High Priority (Core Gaps)

### 1.1 Verification Loop Skill
**Path:** `.claude/skills/development/verification-loop/SKILL.md`

6-phase quality gate missing from current infrastructure:
1. **build** - `npm run build` / `uv build` / `cargo build`
2. **typecheck** - `tsc --noEmit` / `pyright` / `mypy`
3. **lint** - `eslint` / `ruff` / `clippy`
4. **test** - `pytest --cov` / `npm test`
5. **security** - `npm audit` / `bandit` / `safety check`
6. **diff-review** - `git diff HEAD~1 --stat` summary

**Structure:**
```yaml
---
name: verification-loop
description: 6-phase quality gate for code changes
version: 1.0.0
category: development
phases: [build, typecheck, lint, test, security, diff-review]
---
```

### 1.2 Rules Directory
**Path:** `.claude/rules/`

Create structured rule files:

| File | Purpose | Lines |
|------|---------|-------|
| `security.md` | No hardcoded secrets, input validation, XSS/CSRF prevention | ~50 |
| `testing.md` | TDD mandate, 80% coverage, fix implementation not tests | ~60 |
| `coding-style.md` | Naming, 200-400 lines/file max, <50 lines/function | ~40 |
| `git-workflow.md` | Branch naming, commit message format, PR process | ~50 |
| `patterns.md` | Allowed/prohibited patterns, error handling | ~70 |
| `README.md` | Index and loading instructions | ~30 |

### 1.3 Explorer Agent
**Path:** `.claude/agent-library/core/explorer.md`

Read-only file search specialist (complements existing researcher):
- Constraints: `read_only: true`, `max_files_read: 20`
- Output: Summaries only, never raw file content
- Tools: Glob, Grep, Read only

### 1.4 Session Memory Persistence Hooks
**Path:** `.claude/hooks/session-memory/`

Extend existing session-logger with state persistence:

| Script | Trigger | Purpose |
|--------|---------|---------|
| `pre-compact-save.sh` | PreCompact | Save state to `.claude/state/session-memory.json` |
| `session-end-evaluate.sh` | Stop | Evaluate patterns for learning |

**State File Structure:**
```json
{
  "active_plan": "specs/modules/feature-x.md",
  "completed_tasks": ["task-1"],
  "pending_tasks": ["task-2"],
  "context_budget_used": "45%"
}
```

**Settings Update** (`.claude/settings.json`):
```json
"PreCompact": [{
  "matcher": ".*",
  "hooks": [{
    "type": "command",
    "command": "cat | \"${WORKSPACE_HUB}/.claude/hooks/session-memory/pre-compact-save.sh\""
  }]
}]
```

---

## Phase 2: Medium Priority (Documentation)

### 2.1 Command Registry Documentation
**Path:** `.claude/docs/command-registry.md`

Map 155 commands to agents with prerequisites:

```markdown
| Command | Agent | Prerequisites |
|---------|-------|---------------|
| /tdd | tester | pytest/jest |
| /code-review | reviewer | git diff |
| /plan | planner | None |
```

### 2.2 Agent Composition Patterns
**Path:** `.claude/docs/agent-composition.md`

Document command chaining:
- Feature: `/plan` → `/tdd` → `/code-review` → commit
- Bug fix: `/tdd` (reproduce) → `/code` → `/verify`
- Refactor: `/plan` → `/code` → `/verify` → `/code-review`

### 2.3 MCP Strategy Update
**Path:** `.claude/docs/mcp-tools.md` (update existing)

Add context budget allocation section:

| MCP Server | Token Budget | Priority |
|------------|--------------|----------|
| claude-flow | 2000 | High |
| Browser tools | 500 | Low |

---

## Phase 3: Low Priority (Automation)

### 3.1 Rule Audit Script
**Path:** `scripts/audit/rule-compliance.sh`

Automated compliance checking:
- Test coverage >= 80%
- No hardcoded secrets (grep patterns)
- File size limits
- Branch naming validation

---

## Files to Create/Modify

### New Files (10)
```
.claude/skills/development/verification-loop/SKILL.md
.claude/rules/security.md
.claude/rules/testing.md
.claude/rules/coding-style.md
.claude/rules/git-workflow.md
.claude/rules/patterns.md
.claude/rules/README.md
.claude/agent-library/core/explorer.md
.claude/hooks/session-memory/pre-compact-save.sh
.claude/hooks/session-memory/session-end-evaluate.sh
```

### Files to Update (3)
```
.claude/settings.json                    # Add session-memory hooks
.claude/docs/mcp-tools.md               # Add context budget section
.claude/docs/command-registry.md        # Create from scratch (medium priority)
```

---

## Implementation Order

```
Phase 1 (No dependencies):
├── 1.1 Verification Loop Skill
├── 1.2 Rules Directory (all 6 files)
└── 1.3 Explorer Agent

Phase 2 (After Phase 1):
├── 1.4 Session Memory Hooks + settings.json update
└── 2.1-2.3 Documentation updates

Phase 3 (After Phase 2):
└── 3.1 Rule Audit Script
```

---

## Verification

### Per-Item Testing

| Item | Test Method |
|------|-------------|
| Verification Loop | Run `/verify` on digitalmodel, confirm 6 phases execute |
| Rules | Load via `Read .claude/rules/testing.md`, verify content |
| Explorer Agent | Spawn via `Task(subagent_type=Explore)`, verify summaries |
| Session Memory | End session, check `.claude/state/session-memory.json` exists |
| Command Registry | Load doc, verify command→agent mappings present |

### Integration Test
```bash
# End-to-end workflow
/plan "Test feature"           # Creates plan
/tdd                           # Runs TDD workflow
/verify                        # Runs 6-phase gate (NEW)
git commit                     # Should pass all rules
```

---

## Scope Estimate

| Priority | Items | New Files | Lines |
|----------|-------|-----------|-------|
| High | 4 | 10 | ~600 |
| Medium | 3 | 2 | ~350 |
| Low | 1 | 1 | ~100 |
| **Total** | **8** | **13** | **~1050** |

---

## Constraints

- ✅ CLAUDE.md stays under 4KB (rules extracted to `.claude/rules/`)
- ✅ Reference docs in `.claude/docs/` (on-demand loading)
- ✅ Existing directory structure preserved
- ✅ No breaking changes to current workflows
