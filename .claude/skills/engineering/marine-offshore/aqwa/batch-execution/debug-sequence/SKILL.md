---
name: aqwa-batch-execution-debug-sequence
description: 'Sub-skill of aqwa-batch-execution: Debug Sequence.'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Debug Sequence

## Debug Sequence


```bash
# Step 1 — check license
echo "License: $ANSYSLMD_LICENSE_FILE"
lmstat -a -c $ANSYSLMD_LICENSE_FILE 2>/dev/null | grep -i aqwa

# Step 2 — run with all output captured
${AQWA_EXE} std analysis 2>&1 | tee analysis.run.log

# Step 3 — triage .MES (most informative)
cat analysis.mes

# Step 4 — scan .LIS for fatal lines
grep -n "FATAL\|ERROR\|STOP\|WARNING" analysis.lis | head -40

# Step 5 — confirm panel count echo
grep "TOTAL NUMBER OF PANELS" analysis.lis
```
