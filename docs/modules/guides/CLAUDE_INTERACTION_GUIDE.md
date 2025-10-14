# Claude Code Interaction Guide

## Understanding the "droid" Prefix

### What is "droid"?
**"droid" is your personal choice** - a prefix you use to address Claude (me). It's not a tool, agent, or configuration.

### Do You Need It?
**No!** I respond to all your messages regardless of prefix.

### Examples (All work the same):

```bash
# With prefix
droid, create a function

# Without prefix
create a function

# Polite form
please create a function

# Direct form
need a function for X
```

**All trigger the same response from Claude!**

---

## Factory.AI vs Claude Code

### Factory.AI Configuration
Factory.AI is about **AI agent selection and orchestration**:
- Which agent to use for tasks
- Agent capabilities and specialization
- Task routing and coordination

**It does NOT control:**
- How you address Claude
- Whether you need a trigger word
- Personal interaction preferences

### Claude Code Configuration
Claude Code settings control:
- Tool permissions
- MCP server access
- File operation rules
- Working directory

**It does NOT require:**
- Specific command prefixes
- Trigger words
- Special syntax

---

## Recommended Interaction Style

### For Maximum Efficiency

**Just ask directly without "droid":**

```bash
# ❌ Not needed
droid, create a CSV parser

# ✅ More efficient
create a CSV parser

# ✅ Even better (clear intent)
create a CSV parser that handles edge cases and validates data
```

### When Working with Multiple Agents/Tools

If you're using factory.ai to select agents, **factory.ai handles that automatically**:

```bash
# You just describe the task
analyze this codebase for performance bottlenecks

# Factory.ai automatically:
# 1. Selects best agent (code-analyzer, perf-analyzer, etc.)
# 2. Spawns agent via Claude Code Task tool
# 3. Coordinates execution
```

**No "droid" prefix needed!**

---

## Configuration Files Don't Control Interaction

### What CLAUDE.md Controls
```markdown
# CLAUDE.md controls:
- File organization rules
- Code style preferences
- Agent orchestration setup
- Tool usage patterns
```

### What CLAUDE.md Does NOT Control
```markdown
# CLAUDE.md does NOT control:
- Whether you say "droid"
- How you phrase questions
- Personal interaction style
```

---

## Bottom Line

### Simple Answer
**Just stop typing "droid" - I'll respond the same way!**

```bash
# Old way
droid, do task X

# New way (works identically)
do task X
```

### Why "droid" Isn't Needed
1. **I respond to all messages** in this chat
2. **No trigger words required** - Claude Code is already active
3. **Factory.ai auto-selects agents** based on task, not keywords
4. **"droid" is personal preference**, not a technical requirement

### When You Might Use Prefixes

Prefixes can be useful for **clarity in complex scenarios**:

```bash
# When delegating to specific tools
npx factory-ai analyze --task "performance review"

# When running specific agents
npx claude-flow task orchestrate --agent code-analyzer

# But for talking to Claude directly - no prefix needed!
```

---

## Recommended Workflow

### Current Setup
```bash
droid, create doc processor → I respond → factory.ai selects agent → task completes
```

### Simplified Workflow
```bash
create doc processor → I respond → factory.ai selects agent → task completes
```

**Same result, less typing!**

---

## If You Want True Automation

If you want **no human confirmation at all**, that's different:

### Option 1: Batch Scripts
```bash
#!/bin/bash
# automated_workflow.sh
./doc2context.sh docs/ --recursive --combine-by-directory
python analyze_contexts.py
npx factory-ai summarize --input context/
```

### Option 2: GitHub Actions
```yaml
# .github/workflows/auto-process.yml
on: [push]
jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - run: ./doc2context.sh docs/ --recursive
      - run: npx factory-ai analyze
```

### Option 3: Watch Mode (Future Enhancement)
```bash
# Could be implemented
./doc2context.sh docs/ --watch --auto-process
# Monitors directory, auto-processes new documents
```

---

## Summary

| What You Asked | Answer |
|----------------|--------|
| **Make "droid" unnecessary?** | ✅ Already is - just stop using it! |
| **Configure factory.ai for auto-response?** | ❌ factory.ai selects agents, not interaction style |
| **Default behavior without prefix?** | ✅ Works now - I respond to all messages |
| **Automation without confirmation?** | ➡️ Use scripts, GitHub Actions, or batch tools |

**TL;DR: Stop typing "droid" - it's not required. I respond to everything you type!**
