---
name: webapp-testing
description: Web application testing toolkit using Playwright with Python. Use for verifying frontend functionality, debugging UI behavior, capturing browser screenshots, viewing browser logs, and automating web interactions.
---

# Web Application Testing Skill

## Overview

This toolkit enables testing local web applications using Playwright with Python for frontend verification, UI debugging, screenshot capture, and browser automation.

## Quick Start

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

## Installation

```bash
pip install playwright
playwright install chromium
```

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

1. **Wait appropriately**: Use `networkidle` for dynamic content
2. **Select elements**: Prefer text, role, or data-testid over CSS
3. **Handle async**: Always wait for elements before interacting
4. **Clean up**: Close browsers and pages after tests
5. **Use fixtures**: Reuse browser instances across tests

## Dependencies

```bash
pip install playwright pytest requests
playwright install chromium
```
