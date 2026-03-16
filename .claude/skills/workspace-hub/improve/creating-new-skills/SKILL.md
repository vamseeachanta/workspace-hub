---
name: improve-creating-new-skills
description: 'Sub-skill of improve: Creating New Skills (+3).'
version: 1.4.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Creating New Skills (+3)

## Creating New Skills

1. Search `.claude/skills/**/*.md` for existing coverage
2. If no match, create at `.claude/skills/<category>/<subcategory>/<name>/SKILL.md`
3. Follow existing SKILL.md template (YAML frontmatter + markdown sections)
4. Mark as `auto_generated: true` in frontmatter
5. Log in changelog with source pattern evidence


## Enhancing Existing Skills

1. Read current SKILL.md
2. Identify section to update (Quick Reference, examples, error handling)
3. Apply surgical edit (append examples, fix instructions)
4. Bump patch version in frontmatter
5. Log enhancement in changelog


## Deprecating Skills

1. Verify: no usage in last 90 days (check session logs, git history)
2. Verify: superseded by another skill (identify replacement)
3. Add to frontmatter: `deprecated: true`, `deprecated_date`, `replacement_skill`
4. Do NOT delete — archive in next pass


## Archiving Skills

1. Move from `.claude/skills/<category>/` to `.claude/skills/_archive/<category>/`
2. Add archive metadata: `archive_date`, `reason`, `original_path`
3. Update any cross-references in other skills
