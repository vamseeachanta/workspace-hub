---
name: technology-stack-modernization-dependency-management
description: 'Sub-skill of technology-stack-modernization: Dependency Management.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Dependency Management

## Dependency Management

1. **Pin major versions, allow minor updates:**
   ```toml
   # Good: Allows security updates
   dependencies = ["pandas>=2.0.0,<3.0.0"]

   # Bad: Too strict, misses security patches
   dependencies = ["pandas==2.0.0"]
   ```

2. **Test after each major update:**
   - Update one package at a time
   - Run full test suite
   - Check for deprecation warnings
   - Validate outputs

3. **Document breaking changes:**
   ```markdown
