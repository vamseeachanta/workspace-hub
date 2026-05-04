---
name: pytest-fixture-generator-best-practices
description: 'Sub-skill of pytest-fixture-generator: Best Practices.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Use markers consistently** - All tests should have at least one marker
2. **Minimize fixture scope** - Use function scope unless sharing is needed
3. **Keep fixtures focused** - One purpose per fixture
4. **Document fixtures** - Add docstrings explaining usage
5. **Use tmp_path** - For temporary files (auto-cleaned)
