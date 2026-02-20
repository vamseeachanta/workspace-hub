---
name: html-report-verify
description: >
  Visual + structural verification of HTML benchmark/validation reports using the
  Claude-in-Chrome extension. Opens the report in a browser, takes screenshots,
  checks key DOM elements, and produces a PASS/FAIL verdict. Generic by default;
  module-specific check lists extend the base set.
version: 1.0.0
category: development
last_updated: 2026-02-19
tools: [Bash, Task, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__read_page, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__find, mcp__claude-in-chrome__read_console_messages]
related_skills:
  - verification-loop
  - webapp-testing
tags: [html, reporting, verification, chrome, visual-qa, benchmark, orcawave]
platforms: [windows, linux, macos]
---

# /html-report-verify — HTML Report Visual & Structural Verification

Opens an HTML report in Chrome (via local HTTP server for local files) and
performs layered verification: console errors → DOM structure → visual scan →
module-specific checks.

## Trigger

```
/html-report-verify <path-or-url> [--module <name>]
```

Examples:
```
/html-report-verify docs/modules/orcawave/L00_validation_wamit/3.2/benchmark/benchmark_report.html --module orcawave-qtf
/html-report-verify http://localhost:8974/3.1/benchmark/benchmark_report.html
```

## Verification Layers

### Layer 0 — Server Setup (local files only)
If a local path is given, start a Python HTTP server in the parent directory on
a free port (default `8974`). Use `uv run python -m http.server` so the uv
environment is active. Kill the server after verification is complete.

### Layer 1 — Page Load
- Navigate to URL via `mcp__claude-in-chrome__navigate`
- Take screenshot immediately
- Check `mcp__claude-in-chrome__read_console_messages` for JS errors (`onlyErrors: true`)
- FAIL if console shows uncaught errors or the page is blank

### Layer 2 — Generic DOM Structure Checks
Run via `mcp__claude-in-chrome__javascript_tool`:

| Check | Selector / Test | Pass Condition |
|-------|----------------|----------------|
| Title present | `document.title` | Non-empty string |
| H1/H2 headings | `querySelectorAll('h1,h2').length` | ≥ 1 |
| Navigation bar | `querySelector('.nav-bar, nav, [class*="nav"]')` | Not null |
| Plotly charts rendered | `querySelectorAll('.plotly-graph-div').length` | ≥ 1 |
| No broken images | `[...querySelectorAll('img')].every(i => i.complete && i.naturalWidth > 0)` | True |
| No empty script errors | Check console | Zero JS exceptions |

### Layer 3 — Visual Screenshot Scan
1. Screenshot top of page (executive summary / header)
2. Scroll to bottom (`window.scrollTo(0, document.body.scrollHeight)`)
3. Screenshot bottom of page (should show QTF / last section)
4. Confirm plots are visible (not grey/blank boxes)

### Layer 4 — Module-Specific Checks

#### `--module orcawave-qtf`
| Check | Test | Pass Condition |
|-------|------|----------------|
| QTF section exists | `document.getElementById('qtf-analysis')` | Not null |
| QTF heading | `querySelector('#qtf-analysis h2')?.textContent` | Contains "QTF Analysis" |
| Figure cards | `querySelectorAll('#qtf-analysis .qtf-figure').length` | ≥ 1 |
| Figure titles (h3) | `querySelectorAll('#qtf-analysis h3').length` | Matches figure count |
| Reference images | `querySelectorAll('#qtf-analysis img[src^="data:image"]').length` | ≥ 1 (if screenshots available) |
| Plotly in QTF section | `querySelectorAll('#qtf-analysis .plotly-graph-div').length` | ≥ 1 |
| OrcaWave label | Text search for "OrcaWave Output" | Present |
| Reference label | Text search for "Reference (WAMIT paper)" | Present |

Scroll into `#qtf-analysis` and take a screenshot to capture side-by-side layout.

#### `--module benchmark-correlation`
| Check | Test | Pass Condition |
|-------|------|----------------|
| Consensus table | `querySelector('table')` | Not null |
| DOF sections | `querySelectorAll('[id^="dof-"]').length` | ≥ 1 |
| Correlation values | Text contains `r=` | ≥ 1 match |
| Pass/Fail badges | Elements with green/red color styling | Present |

### Layer 5 — Verdict
Produce a structured report:

```
HTML Report Verification — <filename>
======================================
URL          : http://localhost:8974/...
Module checks: orcawave-qtf

Layer 1 (Load)         : PASS
Layer 2 (DOM)          : PASS  [3 h2, 12 Plotly divs, 0 broken images]
Layer 3 (Visual)       : PASS  [screenshots attached]
Layer 4 (Module: QTF)  : PASS  [2 figures, 2 reference images]

OVERALL: ✅ PASS
```

If any layer fails, list the specific failing check and what was found vs expected.

## Implementation Notes

- Always call `mcp__claude-in-chrome__tabs_context_mcp` first to get a valid tab ID
- Use `mcp__claude-in-chrome__tabs_create_mcp` for a fresh tab (don't reuse report tab)
- After verification, kill the HTTP server: `pkill -f "http.server 8974"` (Linux/macOS) or `taskkill` (Windows)
- On Windows MINGW: use `uv run python -m http.server` (not `python3`)
- The Plotly CDN script in the QTF section may cause a duplicate Plotly load warning in console — this is expected, not a failure

## Extending for New Modules

Add a new `--module <name>` block to Layer 4. The module check function receives
the tab ID and runs additional `javascript_tool` calls + screenshots tailored to
that report's specific sections.

## Style Quality Checklist

When verifying, note (but do not fail on) these visual quality signals:
- [ ] Section headers have consistent hierarchy (H1 → H2 → H3)
- [ ] Color scheme is consistent (no clashing inline colors)
- [ ] Charts have axis labels and a legend
- [ ] Reference screenshots are labeled ("Reference (WAMIT paper)")
- [ ] Side-by-side comparison columns are balanced in width
- [ ] No content overflow or horizontal scroll at 1280px viewport
