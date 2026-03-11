# WRK-1084 Plan: Integrate skills.sh as Canonical Reference

## Context

skills.sh (https://skills.sh/) is an open ecosystem for reusable AI agent skills. The
workspace-hub already adopts skills from there (superpowers/*, frontend-design) but the
skill curation workflows (skill-learner, skills-curation, skills-researcher) do not
reference skills.sh as a source during research phases. This creates drift risk — new
skills.sh patterns go unnoticed.

## Scope (Simple / Route A)

Three files to modify + one skill to adopt from skills.sh.

## Implementation Steps

### Step 1 — skill-learner/SKILL.md: add external reference section

File: `.claude/skills/coordination/workspace/skill-learner/SKILL.md`

After the `## Prerequisites` section, add:

```markdown
## External Reference: skills.sh

During any skill lifecycle operation (assess, analyze, learn, prune, curate), consult
https://skills.sh/ as the primary external source for proven patterns:

- Browse leaderboard for high-install skills in relevant domains
- `npx skillsadd <owner/repo>` to install and inspect a skill locally
- GitHub source for top skills: obra/superpowers, anthropics/skills, wshobson/agents
- Cross-reference before creating net-new skills — prefer adoption + adaptation over invention
```

### Step 2 — skills-curation/SKILL.md: wire skills.sh into online research phase

File: `.claude/skills/coordination/workspace/skills-curation/SKILL.md`

In the online research section, add skills.sh as the primary external source with:
- leaderboard URL
- install command
- GitHub source repos
- adoption vs invention preference

### Step 3 — skills-researcher/SKILL.md: same addition to Phase 3 Online Research

File: `.claude/skills/coordination/workspace/skills-researcher/SKILL.md`

At line ~97 (Phase 3 step 2 — research recent developments), prepend:
"Check https://skills.sh/ first for existing proven implementations before web searching."

### Step 4 — Adopt one skill from skills.sh (AC2)

Fetch `wshobson/agents` `code-review-excellence` skill from GitHub and compare to
workspace-hub's existing cross-review skill. Incorporate any novel patterns (e.g.,
review rubric, severity matrix) into `.claude/skills/coordination/core/core-reviewer/SKILL.md`
or create a new note in the skills-curation skill.

If GitHub fetch fails, enhance `skills-curation/SKILL.md` with a dedicated
"skills.sh Adoption Workflow" section that codifies the adoption process itself
(browse → inspect → diff against existing → adopt/adapt/skip).

## Verification

```bash
grep -n "skills.sh" .claude/skills/coordination/workspace/skill-learner/SKILL.md
grep -n "skills.sh" .claude/skills/coordination/workspace/skills-curation/SKILL.md
grep -n "skills.sh" .claude/skills/coordination/workspace/skills-researcher/SKILL.md
```

All three should return matches. At least one skill adoption change should be present.

## Files Modified

1. `.claude/skills/coordination/workspace/skill-learner/SKILL.md`
2. `.claude/skills/coordination/workspace/skills-curation/SKILL.md`
3. `.claude/skills/coordination/workspace/skills-researcher/SKILL.md`
4. One of: `core-reviewer/SKILL.md` or `skills-curation/SKILL.md` (adoption section)
