---
name: webapp-testing-do
description: 'Sub-skill of webapp-testing: Do (+1).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Do (+1)

## Do


1. Wait appropriately using `networkidle` for dynamic content
2. Select elements by text, role, or data-testid over CSS
3. Handle async operations with proper waits
4. Clean up browsers and pages after tests
5. Use fixtures for browser instance reuse
6. Capture console logs for debugging


## Don't


1. Use arbitrary `time.sleep()` for waits
2. Rely on fragile CSS selectors
3. Skip error handling in test cleanup
4. Run tests without checking server status
5. Ignore network errors during testing
