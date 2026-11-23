---
name: web-artifacts-builder
description: Build self-contained interactive web applications as single HTML files.
  Use for creating demos, prototypes, interactive tools, and standalone web experiences
  that work without external servers.
version: 2.0.0
category: _internal
last_updated: 2026-01-02
related_skills:
- frontend-design
- algorithmic-art
- theme-factory
tags: []
see_also:
- web-artifacts-builder-self-contained-architecture
- web-artifacts-builder-basic-template
- web-artifacts-builder-1-interactive-dashboard
- web-artifacts-builder-common-cdn-libraries
- web-artifacts-builder-file-naming
---

# Web Artifacts Builder

## Overview

Create self-contained, interactive web applications as single HTML files. These artifacts require no server, no build process, and can be shared as standalone files that run in any modern browser.

## When to Use

- Creating interactive demos or prototypes
- Building standalone calculators or tools
- Data visualization dashboards
- Interactive documentation
- Shareable proof-of-concepts
- Any web experience that needs to work offline

## Quick Start

1. **Create single HTML file** with all CSS/JS inline
2. **Use CDN for libraries** (Chart.js, Plotly, etc.)
3. **Embed data directly** as JSON or JS objects
4. **Test locally** by opening file in browser
5. **Share** as single file attachment

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Web Artifact</title>
  <style>
    body { font-family: system-ui; padding: 20px; }
    .btn { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
  </style>
</head>
<body>
  <h1>Interactive Tool</h1>
  <button class="btn" onclick="calculate()">Calculate</button>
  <div id="result"></div>
  <script>
    function calculate() {
      document.getElementById('result').textContent = 'Result: ' + (Math.random() * 100).toFixed(2);
    }
  </script>
</body>
</html>
```

## Related Skills

- [frontend-design](../../content-design/frontend-design/SKILL.md) - Advanced UI design
- [algorithmic-art](../../content-design/algorithmic-art/SKILL.md) - Generative visuals
- [theme-factory](../../content-design/theme-factory/SKILL.md) - Color and typography

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections
- **1.0.0** (2024-10-15): Initial release with basic template, dashboard, calculator, data visualization examples, CDN library references, best practices

## Sub-Skills

- [Performance (+2)](performance/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)

## Sub-Skills

- [Self-Contained Architecture (+1)](self-contained-architecture/SKILL.md)
- [Basic Template](basic-template/SKILL.md)
- [1. Interactive Dashboard (+1)](1-interactive-dashboard/SKILL.md)
- [Common CDN Libraries](common-cdn-libraries/SKILL.md)
- [File Naming (+2)](file-naming/SKILL.md)
