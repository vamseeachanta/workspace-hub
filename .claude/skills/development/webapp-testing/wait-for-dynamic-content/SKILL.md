---
name: webapp-testing-wait-for-dynamic-content
description: 'Sub-skill of webapp-testing: Wait for Dynamic Content (+5).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Wait for Dynamic Content (+5)

## Wait for Dynamic Content


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

## Element Selection


**By Text:**
```python
page.get_by_text("Submit").click()
page.get_by_text("Welcome", exact=False).wait_for()
```

**By Role:**
```python
page.get_by_role("button", name="Submit").click()
page.get_by_role("textbox", name="Email").fill("test@example.com")

*See sub-skills for full details.*

## Form Interaction


```python
# Fill form
page.locator("#username").fill("testuser")
page.locator("#password").fill("password123")
page.locator("#remember").check()
page.get_by_role("button", name="Login").click()

# Wait for navigation
page.wait_for_url("**/dashboard")
```

## Screenshots


```python
# Full page
page.screenshot(path="full.png", full_page=True)

# Element only
page.locator(".main-content").screenshot(path="element.png")

# Viewport only
page.screenshot(path="viewport.png")
```

## Console Logs


```python
# Capture console output
console_messages = []

def handle_console(msg):
    console_messages.append({
        "type": msg.type,
        "text": msg.text
    })


*See sub-skills for full details.*

## Network Monitoring


```python
# Capture requests
requests = []

def handle_request(request):
    requests.append({
        "url": request.url,
        "method": request.method
    })


*See sub-skills for full details.*
