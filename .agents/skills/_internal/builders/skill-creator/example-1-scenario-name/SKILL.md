---
name: skill-creator-example-1-scenario-name
description: 'Sub-skill of skill-creator: Example 1: [Scenario Name] (+1).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Example 1: [Scenario Name] (+1)

## Example 1: [Scenario Name]


**Input:** [What user provides]

**Process:** [What skill does]

**Output:** [What user receives]

\`\`\`
// Complete working example
\`\`\`
```


## Step 4: Add Supporting Materials


If needed, create supporting directories:

```
skill-name/
├── SKILL.md
├── references/            # documentation, guides, API references
│   └── api-patterns.md
├── scripts/               # executable scripts
│   └── validate.sh
└── assets/                # templates, fonts, icons
    └── report-template.md
```

Reference them in SKILL.md:
```markdown
Before writing queries, consult `references/api-patterns.md` for:
- Rate limiting guidance
- Pagination patterns
```
