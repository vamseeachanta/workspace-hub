---
name: compliance-check-install-compliance-hooks
description: 'Sub-skill of compliance-check: Install Compliance Hooks (+2).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Install Compliance Hooks (+2)

## Install Compliance Hooks


```bash
./scripts/compliance/install_compliance_hooks.sh
```

## Pre-commit Hook Checks


The pre-commit hook verifies:

1. **File organization**: No files in wrong locations
2. **Test coverage**: Coverage report exists and meets threshold
3. **Linting**: No syntax errors
4. **YAML validation**: Valid YAML configuration
5. **Documentation**: Required docs exist

## Hook Configuration


```bash
# .git/hooks/pre-commit

#!/bin/bash
set -e

echo "Running compliance checks..."

# Check file organization
./scripts/compliance/check_file_org.sh

*See sub-skills for full details.*
