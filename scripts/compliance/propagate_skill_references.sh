#!/bin/bash
# ABOUTME: Propagates skill references and CLAUDE.md template to all repos
# ABOUTME: Ensures repos use on-demand skills instead of embedded docs

# Don't exit on error - handle errors manually
set +e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

WORKSPACE_ROOT="/mnt/github/workspace-hub"
SKILLS_SOURCE="$HOME/.claude/skills"

# Statistics
total=0
updated=0
skipped=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Propagating Skill References to All Repositories          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# CLAUDE.md template with skill references
CLAUDE_TEMPLATE='# Claude Code Configuration

> Uses on-demand skills for detailed guidance. See skills table below.

## Core Rules

1. **TDD Mandatory**: Write failing tests first, then implement
2. **Ask Before Acting**: Clarify ambiguous requirements
3. **Simple Solutions**: Avoid over-engineering
4. **Match Style**: Follow existing code patterns
5. **Fix Bugs Immediately**: When found during work

## Cross-Review Policy

All Claude/Gemini work must be reviewed by Codex (max 3 iterations).
See `cross-review-policy` skill for details.

## On-Demand Skills

Load these when the task requires detailed guidance:

| Need | Skill | When |
|------|-------|------|
| AI workflow rules | `ai-agent-guidelines` | Code review, agent tasks |
| Cross-review process | `cross-review-policy` | Before presenting work |
| Development workflow | `dev-workflow` | YAML/pseudocode/TDD |
| File organization | `file-org-standards` | Creating files/dirs |
| Testing standards | `testing-standards` | Writing tests |
| Logging standards | `logging-standards` | Adding logging |

**Skill path:** `@~/.claude/skills/<category>/<skill-name>/SKILL.md`

## Quick Commands

```bash
# From workspace-hub
./scripts/workspace              # Main CLI
./scripts/repository_sync        # Git operations
```

---
*Skills provide detailed guidance without consuming context. Reference when needed.*
'

# List of repo directories (excluding workspace-hub system dirs)
get_repos() {
    for dir in "$WORKSPACE_ROOT"/*/; do
        [ -d "$dir" ] || continue
        name=$(basename "$dir")
        case "$name" in
            config|coordination|data|dist|docker|docs|ecs|examples|logs|memory|\
            modules|monitoring-dashboard|node_modules|og_knowledge|pyproject|\
            reports|scripts|skills|specs|templates|tests|tools|src|__pycache__|.*)
                continue
                ;;
            *)
                echo "$name"
                ;;
        esac
    done
}

for repo in $(get_repos); do
    total=$((total + 1))
    repo_path="$WORKSPACE_ROOT/$repo"

    echo -e "${BLUE}Processing:${NC} $repo"

    # Skip if not a git repo
    if [ ! -d "$repo_path/.git" ]; then
        echo -e "  ${YELLOW}⊘ Not a git repository - skipping${NC}"
        skipped=$((skipped + 1))
        continue
    fi

    # Create .claude/skills directory
    mkdir -p "$repo_path/.claude/skills"

    # Copy skills from user-level
    if [ -d "$SKILLS_SOURCE/guidelines" ]; then
        cp -r "$SKILLS_SOURCE/guidelines" "$repo_path/.claude/skills/" 2>/dev/null || true
    fi
    if [ -d "$SKILLS_SOURCE/workflows" ]; then
        cp -r "$SKILLS_SOURCE/workflows" "$repo_path/.claude/skills/" 2>/dev/null || true
    fi
    if [ -d "$SKILLS_SOURCE/optimization" ]; then
        cp -r "$SKILLS_SOURCE/optimization" "$repo_path/.claude/skills/" 2>/dev/null || true
    fi
    if [ -d "$SKILLS_SOURCE/product" ]; then
        cp -r "$SKILLS_SOURCE/product" "$repo_path/.claude/skills/" 2>/dev/null || true
    fi
    if [ -d "$SKILLS_SOURCE/meta" ]; then
        cp -r "$SKILLS_SOURCE/meta" "$repo_path/.claude/skills/" 2>/dev/null || true
    fi

    # Create/update CLAUDE.md if it doesn't exist or is small
    claude_file="$repo_path/CLAUDE.md"
    if [ ! -f "$claude_file" ] || [ $(wc -c < "$claude_file" 2>/dev/null || echo 0) -lt 500 ]; then
        echo "$CLAUDE_TEMPLATE" > "$claude_file"
        echo -e "  ${GREEN}✓ Created CLAUDE.md with skill references${NC}"
    else
        echo -e "  ${YELLOW}→ CLAUDE.md exists (preserved)${NC}"
    fi

    # Count skills
    skill_count=$(find "$repo_path/.claude/skills" -name "SKILL.md" 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓ Installed $skill_count skills${NC}"

    updated=$((updated + 1))
    echo ""
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Propagation Summary                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total processed:    ${BLUE}$total${NC}"
echo -e "Successfully updated: ${GREEN}$updated${NC}"
echo -e "Skipped:            ${YELLOW}$skipped${NC}"
echo ""
echo -e "${GREEN}✓ Skill references propagated!${NC}"
