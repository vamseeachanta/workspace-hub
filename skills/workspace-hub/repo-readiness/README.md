# Repository Readiness Skill

> Automatically prepare repositories for new work by analyzing configuration, structure, mission, and establishing complete work context.

## Overview

The repo-readiness skill performs comprehensive analysis of any repository to establish complete work context before executing new tasks. It replaces manual context gathering with automated, systematic preparation.

### What It Does

1. **Analyzes Configuration**: CLAUDE.md, .agent-os/, MCP settings
2. **Assesses Structure**: Directory organization, modules, naming conventions
3. **Extracts Mission**: Project objectives, technical stack, decisions
4. **Checks State**: Git status, environment setup, dependencies
5. **Validates Standards**: Logging, testing, reporting compliance
6. **Generates Report**: Comprehensive readiness assessment with recommendations

### Readiness Levels

- **✅ READY (90-100%)**: Safe to proceed with new work
- **⚠️ NEEDS ATTENTION (70-89%)**: Can proceed with caution, minor issues
- **❌ NOT READY (<70%)**: Critical issues, must resolve first

## Quick Start

### 1. Check Single Repository

```bash
# From skill directory
./check_readiness.sh /path/to/repository

# Or from repository
cd /path/to/repository
~/.claude/skills/workspace-hub/repo-readiness/check_readiness.sh .
```

### 2. Check All Repositories

```bash
# From skill directory
./bulk_readiness_check.sh

# View summary report
cat /mnt/github/workspace-hub/.claude/bulk-readiness-report.md
```

### 3. Install Hook (Single Repo)

```bash
# Install pre-task hook
./install_hook.sh /path/to/repository

# Test hook
cd /path/to/repository
./.claude/hooks/pre-task.sh
```

### 4. Install Hooks (All Repos)

```bash
# Deploy to all workspace-hub repositories
./bulk_install_hooks.sh
```

## Files

```
repo-readiness/
├── SKILL.md                      # Full skill documentation
├── README.md                     # This file
├── check_readiness.sh            # Single repo readiness check
├── bulk_readiness_check.sh       # All repos readiness check
├── install_hook.sh               # Install hook to single repo
└── bulk_install_hooks.sh         # Install hooks to all repos
```

## Usage Patterns

### Manual Check Before Work

```bash
# Check readiness
./check_readiness.sh ~/projects/my-repo

# Review report
cat ~/projects/my-repo/.claude/readiness-report.md

# Proceed if ready
cd ~/projects/my-repo
# ... start work ...
```

### Automated via Hook

```bash
# Hook auto-executes before tasks
cd ~/projects/my-repo
/create-spec "new feature"

# Hook runs automatically:
# 1. Checks readiness
# 2. Prompts if issues found
# 3. Proceeds or blocks based on severity
```

### Weekly Health Check

```bash
# Check all repositories
./bulk_readiness_check.sh > weekly-report-$(date +%Y-%m-%d).txt

# Review summary
cat /mnt/github/workspace-hub/.claude/bulk-readiness-report.md

# Address issues in repos needing attention
```

### CI/CD Integration

```yaml
# .github/workflows/readiness-check.yml
name: Repository Readiness

on: [push, pull_request]

jobs:
  readiness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check readiness
        run: |
          bash ./.claude/skills/repo-readiness/check_readiness.sh .
          if [ $? -eq 2 ]; then
            echo "Critical readiness issues detected"
            exit 1
          fi
```

## Hook Configuration

### Hook Behavior

After installing hooks, configure in `.claude/hooks/config.sh`:

```bash
# Auto-execute readiness check before tasks
AUTO_READINESS_CHECK=1

# Cache duration (seconds)
READINESS_CACHE_DURATION=3600

# Minimum readiness score to proceed
MINIMUM_READINESS_SCORE=70

# Action on low readiness
# "prompt" = ask user, "block" = prevent, "warn" = show warning but proceed
LOW_READINESS_ACTION="prompt"
```

### Bypassing Hook

```bash
# Skip readiness check for urgent work
SKIP_READINESS_CHECK=1 /execute-tasks "urgent fix"

# Or disable temporarily
cd ~/projects/my-repo
mv .claude/hooks/pre-task.sh .claude/hooks/pre-task.sh.disabled
```

## Interpreting Reports

### Configuration Section

```
✅ Root CLAUDE.md found
✅ Extended CLAUDE.md found
✅ Agent OS configuration found
⚠️ No MCP configuration found

Configuration Score: 75/100
```

**Action**: If MCP integration needed, create `.claude.json` or `.mcp.json`

### Structure Section

```
✅ src/ directory present
✅ tests/ directory present
⚠️ docs/ directory missing
⚠️ config/ directory missing

Structure Score: 60/100
```

**Action**: Create missing directories per FILE_ORGANIZATION_STANDARDS.md

### Mission Section

```
✅ Mission defined
⚠️ Tech stack not documented
⚠️ Roadmap not defined

Mission Score: 30/100
```

**Action**: Document tech stack and roadmap in `.agent-os/product/`

### State Section

```
✅ Git working directory clean
✅ Virtual environment detected
⚠️ Out of sync: 0 ahead, 3 behind

State Score: 70/100
```

**Action**: Pull latest changes: `git pull`

### Standards Section

```
✅ Logging implementation detected
✅ pytest configured
⚠️ Coverage configuration not found

Standards Score: 65/100
```

**Action**: Add `.coveragerc` or coverage config to `pyproject.toml`

## Troubleshooting

### Script Not Executable

```bash
chmod +x check_readiness.sh
chmod +x bulk_readiness_check.sh
chmod +x install_hook.sh
chmod +x bulk_install_hooks.sh
```

### Cache Issues

```bash
# Force refresh (ignore cache)
FORCE_REFRESH=1 ./check_readiness.sh /path/to/repo

# Clear cache
rm /path/to/repo/.claude/.readiness-cache
```

### Hook Not Triggering

```bash
# Verify hook installed
ls -la .claude/hooks/pre-task.sh

# Make executable
chmod +x .claude/hooks/pre-task.sh

# Test manually
./.claude/hooks/pre-task.sh
```

### False Positives

If readiness check incorrectly reports issues:

1. Review `.claude/readiness-report.md` for details
2. Check if repository follows workspace-hub standards
3. Update standards if repository has valid alternate structure
4. File issue if bug in readiness logic

## Best Practices

### 1. Run Before Starting Work

```bash
# Always check readiness first
./check_readiness.sh ~/projects/my-repo

# Then start work
cd ~/projects/my-repo
# ... work ...
```

### 2. Install Hooks on All Repos

```bash
# One-time setup
./bulk_install_hooks.sh

# Hooks auto-check from then on
```

### 3. Weekly Bulk Checks

```bash
# Schedule weekly
crontab -e

# Add:
0 9 * * 1 /path/to/bulk_readiness_check.sh > ~/weekly-readiness.txt
```

### 4. Address Issues Promptly

Don't ignore warnings - fix them before they become blockers.

### 5. Update Configuration as Needed

Keep CLAUDE.md, mission.md, and other configs current.

## Integration

### With Claude Code Skills

```bash
# In skill invocation
/repo-readiness → analyze → /create-spec "feature"
```

### With SPARC Workflow

```bash
# Before each phase
/repo-readiness
/sparc-specification "feature"
# ... readiness re-checked automatically ...
/sparc-implementation
```

### With Compliance Check

```bash
# Combined health validation
./check_readiness.sh . && ~/scripts/compliance-check.sh .
```

## Metrics

Track readiness over time:

```bash
# Generate weekly reports
./bulk_readiness_check.sh > reports/readiness-$(date +%Y-%m-%d).txt

# Monitor trends
# - Increase in ready repos = good
# - Decrease in not ready repos = good
# - Stable high percentage = excellent
```

## Support

- **Skill Documentation**: [SKILL.md](SKILL.md)
- **Workspace Hub Docs**: [/docs/README.md](../../../../docs/README.md)
- **Standards**: [/docs/modules/standards/](../../../../docs/modules/standards/)
- **Development Workflow**: [/docs/modules/workflow/DEVELOPMENT_WORKFLOW.md](../../../../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-07
**Category**: workspace-hub
