---
name: webapp-testing
description: Web application testing toolkit using Playwright with Python. Use for
  verifying frontend functionality, debugging UI behavior, capturing browser screenshots,
  viewing browser logs, and automating web interactions.
version: 1.1.0
category: development
related_skills:
- engineering-report-generator
- data-pipeline-processor
- parallel-file-processor
capabilities: []
requires: []
see_also:
- webapp-testing-static-html
- webapp-testing-wait-for-dynamic-content
- webapp-testing-start-server-before-testing
- webapp-testing-assertion-examples
- webapp-testing-slow-motion
tags: []
---

# Webapp Testing

## Overview

This toolkit enables testing local web applications using Playwright with Python for frontend verification, UI debugging, screenshot capture, and browser automation.

## Quick Start

```bash
# Install dependencies
pip install playwright pytest requests
playwright install chromium
```

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:3000")

    # Take screenshot
    page.screenshot(path="screenshot.png")

    # Get page content
    content = page.content()
    print(content)

    browser.close()
```

## When to Use

- Verifying frontend functionality after code changes
- Debugging UI behavior and layout issues
- Capturing screenshots for documentation
- Viewing browser console logs for errors
- Automating repetitive web interactions
- End-to-end testing of web applications
- Validating form submissions and user flows

## Related Skills

- [engineering-report-generator](../engineering-report-generator/SKILL.md) - Generate test reports
- [data-pipeline-processor](../data-pipeline-processor/SKILL.md) - Process test data
- [parallel-file-processor](../parallel-file-processor/SKILL.md) - Batch screenshot processing

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format with Quick Start, Usage Examples, Error Handling, Metrics, Execution Checklist
- **1.0.0** (2024-10-15): Initial release with Playwright patterns, server management, debugging tools

## Sub-Skills

- [Example 1: Screenshot Comparison Testing (+2)](example-1-screenshot-comparison-testing/SKILL.md)
- [Do (+1)](do/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Metrics](metrics/SKILL.md)
- [Dependencies](dependencies/SKILL.md)

## Sub-Skills

- [Static HTML (+2)](static-html/SKILL.md)
- [Wait for Dynamic Content (+5)](wait-for-dynamic-content/SKILL.md)
- [Start Server Before Testing (+1)](start-server-before-testing/SKILL.md)
- [Assertion Examples (+1)](assertion-examples/SKILL.md)
- [Slow Motion (+3)](slow-motion/SKILL.md)
