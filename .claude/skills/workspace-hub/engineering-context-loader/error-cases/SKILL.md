---
name: engineering-context-loader-error-cases
description: 'Sub-skill of engineering-context-loader: Error Cases.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Error Cases

## Error Cases


| Situation | Behavior |
|-----------|----------|
| No `tags:` in WRK frontmatter | Warn and return full catalog hint |
| Tags present but no domain match | List unmatched tags; no skill subset emitted |
| WRK file not found at any path | Ask user to provide WRK ID or file path |
| Skill path does not exist on disk | Note as "skill not found — may be planned" |
| Multiple domains detected | Output union of all matched skills + codes |
