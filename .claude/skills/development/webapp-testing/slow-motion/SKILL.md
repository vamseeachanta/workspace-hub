---
name: webapp-testing-slow-motion
description: 'Sub-skill of webapp-testing: Slow Motion (+3).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Slow Motion (+3)

## Slow Motion


```python
browser = p.chromium.launch(slow_mo=500)  # 500ms delay between actions
```

## Headed Mode


```python
browser = p.chromium.launch(headless=False)  # See the browser
```

## Pause Execution


```python
page.pause()  # Opens Playwright Inspector
```

## Trace Recording


```python
context = browser.new_context()
context.tracing.start(screenshots=True, snapshots=True)

page = context.new_page()
# ... test code ...

context.tracing.stop(path="trace.zip")
# View with: playwright show-trace trace.zip
```
