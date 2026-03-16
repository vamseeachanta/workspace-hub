---
name: compliance-check-common-compliance-failures
description: 'Sub-skill of compliance-check: Common Compliance Failures (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Common Compliance Failures (+2)

## Common Compliance Failures


| Issue | Cause | Resolution |
|-------|-------|------------|
| Structure violation | Files in wrong directory | Move files to correct location |
| Low test coverage | Insufficient tests | Add unit/integration tests |
| Static images | matplotlib exports | Convert to Plotly/Bokeh HTML |
| Missing CLAUDE.md | New repo setup | Run propagation script |
| Hook not running | Permission issue | `chmod +x .git/hooks/pre-commit` |

## Fixing Non-Compliance


#### Structure Issues

```bash
# Create missing directories
mkdir -p src tests docs config scripts data reports logs

# Move misplaced files
git mv root_file.py src/
git mv old_tests.py tests/unit/
```

*See sub-skills for full details.*

## Troubleshooting


#### Hook Not Running

```bash
# Make hook executable
chmod +x .git/hooks/pre-commit

# Check hook exists
ls -la .git/hooks/pre-commit
```


*See sub-skills for full details.*
