---
name: skill-creator-file-structure
description: 'Sub-skill of skill-creator: File Structure (+1).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# File Structure (+1)

## File Structure


```
.claude/skills/
└── skill-name/            # kebab-case only (no underscores, spaces, capitals)
    ├── SKILL.md           # Required: exactly "SKILL.md" (case-sensitive)
    ├── scripts/           # Optional: executable code (Python, Bash, etc.)
    ├── references/        # Optional: documentation loaded as needed
    └── assets/            # Optional: templates, fonts, icons used in output
```

**Critical rules (from Anthropic guide):**
- `SKILL.md` must be named exactly `SKILL.md` — no variations (SKILL.MD, skill.md, etc.)
- NO `README.md` inside the skill folder — all docs go in SKILL.md or references/
- Folder name must be kebab-case only (no underscores, no capitals, no spaces)
- Keep SKILL.md under 5,000 words — move detailed docs to references/ and link to them
- Do NOT use "claude" or "anthropic" in skill name (reserved)

## SKILL.md Structure


```markdown
---
name: skill-name
description: One-line description of what this skill does and when to use it.
version: 1.0.0
category: builders
last_updated: 2026-01-02
tags: [discovery-keyword, tool-name, use-case]        # optional, free-form
related_skills:                                        # optional, by skill name
  - related-skill-1
  - related-skill-2
---

# Skill Title
