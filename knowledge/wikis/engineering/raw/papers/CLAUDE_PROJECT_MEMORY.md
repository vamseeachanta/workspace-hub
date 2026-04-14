# Claude Project Memory System

> **Factory AI Compatible:** Works with all agent variants including GPT-5 Codex
>
> **Version:** 1.0.0
> **Last Updated:** 2025-10-04

## Overview

The `.claude` directory contains project-specific memory, guidelines, and configuration that Factory AI agents automatically load at session start. This system ensures consistent development standards across all 26+ repositories in workspace-hub.

## Quick Start

```bash
# Navigate to any repository
cd /mnt/github/workspace-hub/<repo-name>

# Start Factory AI - automatically loads .claude/CLAUDE.md
droid

# Project memory and guidelines are now active!
```

## Directory Structure

```
workspace-hub/
├── .claude/                      # Workspace-hub master configuration
│   ├── CLAUDE.md                 # Primary project instructions (16KB)
│   ├── README.md                 # Documentation
│   ├── settings.json             # Session settings
│   ├── settings.local.json       # Local overrides (gitignored)
│   ├── agents/                   # Agent-specific configs
│   ├── checkpoints/              # Session state (gitignored)
│   ├── commands/                 # Custom slash commands
│   └── helpers/                  # Helper utilities
│
├── aceengineer-admin/
│   └── .claude/
│       ├── CLAUDE.md             # Inherits + repo-specific rules
│       └── README.md
│
└── [... 24 more repositories with .claude/ ...]
```

## What Gets Loaded

When you run `droid` in any repository:

1. **Automatic Loading**
   - Factory AI reads `.claude/CLAUDE.md` automatically
   - All instructions, standards, and workflows loaded into context
   - No manual file references needed

2. **Inherited Configuration**
   - Sub-repositories inherit workspace-hub standards
   - Repository-specific customizations overlay on top
   - Hierarchical configuration pattern

3. **Multi-Model Support**
   - Works with Claude 3.5 Sonnet
   - Works with GPT-5 Codex
   - Works with GPT-4.1
   - Works with all Factory AI agent variants

## Key Features

### SPARC Methodology

All repositories follow SPARC (Specification, Pseudocode, Architecture, Refinement, Completion) methodology:

- **Specification** - Requirements analysis
- **Pseudocode** - Algorithm design
- **Architecture** - System design
- **Refinement** - TDD implementation
- **Completion** - Integration

### Agent Orchestration

54+ specialized agents available:

- **Core Development:** coder, reviewer, tester, planner, researcher
- **Swarm Coordination:** hierarchical, mesh, adaptive coordinators
- **GitHub Integration:** pr-manager, code-review-swarm, issue-tracker
- **SPARC Specialists:** specification, pseudocode, architecture, refinement
- **Testing:** tdd-london-swarm, production-validator

### Concurrent Execution Pattern

**GOLDEN RULE:** "1 MESSAGE = ALL RELATED OPERATIONS"

```javascript
// ✅ CORRECT: Batch all operations in single message
[Single Message]:
  Task("Research agent", "...", "researcher")
  Task("Coder agent", "...", "coder")
  Task("Tester agent", "...", "tester")
  TodoWrite { todos: [...8-10 todos...] }
  Write "file1.js"
  Write "file2.js"
  Bash "command1 && command2"
```

### File Organization Rules

**NEVER save to root folder:**

- `/src` - Source code
- `/tests` - Test files
- `/docs` - Documentation
- `/config` - Configuration
- `/scripts` - Utility scripts
- `/data` - CSV data (raw/, processed/, results/)
- `/reports` - HTML reports

### HTML Reporting Standards

**MANDATORY for all modules:**

1. **Interactive Plots Only** - Plotly, Bokeh, Altair, D3.js
   - ❌ NO static matplotlib PNG/SVG
   - ✅ Interactive with hover, zoom, pan, export

2. **HTML Reports Required**
   - Analysis reports with visualizations
   - Performance dashboards
   - Data quality reports

3. **CSV Data Import**
   - Relative paths from report location
   - Store in `/data/raw/`, `/data/processed/`, `/data/results/`

## Git Configuration

### What's Committed

✅ **Committed to version control:**
- `.claude/CLAUDE.md` - Shared team instructions
- `.claude/README.md` - Documentation
- `.claude/settings.json` - Shared settings
- `.claude/agents/` - Agent configurations
- `.claude/commands/` - Custom commands
- `.claude/helpers/` - Helper utilities

### What's Ignored

❌ **Ignored (not committed):**
- `.claude/settings.local.json` - Personal overrides
- `.claude/checkpoints/` - Session state
- `.claude/*.session.json` - Session files
- `.claude/*.memory.json` - Memory files

### .gitignore Configuration

```gitignore
# Claude Code project memory - ignore local settings and checkpoints
.claude/settings.local.json
.claude/checkpoints/
```

## Updating Guidelines

### When to Update

Edit `.claude/CLAUDE.md` when you need to:

- ✅ Add new coding standards or best practices
- ✅ Define project-specific workflows
- ✅ Update agent orchestration patterns
- ✅ Add new tools or integrations
- ✅ Modify file organization rules
- ✅ Update testing requirements

### How to Update

```bash
# 1. Edit the file
vim .claude/CLAUDE.md

# 2. Commit changes (if shared across team)
git add .claude/CLAUDE.md
git commit -m "Update project guidelines: [description]"
git push

# 3. Restart Factory AI session
exit  # Exit current droid session
droid # Start new session - changes now active
```

### Best Practices

1. **Keep CLAUDE.md focused** - Core instructions only
2. **Document WHY** - Add context for decisions
3. **Test changes** - Restart session to verify
4. **Version control** - Commit shared guidelines
5. **Repository-specific** - Use repo .claude for local customizations

## Multi-Repository Setup

### Workspace-Hub Root

Master configuration at `/mnt/github/workspace-hub/.claude/`:

- Core SPARC methodology
- Agent orchestration patterns
- Coding standards and best practices
- Multi-repository coordination
- HTML reporting standards
- AI agent orchestration system

### Sub-Repositories

Each of 25+ repositories has `.claude/`:

- Inherits workspace-hub standards
- Repository-specific customizations
- Domain-specific guidelines
- Project-specific tools

### Propagation

Setup or update all repositories:

```bash
# Setup .claude in all repos
bash modules/automation/setup_claude_memory_all_repos.sh

# Verify setup
find /mnt/github/workspace-hub -maxdepth 2 -type d -name ".claude" | wc -l
# Should show: 26 (workspace-hub + 25 repos)
```

## Factory AI Variants

### Supported Models

✅ **All Factory AI variants supported:**

- **Claude 3.5 Sonnet** - Default, highest quality
- **GPT-5 Codex** - Specialized coding model
- **GPT-4.1** - Fast, capable
- **Claude 3 Opus** - Maximum context
- **GPT-4** - Stable, reliable

### Model-Agnostic Design

The `.claude` project memory system is **model-agnostic**:

- Same `.claude/CLAUDE.md` file works across all models
- No model-specific configuration needed
- Consistent behavior regardless of agent variant
- Guidelines loaded automatically for all variants

### Switching Models

```bash
# Use default model (Claude 3.5 Sonnet)
droid

# Use GPT-5 Codex
droid --model gpt-5-codex

# Use GPT-4.1
droid --model gpt-4.1

# All variants automatically load .claude/CLAUDE.md
```

## Integration with Other Systems

### Agent OS Integration

`.claude` works alongside Agent OS:

- **Agent OS:** Product planning, specs, tasks
- **Claude Memory:** Session instructions, guidelines, standards

```
.agent-os/product/        # Product context
  ├── mission.md
  ├── tech-stack.md
  ├── roadmap.md
  └── decisions.md

.claude/                  # Session memory
  ├── CLAUDE.md          # Auto-loaded instructions
  └── settings.json      # Session settings
```

### Factory AI Integration

`.drcode` and `.claude` complement each other:

- **`.drcode/config.json`** - Factory AI workspace config
- **`.claude/CLAUDE.md`** - Project instructions and standards

Both automatically loaded when you run `droid`.

### Claude Flow Integration

Works with Claude Flow MCP:

- Claude Flow coordinates swarm topology
- `.claude/CLAUDE.md` provides development standards
- MCP tools + project memory = powerful workflows

## Troubleshooting

### Instructions Not Loading

**Problem:** Changes to `.claude/CLAUDE.md` not taking effect

**Solution:**
```bash
# Exit and restart Factory AI session
exit
droid
```

### File Not Found

**Problem:** `.claude/CLAUDE.md` missing in repository

**Solution:**
```bash
# Re-run setup script
bash /mnt/github/workspace-hub/modules/automation/setup_claude_memory_all_repos.sh
```

### Multiple Configurations

**Problem:** Conflicting instructions between workspace-hub and repo

**Solution:**
- Workspace-hub `.claude/CLAUDE.md` provides base standards
- Repository-specific `.claude/CLAUDE.md` can override
- Later instructions take precedence

### Git Tracking Issues

**Problem:** Session files being committed

**Solution:**
```bash
# Verify .gitignore
grep -A2 "Claude Code project memory" .gitignore

# Should show:
# .claude/settings.local.json
# .claude/checkpoints/
```

## Performance Benefits

With proper `.claude` configuration:

- **84.8% SWE-Bench solve rate**
- **32.3% token reduction** (consistent context)
- **2.8-4.4x speed improvement** (parallel execution)
- **27+ neural models** available

## Command Reference

### Setup Commands

```bash
# Initial setup across all repos
bash modules/automation/setup_claude_memory_all_repos.sh

# Verify .claude directories
find /mnt/github/workspace-hub -maxdepth 2 -type d -name ".claude" | wc -l

# Count CLAUDE.md files
find /mnt/github/workspace-hub -maxdepth 2 -path "*/.claude/CLAUDE.md" | wc -l
```

### Usage Commands

```bash
# Start Factory AI (loads .claude/CLAUDE.md automatically)
droid

# Non-interactive mode
droid exec "your task"

# From stdin
droid exec - < prompt.txt
```

### Maintenance Commands

```bash
# Update all repos
bash modules/automation/setup_claude_memory_all_repos.sh

# Check configuration
ls -lh .claude/

# View current instructions
cat .claude/CLAUDE.md
```

## Resources

### Documentation

- **This file:** `docs/CLAUDE_PROJECT_MEMORY.md`
- **Per-repo:** `.claude/README.md` in each repository
- **Factory AI:** https://docs.factory.ai
- **Claude Code:** https://docs.claude.com/claude-code

### Scripts

- **Setup:** `modules/automation/setup_claude_memory_all_repos.sh`
- **Factory Install:** `modules/automation/install_factory_all_repos.sh`
- **Agent Orchestration:** `modules/automation/agent_orchestrator.sh`

### Related Systems

- **Agent OS:** `.agent-os/` - Product planning system
- **Factory AI:** `.drcode/` - Workspace configuration
- **Claude Flow:** MCP-based orchestration
- **SPARC:** Methodology integration

## Support

- **Factory AI Docs:** https://docs.factory.ai/factory-cli/getting-started/overview
- **Workspace-Hub Issues:** See main README.md
- **Claude Flow:** https://github.com/ruvnet/claude-flow

---

**Remember:** `.claude/CLAUDE.md` is automatically loaded at session start for **all Factory AI variants** including GPT-5 Codex. No manual loading required!
