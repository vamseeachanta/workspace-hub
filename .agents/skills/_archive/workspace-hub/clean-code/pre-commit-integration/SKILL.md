---
name: clean-code-pre-commit-integration
description: 'Sub-skill of clean-code: Pre-commit Integration.'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# Pre-commit Integration

## Pre-commit Integration


Add to `.pre-commit-config.yaml` to catch new violations before they land:

```yaml
repos:
  - repo: local
    hooks:
      - id: file-size-check
        name: Python file size check (400 line limit)
        language: system
        entry: bash -c 'find src/ -name "*.py" -exec wc -l {} + | awk "$1 > 400 {print $1, $2; found=1} END {exit found+0}" | sort -rn'
        pass_filenames: false
        types: [python]

      - id: validate-file-placement
        name: Validate file placement
        language: system
        entry: bash scripts/operations/validate-file-placement.sh
        pass_filenames: false
```

---
