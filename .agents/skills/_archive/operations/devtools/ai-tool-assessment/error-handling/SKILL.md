---
name: ai-tool-assessment-error-handling
description: 'Sub-skill of ai-tool-assessment: Error Handling.'
version: 2.0.0
category: operations
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Issues


**Error: Missing subscription data**
- Cause: `docs/AI_development_tools.md` not found or outdated
- Solution: Ask user for current subscription list, create/update doc

**Error: Incomplete usage data**
- Cause: User unsure about usage patterns
- Solution: Suggest tracking usage for 2 weeks before full assessment

**Error: Can't determine value**
- Cause: Tool usage overlaps with others
- Solution: Run overlap analysis first, identify unique value per tool

**Error: Outdated pricing**
- Cause: Subscription costs changed
- Solution: Verify current pricing on vendor websites
