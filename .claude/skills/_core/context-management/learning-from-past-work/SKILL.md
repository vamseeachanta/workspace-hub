---
name: core-context-management-learning-from-past-work
description: 'Sub-skill of core-context-management: Learning from Past Work (+2).'
version: 1.0.0
category: _core
type: reference
scripts_exempt: true
---

# Learning from Past Work (+2)

## Learning from Past Work


The skill tracks patterns across sessions:

```yaml
# .claude/state/context-patterns.yaml
patterns:
  frequently_referenced:
    - ".claude/docs/agents.md"  # 45 loads
    - ".claude/docs/execution-patterns.md"  # 32 loads
  rarely_used:
    - "verbose section X"  # 0 references in 30 days

*See sub-skills for full details.*

## Daily Analysis Tasks


1. **Size Check**: Validate all CLAUDE.md files against limits
2. **Pattern Analysis**: Analyze git commits for instruction patterns
3. **Usage Tracking**: Check which docs were loaded
4. **Suggestion Generation**: Create improvement proposals
5. **Report Generation**: Output daily health report

## Improvement Workflow


```
1. Validate sizes → Report violations
2. Analyze patterns → Identify redundancy
3. Check usage → Find unused content
4. Generate suggestions → Propose changes
5. Apply approved changes → Update files
6. Commit → Track improvements
```

---
