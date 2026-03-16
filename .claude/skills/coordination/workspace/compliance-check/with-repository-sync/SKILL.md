---
name: compliance-check-with-repository-sync
description: 'Sub-skill of compliance-check: With Repository Sync (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# With Repository Sync (+2)

## With Repository Sync


```bash
# After pulling, verify compliance
./scripts/repository_sync pull all
./scripts/compliance/verify_compliance.sh
```

## With AI Agents


AI agents should:
1. Check compliance status before making changes
2. Maintain compliance during modifications
3. Report compliance issues found during work
4. Follow guidelines in CLAUDE.md

## Related Skills


- [repo-sync](../repo-sync/SKILL.md) - Repository management
- [sparc-workflow](../sparc-workflow/SKILL.md) - Development methodology
- [workspace-cli](../workspace-cli/SKILL.md) - Unified CLI interface
