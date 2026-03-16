---
name: github-project-board-status-mapping
description: 'Sub-skill of github-project-board: Status Mapping (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Status Mapping (+1)

## Status Mapping


```yaml
# .github/board-sync.yml
version: 1
project:
  name: "Development Board"
  number: 1

mapping:
  status:
    pending: "Backlog"

*See sub-skills for full details.*

## View Configuration


```json
{
  "views": [
    {
      "name": "Swarm Overview",
      "type": "board",
      "groupBy": "status",
      "filters": ["is:open"],
      "sort": "priority:desc"
    },

*See sub-skills for full details.*
