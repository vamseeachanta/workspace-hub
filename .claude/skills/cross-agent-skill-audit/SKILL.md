---
name: cross-agent-skill-audit
version: 1.0.0
category: coordination
description: Audit and fix skill accessibility across all 4 agents (Hermes, Claude Code, Codex CLI, Gemini CLI). Identifies gaps in symlink wiring, external_dirs, and per-repo routing.
tags: [skills, audit, multi-agent, codex, gemini, hermes, claude-code, harness]
---

# Cross-Agent Skill Audit

## When to Use

- User reports a skill isn't visible to one or more agents
- After migrating skills between locations (~/.hermes/ vs .claude/)
- When adding a new repo to the workspace
- After hermes update or harness-update to verify nothing broke

## Architecture Overview

All 4 agents access skills through different mechanisms:

```
Hermes:         external_dirs in ~/.hermes/config.yaml (reads 6 repos' .claude/skills/)
Claude Code:    .claude/skills/ (native, on-demand via slash commands)
Codex CLI:      .codex/skills/ → symlink → ../.claude/skills/
Gemini CLI:     .gemini/skills/ → symlink → ../.claude/skills/
```

Per-repo: each repo that has agents must have `.codex/skills` and `.gemini/skills` symlinks pointing to `../../.claude/skills`.

## Audit Procedure

### Step 1: Count skills per agent

```bash
WS=/mnt/local-analysis/workspace-hub

# Claude Code (native .claude/skills/)
echo "CC: $(find -L $WS/.claude/skills -name 'SKILL.md' -not -path '*/_archive/*' | wc -l)"

# Codex (symlink → .claude/)
echo "Codex: $(find -L $WS/.codex/skills -name 'SKILL.md' -not -path '*/_archive/*' | wc -l)"

# Gemini (symlink → .claude/)
echo "Gemini: $(find -L $WS/.gemini/skills -name 'SKILL.md' -not -path '*/_archive/*' | wc -l)"

# Hermes (external_dirs)
grep -A7 'external_dirs' ~/.hermes/config.yaml | grep '.claude/skills' | wc -l
echo "(count of external_dirs paths)"
```

Expected: All three symlink agents should show the same count. A mismatch means broken symlink or real directory takeover.

### Step 2: Verify symlink integrity

```bash
# Check if .codex/skills is a symlink (NOT a real directory)
test -L $WS/.codex/skills && echo "OK: symlink" || echo "BROKEN: real dir or missing"
test -L $WS/.gemini/skills && echo "OK: symlink" || echo "BROKEN: real dir or missing"

# Check per-repo symlinks
for repo in CAD-DEVELOPMENTS digitalmodel worldenergydata achantas-data assetutilities; do
  if [ -d "$WS/$repo/.codex" ]; then
    target=$(readlink "$WS/$repo/.codex/skills" 2>/dev/null || echo "MISSING")
    echo "  $repo/.codex/skills → $target"
  fi
done
```

### Step 3: Check external_dirs coverage

```bash
for d in $(grep 'external_dirs' ~/.hermes/config.yaml -A10 | grep '.claude/skills' | sed 's/.*- //'); do
  count=$(find -L "$d" -name 'SKILL.md' -not -path '*/_archive/*' | wc -l 2>/dev/null)
  label=$(basename $(dirname $(dirname "$d")))
  echo "  $label: $count skills"
done
```

### Step 4: Check for local-only skills

```bash
# Any skills left in ~/.hermes/skills/ not covered by external_dirs?
find ~/.hermes/skills -name 'SKILL.md' 2>/dev/null | while read f; do
  echo "  LOCAL ONLY: $f"
done
```

Expected: 0 results. Any local skills should be migrated to repo .claude/skills/.

## Common Fixes

### Fix 1: .codex/skills is a real directory instead of symlink

```bash
cd $WS
# Verify all 57 GSD skills exist in .claude/skills/ first
mv .codex/skills .codex/skills.bak
ln -s ../.claude/skills .codex/skills
rm -rf .codex/skills.bak  # after verification
git add .codex/skills
git commit -m "fix(codex): replace .codex/skills real dir with symlink"
```

### Fix 2: Missing per-repo symlinks

```bash
cd $WS/GEMINI-REPO
rm -rf .codex/skills 2>/dev/null
rm -rf .gemini/skills 2>/dev/null
ln -s ../../.claude/skills .codex/skills
ln -s ../../.claude/skills .gemini/skills
git add .codex/skills .gemini/skills
git commit -m "feat(harness): add .codex/.gemini symlinks for GEMINI-REPO"
```

### Fix 3: Hermes external_dirs missing a repo

Edit `~/.hermes/config.yaml`:
```yaml
skills:
  external_dirs:
    - /path/to/repo/.claude/skills  # ADD missing repo here
```
Then run: `scripts/_core/sync-agent-configs.sh`

### Fix 4: Skills in ~/.hermes/skills/ not migrated to repo

```bash
# Preferred: use the backfill script (handles per-repo routing, legal scan, commit, push)
bash scripts/hermes/backfill-skills-to-repo.sh --commit

# Manual alternative: copy skill to repo .claude/skills/ then delete local copy
cp -r ~/.hermes/skills/CAT/NAME/ .claude/skills/CAT/NAME/
git add .claude/skills/CAT/NAME/
git commit -m "feat(skills): migrate CAT/NAME from ~/.hermes/skills/"
rm -rf ~/.hermes/skills/CAT/
```

Note: after migration, ~/.hermes/skills/ should end up with 0 SKILL.md files.
Empty category dirs can be cleaned with:
```bash
find ~/.hermes/skills -mindepth 1 -maxdepth 1 -type d -empty -delete
```

## Pitfalls

1. **find without -L doesn't follow symlinks**: Always use `find -L` when counting skills through `.codex/skills` or `.gemini/skills`. Plain `find` returns 0 for symlinked directories.

2. **Codex symlink takeover**: A common bug where `.codex/skills` somehow becomes a real directory (e.g., from a git checkout that dereferences symlinks). Always check with `test -L`.

3. **Per-repo vs workspace-hub access**: When Codex/Gemini work inside a sub-repo (e.g., CAD-DEVELOPMENTS/), their symlinks point to `../../.claude/skills` which is the sub-repo's local skills only. They do NOT automatically see workspace-hub canonical skills. This is by design to limit context budget.

4. **external_dirs path changes**: If workspace-hub moves to a different path, update `__WS_HUB_PATH__` in `config/agents/hermes/config.yaml.template` and re-run `sync-agent-configs.sh`.

5. **_archive directory**: The 2166 archived skills in workspace-hub `.claude/skills/` should NOT be counted. Always exclude with `-not -path '*/_archive/*'`.

6. **Empty category dirs in ~/.hermes/skills/**: After migration, empty dirs remain. Clean with: `find ~/.hermes/skills -mindepth 1 -maxdepth 1 -type d -empty -delete`

## Validation Checklist

After any change to the skill ecosystem:
- [ ] CC count = Codex count = Gemini count (workspace-hub baseline)
- [ ] .codex/skills is a symlink (test -L)
- [ ] .gemini/skills is a symlink (test -L)
- [ ] 0 skills in ~/.hermes/skills/ (find returns nothing)
- [ ] All 6 external_dirs paths exist in config.yaml
- [ ] hermes skills_list shows expected count
- [ ] skill_view <known-skill> works for both Hermes and CC
- [ ] git status clean (no unstaged symlink changes)
