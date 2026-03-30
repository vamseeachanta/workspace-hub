---
name: webapp-testing-assertion-examples
description: 'Sub-skill of webapp-testing: Assertion Examples (+1).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Assertion Examples (+1)

## Assertion Examples


```python
from playwright.sync_api import expect

# Text content
expect(page.locator("h1")).to_have_text("Welcome")

# Visibility
expect(page.locator(".modal")).to_be_visible()
expect(page.locator(".loading")).to_be_hidden()


*See sub-skills for full details.*

## Test Structure


```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

*See sub-skills for full details.*
