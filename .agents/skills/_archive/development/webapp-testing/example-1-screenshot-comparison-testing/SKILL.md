---
name: webapp-testing-example-1-screenshot-comparison-testing
description: 'Sub-skill of webapp-testing: Example 1: Screenshot Comparison Testing
  (+2).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Screenshot Comparison Testing (+2)

## Example 1: Screenshot Comparison Testing


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


## Example 2: Form Automation


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


## Example 3: API Response Verification


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
