---
name: webapp-testing-start-server-before-testing
description: 'Sub-skill of webapp-testing: Start Server Before Testing (+1).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Start Server Before Testing (+1)

## Start Server Before Testing


```python
import subprocess
import time
from playwright.sync_api import sync_playwright

# Start server
server = subprocess.Popen(
    ["npm", "run", "dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE

*See sub-skills for full details.*

## Check Server Status


```python
import requests

def is_server_running(url="http://localhost:3000"):
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False
```
