---
name: webapp-testing-error-handling
description: 'Sub-skill of webapp-testing: Error Handling.'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

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
