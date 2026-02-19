---
name: webapp-testing
description: Web application testing toolkit using Playwright with Python. Use for verifying frontend functionality, debugging UI behavior, capturing browser screenshots, viewing browser logs, and automating web interactions.
version: 1.1.0
category: development
related_skills:
  - engineering-report-generator
  - data-pipeline-processor
  - parallel-file-processor
capabilities: []
requires: []
see_also: []
---

# Web Application Testing Skill

> Version: 1.1.0
> Category: Development
> Last Updated: 2026-01-02

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

## Decision Tree

### Static HTML
1. Read files directly to find selectors
2. Then automate with Playwright

### Dynamic Webapps
1. Check if server runs
2. If not, start with helper script
3. Perform reconnaissance (screenshots/DOM)
4. Then automate

### Running Servers
1. Perform reconnaissance first
2. Take screenshots
3. Inspect DOM
4. Then automate

## Core Patterns

### Wait for Dynamic Content
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:3000")

    # CRITICAL: Wait for JS to execute
    page.wait_for_load_state("networkidle")

    # Now safe to interact
    content = page.content()
    browser.close()
```

### Element Selection

**By Text:**
```python
page.get_by_text("Submit").click()
page.get_by_text("Welcome", exact=False).wait_for()
```

**By Role:**
```python
page.get_by_role("button", name="Submit").click()
page.get_by_role("textbox", name="Email").fill("test@example.com")
page.get_by_role("link", name="Home").click()
```

**By CSS Selector:**
```python
page.locator(".btn-primary").click()
page.locator("#email-input").fill("test@example.com")
page.locator("[data-testid='submit']").click()
```

**By ID:**
```python
page.locator("#submit-button").click()
```

### Form Interaction
```python
# Fill form
page.locator("#username").fill("testuser")
page.locator("#password").fill("password123")
page.locator("#remember").check()
page.get_by_role("button", name="Login").click()

# Wait for navigation
page.wait_for_url("**/dashboard")
```

### Screenshots
```python
# Full page
page.screenshot(path="full.png", full_page=True)

# Element only
page.locator(".main-content").screenshot(path="element.png")

# Viewport only
page.screenshot(path="viewport.png")
```

### Console Logs
```python
# Capture console output
console_messages = []

def handle_console(msg):
    console_messages.append({
        "type": msg.type,
        "text": msg.text
    })

page.on("console", handle_console)
page.goto("http://localhost:3000")

# Print captured logs
for msg in console_messages:
    print(f"[{msg['type']}] {msg['text']}")
```

### Network Monitoring
```python
# Capture requests
requests = []

def handle_request(request):
    requests.append({
        "url": request.url,
        "method": request.method
    })

page.on("request", handle_request)
page.goto("http://localhost:3000")

# Print captured requests
for req in requests:
    print(f"{req['method']} {req['url']}")
```

## Server Management

### Start Server Before Testing
```python
import subprocess
import time
from playwright.sync_api import sync_playwright

# Start server
server = subprocess.Popen(
    ["npm", "run", "dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(3)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:3000")
        # ... test code ...
        browser.close()
finally:
    server.terminate()
```

### Check Server Status
```python
import requests

def is_server_running(url="http://localhost:3000"):
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False
```

## Testing Patterns

### Assertion Examples
```python
from playwright.sync_api import expect

# Text content
expect(page.locator("h1")).to_have_text("Welcome")

# Visibility
expect(page.locator(".modal")).to_be_visible()
expect(page.locator(".loading")).to_be_hidden()

# Input values
expect(page.locator("#email")).to_have_value("test@example.com")

# Count
expect(page.locator(".item")).to_have_count(5)

# URL
expect(page).to_have_url("http://localhost:3000/dashboard")
```

### Test Structure
```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

def test_homepage(page):
    page.goto("http://localhost:3000")
    assert page.title() == "My App"

def test_login(page):
    page.goto("http://localhost:3000/login")
    page.fill("#username", "testuser")
    page.fill("#password", "password")
    page.click("button[type='submit']")
    page.wait_for_url("**/dashboard")
```

## Usage Examples

### Example 1: Screenshot Comparison Testing

```python
from playwright.sync_api import sync_playwright
from pathlib import Path

def capture_page_state(url: str, output_dir: str):
    """Capture full page screenshot and HTML content."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Screenshot
        page.screenshot(path=str(output / "screenshot.png"), full_page=True)

        # HTML content
        (output / "content.html").write_text(page.content())

        browser.close()

    return output

# Usage
capture_page_state("http://localhost:3000", "tests/snapshots/")
```

### Example 2: Form Automation

```python
def submit_contact_form(page, name, email, message):
    """Submit a contact form and verify success."""
    page.goto("http://localhost:3000/contact")

    # Fill form fields
    page.fill("[name='name']", name)
    page.fill("[name='email']", email)
    page.fill("[name='message']", message)

    # Submit
    page.click("button[type='submit']")

    # Wait for success message
    page.wait_for_selector(".success-message")

    return page.locator(".success-message").text_content()
```

### Example 3: API Response Verification

```python
def verify_api_call(page, endpoint_pattern):
    """Intercept and verify API calls."""
    api_response = None

    def handle_response(response):
        nonlocal api_response
        if endpoint_pattern in response.url:
            api_response = response.json()

    page.on("response", handle_response)
    page.goto("http://localhost:3000/dashboard")
    page.wait_for_load_state("networkidle")

    return api_response
```

## Debugging

### Slow Motion
```python
browser = p.chromium.launch(slow_mo=500)  # 500ms delay between actions
```

### Headed Mode
```python
browser = p.chromium.launch(headless=False)  # See the browser
```

### Pause Execution
```python
page.pause()  # Opens Playwright Inspector
```

### Trace Recording
```python
context = browser.new_context()
context.tracing.start(screenshots=True, snapshots=True)

page = context.new_page()
# ... test code ...

context.tracing.stop(path="trace.zip")
# View with: playwright show-trace trace.zip
```

## Best Practices

### Do

1. Wait appropriately using `networkidle` for dynamic content
2. Select elements by text, role, or data-testid over CSS
3. Handle async operations with proper waits
4. Clean up browsers and pages after tests
5. Use fixtures for browser instance reuse
6. Capture console logs for debugging

### Don't

1. Use arbitrary `time.sleep()` for waits
2. Rely on fragile CSS selectors
3. Skip error handling in test cleanup
4. Run tests without checking server status
5. Ignore network errors during testing

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TimeoutError` | Element not found in time | Use explicit waits or increase timeout |
| `Page closed` | Browser closed prematurely | Check cleanup order in fixtures |
| `Connection refused` | Server not running | Start server before tests |
| `Element not visible` | Hidden by CSS/JS | Wait for visibility state |
| `Target closed` | Navigation during action | Wait for navigation to complete |

### Debugging Tips

```python
# Increase default timeout
page.set_default_timeout(60000)  # 60 seconds

# Take screenshot on failure
try:
    page.click("#submit")
except Exception as e:
    page.screenshot(path="error_screenshot.png")
    raise

# Print page HTML for debugging
print(page.content())
```

## Execution Checklist

- [ ] Playwright and chromium installed
- [ ] Server running before tests
- [ ] Proper wait states for dynamic content
- [ ] Screenshots captured for visual verification
- [ ] Console logs monitored for errors
- [ ] Network requests validated
- [ ] Fixtures clean up browser resources
- [ ] Error screenshots captured on failure
- [ ] Tests run in both headed and headless modes

## Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Test Duration | <10s per test | Individual test execution time |
| Flakiness Rate | <2% | Tests passing consistently |
| Screenshot Match | 100% | Visual regression accuracy |
| Network Coverage | >90% | API endpoints tested |

## Dependencies

```bash
pip install playwright pytest requests
playwright install chromium
```

## Related Skills

- [engineering-report-generator](../engineering-report-generator/SKILL.md) - Generate test reports
- [data-pipeline-processor](../data-pipeline-processor/SKILL.md) - Process test data
- [parallel-file-processor](../parallel-file-processor/SKILL.md) - Batch screenshot processing

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format with Quick Start, Usage Examples, Error Handling, Metrics, Execution Checklist
- **1.0.0** (2024-10-15): Initial release with Playwright patterns, server management, debugging tools
