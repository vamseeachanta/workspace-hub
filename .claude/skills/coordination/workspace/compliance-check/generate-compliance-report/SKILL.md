---
name: compliance-check-generate-compliance-report
description: 'Sub-skill of compliance-check: Generate Compliance Report (+1).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# Generate Compliance Report (+1)

## Generate Compliance Report


```bash
./scripts/compliance/generate_report.sh > reports/compliance_report.html
```

## Report Template


```html
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Report</title>
    <style>
        .pass { color: green; }
        .fail { color: red; }
        .warn { color: orange; }
    </style>

*See sub-skills for full details.*
