---
name: core-reviewer-be-constructive
description: 'Sub-skill of core-reviewer: Be Constructive (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Be Constructive (+3)

## Be Constructive

- Focus on the code, not the person
- Explain why something is an issue
- Provide concrete suggestions
- Acknowledge good practices


## Consider Context

- Development stage
- Time constraints
- Team standards
- Technical debt


## Automate When Possible

```bash
# Run automated tools before manual review
npm run lint
npm run test
npm run security-scan
npm run complexity-check
```


## Review Guidelines

1. **Review Early and Often**: Don't wait for completion
2. **Keep Reviews Small**: <400 lines per review
3. **Use Checklists**: Ensure consistency
4. **Automate When Possible**: Let tools handle style
5. **Learn and Teach**: Reviews are learning opportunities
6. **Follow Up**: Ensure issues are addressed
