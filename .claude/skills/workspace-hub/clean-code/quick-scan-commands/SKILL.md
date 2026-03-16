---
name: clean-code-quick-scan-commands
description: 'Sub-skill of clean-code: Quick Scan Commands.'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# Quick Scan Commands

## Quick Scan Commands


Run these before reviewing or merging code:

```bash
# Find files exceeding 400-line hard limit
find src/ -name "*.py" -exec wc -l {} + | awk '$1 > 400 {print $1, $2}' | sort -rn | head -20

# Find functions exceeding 50 lines (approximate — counts def blocks)
grep -n "^    def \|^def " src/**/*.py | awk -F: '{print $1, $2}' | head -30

# Oversized files by severity
echo "=== CRITICAL (>1000 lines) ===" && find src/ -name "*.py" -exec wc -l {} + | awk '$1>1000{print}' | sort -rn
echo "=== HIGH (400-1000 lines) ===" && find src/ -name "*.py" -exec wc -l {} + | awk '$1>400 && $1<=1000{print}' | sort -rn

# Dead code: files named *_unused.py or *_old.py
find src/ \( -name "*_unused.py" -o -name "*_old.py" -o -name "*_bak.py" \) | head -20

# Duplicate class names (possible God Object fragmentation)
grep -r "^class " src/ | sed 's/.*class //' | sed 's/[:(].*//' | sort | uniq -d
```

---
