---
name: hidden-folder-audit-migrate-agent-os-to-claude
description: 'Sub-skill of hidden-folder-audit: Migrate .agent-os to .claude (+4).'
version: 1.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Migrate .agent-os to .claude (+4)

## Migrate .agent-os to .claude


```bash
# Backup first
cp -r .agent-os .agent-os.backup

# Migrate agents
mkdir -p .claude/agents
cp -r .agent-os/agents/* .claude/agents/ 2>/dev/null

# Migrate standards (if applicable)
mkdir -p .claude/standards

*See sub-skills for full details.*

## Migrate .ai to .claude


```bash
# Backup first
cp -r .ai .ai.backup

# Migrate prompts to skills
mkdir -p .claude/skills/prompts
cp -r .ai/prompts/* .claude/skills/prompts/ 2>/dev/null

# Migrate config
cp .ai/config.* .claude/ 2>/dev/null

# Cleanup
git rm -r --cached .ai/ 2>/dev/null
rm -rf .ai
```

## Clean Dead Symlinks


```bash
# Find broken symlinks
find . -maxdepth 2 -type l ! -exec test -e {} \; -print

# Remove broken symlinks
find . -maxdepth 2 -type l ! -exec test -e {} \; -delete

# Remove specific dead symlink folder
rm -rf .agent-runtime
```

## Consolidate Runtime Directories


```bash
# Create standard runtime directory

# Migrate coordination data

# Remove old directories
rm -rf .coordination .session
```

## Update .gitignore


Add these patterns after consolidation:

```gitignore
# Runtime and state (not tracked)
.coordination/
.session/

# Legacy folders (prevent re-creation)
.agent-os/
.ai/

*See sub-skills for full details.*
