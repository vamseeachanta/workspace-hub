---
name: obsidian-integration-with-notion-export
description: 'Sub-skill of obsidian: Integration with Notion Export.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Integration with Notion Export

## Integration with Notion Export


```python
#!/usr/bin/env python3
"""notion_to_obsidian.py - Export Notion pages to Obsidian"""

import os
import re
from notion_client import Client

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
VAULT_PATH = os.path.expanduser("~/Documents/ObsidianVault")

*See sub-skills for full details.*
