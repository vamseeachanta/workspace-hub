# WRK-1013 Plan — Fix Anthropic Guide Violations

## Objective

Comply with Anthropic official skill guide:
1. Remove README.md from all skill folders (109 violations found)
2. Refactor 6 SKILL.md files exceeding 5,000 words

## Approach

**P1 — Batch-delete README.md files**
- Audit each file for unique content not in SKILL.md
- For skill-creator and similar files: migrate unique content to references/
- Delete all 109 files

**P2 — Refactor oversized SKILL.md files**
For each of the 6 oversized files:
1. Identify bulk content (phase details, API refs, examples, standards tables)
2. Extract to `references/<topic>.md`
3. Replace extracted content with a lean summary + reference pointer
4. Verify SKILL.md < 5,000 words post-refactor

## Files Affected

- `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` → `references/pipeline-detail.md`
- `.claude/skills/data/energy/production-forecaster/SKILL.md` → `references/examples.md`
- `.claude/skills/ai/prompting/pandasai/SKILL.md` → `references/api-reference.md`
- `.claude/skills/_internal/meta/module-based-refactor/SKILL.md` → `references/patterns.md`
- `.claude/skills/engineering/marine-offshore/structural-analysis/SKILL.md` → `references/standards.md`
- `.claude/skills/_diverged/digitalmodel/ai-prompting/pandasai/SKILL.md` → `references/api-reference.md`

## Route A — Simple

No spec file required. Single cross-review pass. Implement → Test → Archive.
