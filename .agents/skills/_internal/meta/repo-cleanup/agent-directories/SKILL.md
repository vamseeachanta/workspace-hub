---
name: repo-cleanup-agent-directories
description: 'Sub-skill of repo-cleanup: Agent Directories (+4).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Agent Directories (+4)

## Agent Directories


Multiple agent-related directories should consolidate to `.claude/agents/`.

**Before:**
```
root/
├── agents/
├── .agents/
├── agent_configs/
└── .agent-os/
```

*See sub-skills for full details.*

## Runtime/Coordination Data


- Session state files
- Coordination lock files
- Runtime cache
- Worker state

**Commands:**
```bash
# Create runtime directory

# Move runtime files (don't use git mv - these are untracked)
```

## Prototype Code


Prototype and experimental code should go to `examples/prototypes/`.

**Commands:**
```bash
mkdir -p examples/prototypes
git mv prototype_*.py examples/prototypes/
git mv experimental/ examples/prototypes/
```

## Test Outputs


Test output files should go to `tests/outputs/` (gitignored).

**Commands:**
```bash
mkdir -p tests/outputs
mv tests/*.html tests/outputs/
mv tests/*.json tests/outputs/
mv tests/test_results/ tests/outputs/
```

## Plan Files


Completed specification plans should be archived.

**Pattern:**
- Active plans: `specs/modules/<plan>.md`
- Completed plans: `specs/archive/<plan>.md`

**Commands:**
```bash
# Archive completed plan (check status: completed in YAML frontmatter)
mkdir -p specs/archive
git mv specs/modules/<completed-plan>.md specs/archive/
```
