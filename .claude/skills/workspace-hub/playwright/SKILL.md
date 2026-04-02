---
name: playwright
version: 1.0.0
category: workspace-hub
applies-to:
- claude
- codex
- gemini
invocation: /playwright
description: 'Playwright CLI recipes for E2E testing, screenshots, PDF export, and
  accessibility audits. Use instead of browser MCP tools for deterministic, token-efficient
  browser automation.

  '
type: reference
triggers:
- playwright
- screenshot
- pdf export
- e2e test
- browser automation
- accessibility audit
- headless browser
related_skills:
- webapp-testing
---

# Playwright CLI Skill

> Token-efficient browser automation via `npx playwright` CLI.
> Prefer this over MCP browser tools for deterministic, scriptable tasks.

## Quick Start

```bash
# Install (one-time) — only chromium needed for most tasks
npx playwright install chromium
```

## Decision Matrix: Playwright CLI vs Chrome MCP

| Use Case | Tool | Why |
|----------|------|-----|
| Page screenshot | Playwright CLI | Single command, ~27K tokens vs ~114K MCP |
| PDF export | Playwright CLI | Native `npx playwright pdf` command |
| E2E test suite | Playwright CLI | `npx playwright test` with config file |
| Accessibility audit | Playwright CLI | Scriptable, repeatable, CI-friendly |
| UI visual audit | Playwright CLI | gsd-ui-auditor already uses this pattern |
| Interactive exploration | Chrome MCP | Stateful browsing, clicking, form filling |
| Live debugging | Chrome MCP | Real-time DOM inspection, console access |
| Multi-step navigation | Chrome MCP | When path is unknown, needs human-like exploration |

**Rule of thumb:** If the task is scriptable and deterministic, use Playwright CLI.
If the task requires interactive exploration or unknown navigation, use Chrome MCP.

## Recipes

### 1. Page Screenshot

```bash
# Basic screenshot
npx playwright screenshot <url> <output.png>

# Full-page (scrollable area)
npx playwright screenshot --full-page <url> <output.png>

# Mobile viewport
npx playwright screenshot --device "iPhone 12" <url> <output-mobile.png>

# Dark mode
npx playwright screenshot --color-scheme dark <url> <output-dark.png>

# Wait for dynamic content
npx playwright screenshot --wait-for-selector ".loaded" <url> <output.png>
npx playwright screenshot --wait-for-timeout 3000 <url> <output.png>

# Multi-viewport capture (desktop + mobile + tablet)
npx playwright screenshot --full-page <url> desktop.png
npx playwright screenshot --device "iPhone 12" <url> mobile.png
npx playwright screenshot --device "iPad Pro 11" <url> tablet.png
```

### 2. PDF Export

```bash
# Default (Letter size)
npx playwright pdf <url> <output.pdf>

# A4 format
npx playwright pdf --paper-format A4 <url> <output.pdf>

# Wait for content before export
npx playwright pdf --wait-for-selector ".content-loaded" <url> <output.pdf>
```

### 3. E2E Test Runner

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e/login.spec.ts

# Run with specific browser
npx playwright test --project=chromium

# Run in headed mode (for debugging)
npx playwright test --headed

# Run with HTML report
npx playwright test --reporter=html

# Run single test by title
npx playwright test -g "should display dashboard"

# Debug mode (step through)
npx playwright test --debug
```

### 4. Accessibility Audit

```python
# accessibility-audit.py — run with: python accessibility-audit.py <url>
import sys, json
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)

    # Snapshot accessibility tree
    snapshot = page.accessibility.snapshot()
    print(json.dumps(snapshot, indent=2))

    # Check for missing alt text
    images = page.query_selector_all("img:not([alt])")
    if images:
        print(f"\nWARNING: {len(images)} images missing alt text")

    # Check for missing form labels
    inputs = page.query_selector_all("input:not([aria-label]):not([id])")
    if inputs:
        print(f"WARNING: {len(inputs)} inputs missing labels")

    browser.close()
```

### 5. Code Generation (Record and Replay)

```bash
# Record user actions and generate test code
npx playwright codegen <url>

# Generate code for specific browser
npx playwright codegen --browser firefox <url>

# Generate code targeting specific language
npx playwright codegen --target python <url>
```

## Token Cost Context

Playwright CLI uses ~4x fewer tokens than MCP-based browser tools for equivalent tasks:
- **CLI screenshot:** ~27K tokens (single shell command + file path result)
- **MCP screenshot:** ~114K tokens (tool schemas loaded, browser state in context, JSON roundtrips)
- **CLI test run:** compact stdout output, results on disk
- **MCP test equivalent:** full DOM state serialized into context window each step

The savings compound over longer sessions. CLI keeps browser state on disk; MCP keeps it in the model's context window.

## Integration with Existing Tools

- **gsd-ui-auditor** already uses `npx playwright screenshot` for multi-viewport captures
- **webapp-testing skill** provides Python-based Playwright patterns for deeper integration
- **tests/playwright.config.js** defines the project's E2E test configuration

## Common Options (All Commands)

| Flag | Description |
|------|-------------|
| `-b, --browser <type>` | `cr`, `ff`, `wk` (default: `chromium`) |
| `--device <name>` | Emulate device (e.g., `"iPhone 12"`, `"iPad Pro 11"`) |
| `--color-scheme <scheme>` | `light` or `dark` |
| `--ignore-https-errors` | Skip certificate validation |
| `--load-storage <file>` | Load auth state from file |
| `--lang <locale>` | Set language (e.g., `en-GB`) |
| `--proxy-server <url>` | Route through proxy |
| `--wait-for-selector <sel>` | Wait for element before action |
| `--wait-for-timeout <ms>` | Wait N milliseconds before action |
