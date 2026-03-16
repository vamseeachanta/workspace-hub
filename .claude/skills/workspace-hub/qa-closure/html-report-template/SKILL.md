---
name: qa-closure-html-report-template
description: 'Sub-skill of qa-closure: HTML Report Template.'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# HTML Report Template

## HTML Report Template


The `generate-qa-report.sh` script produces a self-contained HTML file using
this structure. All CSS is inline; no external dependencies.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>QA Report — WRK-NNN</title>
  <!-- Inline CSS: dark header, section cards, verdict badge -->
</head>
<body>
  <header>WRK-NNN · <title> · <date></header>
  <section id="s1"><!-- Inputs --></section>
  <section id="s2"><!-- Process log --></section>
  <section id="s3"><!-- Outputs --></section>
  <section id="s4"><!-- QA checks --></section>
  <section id="s5" class="verdict PASS|WARN|FAIL"><!-- Verdict --></section>
</body>
</html>
```

---
