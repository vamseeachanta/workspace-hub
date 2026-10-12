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

## Human review / rating apps

When the artifact is an interactive review, scoring, calibration, triage, QA, or annotation app, include a one-click **Submit** workflow by default. Manual JSON/CSV export-download-upload is acceptable only as a fallback; it is too convoluted as the primary user path.

Recommended pattern:

- Add localStorage autosave, progress tracking, JSON/CSV export, and JSON import/resume.
- Add a prominent `Submit` button as the primary completion path; export/copy controls should be visually secondary.
- Add a visible receiver health/status indicator so the user knows whether Submit will work before investing time in scoring.
- Place a tiny localhost receiver next to the HTML artifact (`GET /health`, `POST /submit`) that writes timestamped submissions plus `submissions/latest.json`.
- The app should POST to `http://127.0.0.1:<port>/submit`; if unavailable, copy JSON to clipboard and show the exact receiver start command.
- Verify with a browser load, a test edit, a submit POST, and reset test state before handoff.

See `references/interactive-review-submit-pattern.md` for implementation details and pitfalls.

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

## Interactive Rating / Review Apps

Use this pattern when the user needs to rate, triage, or calibrate a batch of examples in a browser instead of editing Markdown/CSV by hand.

1. Build a single-file HTML app with embedded JSON data, no server dependency, and all CSS/JS inline.
2. Include per-item navigation, progress tracking, score inputs, defect/checklist toggles, notes, and autosave via `localStorage`.
3. Provide JSON and CSV export; if the user may resume later, also provide JSON import or copy-to-clipboard.
4. Verify the artifact before handoff:
   - extract embedded JavaScript and run `node --check` when Node is available;
   - open the file in a browser and confirm the expected card/control counts;
   - exercise one score/checkbox/note update and then reset the test state so the user starts clean.
5. Watch for JavaScript string-escaping hazards when generating HTML from Python. In particular, CSV export code must use an escaped newline string (`'\\n'`) inside JavaScript; an actual newline inside a quoted JS string will make the page render shell content but fail to initialize.

Starter template: `templates/interactive-rating-app.html`.

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
