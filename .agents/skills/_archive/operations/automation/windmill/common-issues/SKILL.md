---
name: windmill-common-issues
description: 'Sub-skill of windmill: Common Issues (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: Script timeout**
```yaml
# Increase timeout in script metadata
# At top of script file:
# extra_perms:
#   timeout: 600  # 10 minutes
```

**Issue: Import errors in Python**
```python
# Add dependencies to script header
# requirements:
# pandas==2.0.0
# requests==2.31.0

import pandas as pd
import requests
```

**Issue: Resource not found**
```bash
# List available resources
wmill resource list

# Check resource path
wmill resource get u/admin/my_resource
```


## Debugging Tips


```python
# Add logging
import wmill

def main(data: dict):
    print(f"Input: {data}")  # Shows in logs
    wmill.set_state({"debug": "checkpoint_1"})

    result = process(data)

    print(f"Result: {result}")
    return result

# Check script state
# wmill script get-state f/my_script
```

```bash
# View recent runs
wmill job list --script f/data/my_script --limit 10

# Get job logs
wmill job get <job_id>
```
