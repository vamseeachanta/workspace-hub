# Claude Rules Quick Reference

## 🚨 Critical Rules (Never Break These)

1. **TDD is Mandatory**: Write failing test → Implement → Refactor (for ALL features/bugfixes)
2. **YAGNI**: Don't add features we don't need right now
3. **Push Back**: MUST call out bad ideas and mistakes (it's required, not optional)
4. **Batch Operations**: 1 message = ALL related operations (TodoWrite, Tasks, Files, Bash)
5. **Root Cause Only**: Never fix symptoms or add workarounds
6. **No Sycophancy**: Never write "You're absolutely right!" or excessive praise
7. **Stop and Ask**: Always clarify rather than making assumptions

## 📐 Code Quality Standards

### Naming
- ✅ Domain-focused: `Tool`, `RemoteTool`, `execute()`
- ❌ Implementation details: `MCPWrapper`, `executeToolWithValidation()`
- ❌ Temporal context: `NewAPI`, `LegacyHandler`, `ImprovedInterface`

### Comments
- ✅ Explain WHAT/WHY: `// Executes tools with validated arguments`
- ❌ Historical context: `// Refactored from old system`
- ❌ Implementation details: `// Uses Zod for validation`
- **Required**: `ABOUTME:` headers (2 lines, greppable)

### File Organization
- `/src` - Source code
- `/tests` - Test files
- `/docs` - Documentation
- `/config` - Configuration
- `/scripts` - Utility scripts
- `/data` - CSV data (raw/, processed/, results/)
- `/reports` - Generated HTML reports

## 🧪 Test-Driven Development

```
FOR EVERY FEATURE OR BUGFIX:
1. Write failing test (validates desired functionality)
2. Run test (confirm it fails as expected)
3. Write ONLY enough code to pass
4. Run test (confirm success)
5. Refactor (keep tests green)
```

## 🐛 Systematic Debugging

```
Phase 1: Root Cause Investigation
  - Read error messages carefully
  - Reproduce consistently
  - Check recent changes (git diff)

Phase 2: Pattern Analysis
  - Find working examples
  - Compare against references
  - Identify differences
  - Understand dependencies

Phase 3: Hypothesis and Testing
  - Form single hypothesis
  - Test minimally
  - Verify before continuing
  - Say "I don't understand X" when unsure

Phase 4: Implementation
  - ALWAYS have simplest failing test
  - NEVER add multiple fixes at once
  - ALWAYS test after each change
  - STOP and re-analyze if fix doesn't work
```

## 🤖 AI Orchestration Patterns

### Correct Pattern (Parallel Execution)
```javascript
[Single Message]:
  Task("Research agent", "...", "researcher")
  Task("Coder agent", "...", "coder")
  Task("Tester agent", "...", "tester")
  TodoWrite { todos: [...8-10 todos...] }
  Write "file1.js"
  Write "file2.js"
  Bash "mkdir -p dirs && command"
```

### Wrong Pattern (Sequential Messages)
```javascript
Message 1: Task("agent 1")
Message 2: TodoWrite { todos: [single] }
Message 3: Write "file.js"
// ❌ This breaks parallel coordination!
```

## 📋 Agent Coordination Hooks

```bash
# BEFORE Work
npx claude-flow@alpha hooks pre-task --description "[task]"
npx claude-flow@alpha hooks session-restore --session-id "swarm-[id]"

# DURING Work
npx claude-flow@alpha hooks post-edit --file "[file]"
npx claude-flow@alpha hooks notify --message "[what was done]"

# AFTER Work
npx claude-flow@alpha hooks post-task --task-id "[task]"
npx claude-flow@alpha hooks session-end --export-metrics true
```

## 🔀 SPARC Workflow

1. **Specification** - Requirements analysis
2. **Pseudocode** - Algorithm design
3. **Architecture** - System design
4. **Refinement** - TDD implementation (← TDD applies here)
5. **Completion** - Integration

## 📝 Version Control

- Create WIP branch for unclear tasks
- Commit frequently (even incomplete work)
- NEVER skip pre-commit hooks
- NEVER use `git add -A` without `git status` first
- Commit journal entries

## 🎯 Rule Precedence

When rules overlap:
1. **Security/Safety** (highest priority)
2. **TDD Requirement** (mandatory)
3. **Code Quality** (Part 1 standards)
4. **Orchestration** (Part 2 patterns)
5. **Project-Specific** (Part 3 overrides)

## 🚀 Quick Commands

```bash
# Propagate rules to all repos
./modules/automation/propagate_claude_rules.sh --all --dry-run  # preview
./modules/automation/propagate_claude_rules.sh --all --backup   # deploy

# SPARC commands
npx claude-flow sparc modes                    # list modes
npx claude-flow sparc run <mode> "<task>"      # execute mode
npx claude-flow sparc tdd "<feature>"          # TDD workflow

# Agent orchestration
./modules/automation/agent_orchestrator.sh <task-type> "<description>"
```

## 🔍 Common Scenarios

### Starting New Feature
1. Write failing test
2. Use SPARC specification phase
3. Spawn agents in parallel (single message)
4. Follow TDD cycle
5. Commit frequently

### Debugging Issue
1. Read error message carefully
2. Reproduce consistently
3. Check recent changes
4. Form hypothesis
5. Test minimally
6. Find root cause (not symptom)

### Code Review
1. Check TDD compliance (tests exist?)
2. Verify naming standards
3. Review comment quality
4. Check for code duplication
5. Push back if standards violated

### Collaboration
1. Be direct and honest
2. Push back on bad ideas
3. Say "I don't understand" when unsure
4. Use journal for continuity
5. Signal discomfort: "Strange things are afoot at the Circle K"

## 📚 Full Documentation

- **Integration Plan**: `docs/CLAUDE_RULES_INTEGRATION_PLAN.md`
- **Deployment Guide**: `docs/CLAUDE_RULES_DEPLOYMENT.md`
- **Implementation Summary**: `docs/CLAUDE_RULES_INTEGRATION_SUMMARY.md`
- **Full Rules**: `CLAUDE.md` (28KB, three parts)

---

**Remember**: Claude Flow coordinates, Claude Code creates! | TDD is non-negotiable | YAGNI | Push back on bad ideas
