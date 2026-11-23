---
name: raycast-alfred-4-alfred-workflows-python
description: 'Sub-skill of raycast-alfred: 4. Alfred Workflows - Python.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 4. Alfred Workflows - Python

## 4. Alfred Workflows - Python


```python
#!/usr/bin/env python3
# alfred-github-search.py
# ABOUTME: Search GitHub repositories from Alfred
# ABOUTME: Python script filter for Alfred

import sys
import json
import urllib.request
import urllib.parse
import os

def search_github(query):
    """Search GitHub repositories"""
    if not query or len(query) < 2:
        return []

    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&per_page=10"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Alfred-GitHub-Search",
    }

    if token:
        headers["Authorization"] = f"token {token}"

    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            return data.get("items", [])
    except Exception as e:
        return []

def format_alfred_results(repos):
    """Format results for Alfred JSON output"""
    items = []

    for repo in repos:
        items.append({
            "uid": str(repo["id"]),
            "title": repo["full_name"],
            "subtitle": f"★ {repo['stargazers_count']} | {repo.get('description', 'No description')}",
            "arg": repo["html_url"],
            "icon": {
                "path": "icon.png"
            },
            "mods": {
                "cmd": {
                    "arg": f"git clone {repo['clone_url']}",
                    "subtitle": "Clone repository"
                },
                "alt": {
                    "arg": repo["clone_url"],
                    "subtitle": "Copy clone URL"
                }
            }
        })

    return {"items": items}

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    repos = search_github(query)
    result = format_alfred_results(repos)
    print(json.dumps(result))
```

```python
#!/usr/bin/env python3
# alfred-jira-search.py
# ABOUTME: Search JIRA issues from Alfred
# ABOUTME: JQL-powered issue search

import sys
import json
import urllib.request
import urllib.parse
import base64
import os

JIRA_BASE_URL = os.environ.get("JIRA_URL", "https://your-company.atlassian.net")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")

def search_jira(query):
    """Search JIRA issues"""
    if not query:
        return []

    # Build JQL query
    jql = f'text ~ "{query}" ORDER BY updated DESC'
    url = f"{JIRA_BASE_URL}/rest/api/3/search?jql={urllib.parse.quote(jql)}&maxResults=10"

    # Basic auth
    auth = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()

    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {auth}",
    }

    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            return data.get("issues", [])
    except Exception as e:
        return []

def format_alfred_results(issues):
    """Format JIRA issues for Alfred"""
    items = []

    status_icons = {
        "To Do": "⚪",
        "In Progress": "🔵",
        "Done": "✅",
        "Blocked": "🔴",
    }

    for issue in issues:
        fields = issue["fields"]
        status = fields.get("status", {}).get("name", "Unknown")
        icon = status_icons.get(status, "⚫")

        items.append({
            "uid": issue["key"],
            "title": f"{icon} {issue['key']}: {fields['summary']}",
            "subtitle": f"{status} | {fields.get('assignee', {}).get('displayName', 'Unassigned')}",
            "arg": f"{JIRA_BASE_URL}/browse/{issue['key']}",
            "icon": {"path": "jira-icon.png"},
            "mods": {
                "cmd": {
                    "arg": issue["key"],
                    "subtitle": "Copy issue key"
                }
            }
        })

    return {"items": items}

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    issues = search_jira(query)
    result = format_alfred_results(issues)
    print(json.dumps(result))
```

```python
#!/usr/bin/env python3
# alfred-snippet-manager.py
# ABOUTME: Text snippet management
# ABOUTME: Store and retrieve code snippets

import sys
import json
import os
import hashlib
from pathlib import Path

SNIPPETS_DIR = Path.home() / ".alfred-snippets"
SNIPPETS_DIR.mkdir(exist_ok=True)

def load_snippets():
    """Load all snippets"""
    snippets = []
    for file in SNIPPETS_DIR.glob("*.json"):
        with open(file) as f:
            snippet = json.load(f)
            snippet["file"] = str(file)
            snippets.append(snippet)
    return sorted(snippets, key=lambda x: x.get("uses", 0), reverse=True)

def save_snippet(name, content, tags=None):
    """Save a new snippet"""
    snippet_id = hashlib.md5(name.encode()).hexdigest()[:8]
    snippet = {
        "id": snippet_id,
        "name": name,

*Content truncated — see parent skill for full reference.*
