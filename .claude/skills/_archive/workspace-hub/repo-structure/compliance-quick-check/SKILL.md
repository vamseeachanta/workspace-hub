---
name: repo-structure-compliance-quick-check
description: 'Sub-skill of repo-structure: Compliance Quick-Check.'
version: 1.4.0
category: workspace
type: reference
scripts_exempt: true
---

# Compliance Quick-Check

## Compliance Quick-Check


Run against any repo before and after structural changes. For automated enforcement, use `scripts/operations/validate-file-placement.sh`.

```bash
# 1. No orphaned dirs at src/ root (non-package dirs)
ls src/ | grep -v "^$(basename $(pwd | sed 's/-/_/g'))$"

# 2. Every package dir has __init__.py
find src/ -type d | while read d; do
  [ -f "$d/__init__.py" ] || echo "MISSING __init__.py: $d"
done

# 3. No loose .py at repo root
ls *.py 2>/dev/null && echo "WARNING: loose .py files at root"

# 4. pytest.ini has pythonpath
grep -q "pythonpath" pytest.ini && echo "OK" || echo "MISSING pythonpath in pytest.ini"

# 5. Windows path artifacts (backslash dirs)
ls | grep '\\' && echo "WARNING: Windows-path directory artifacts found"

# 6. agent-os still present
[ -d ".agent-os" ] && echo "WARNING: .agent-os/ vestigial — delete"

# 7. Tests inside src/ (FAIL)
find src/ -name "test_*.py" -o -name "*_test.py" | grep -v __pycache__

# 8. Committed output artifacts at root (FAIL)
git ls-files | grep -E '^(report_.*\.(xlsx|csv)|test_export.*\.json|COVERAGE_ANALYSIS\.txt|verdict\.txt)$'

# 9. Agent harness files in docs/ (WARN)
ls docs/ | grep -iE '^(AGENT_OS|MANDATORY_SLASH|AI_AGENT_ORCHESTRATION)' 2>/dev/null

# 10. Legacy setup.py alongside pyproject.toml (WARN)
[ -f setup.py ] && [ -f pyproject.toml ] && echo "WARNING: setup.py is superseded by pyproject.toml — remove it"
```

---

---
