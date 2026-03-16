---
name: technology-stack-modernization-current-state
description: 'Sub-skill of technology-stack-modernization: Current State (+3).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Current State (+3)

## Current State


- **Version:** [current_version]
- **Usage:** [where/how it's used]
- **Issues:** [any known problems]

## Update Plan


- **Target Version:** [target_version]
- **Breaking Changes:** [yes/no - list if yes]
- **Migration Steps:**
  1. [step 1]
  2. [step 2]
  3. [step 3]

## Testing Plan


- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance benchmarks within acceptable range

## Rollback Plan


If update fails:
1. Revert pyproject.toml changes
2. Reinstall previous version: `uv pip install [package]==[old_version]`
3. Document issue for future reference
```
