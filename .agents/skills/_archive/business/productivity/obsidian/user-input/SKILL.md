---
name: obsidian-user-input
description: 'Sub-skill of obsidian: User Input.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# User Input

## User Input


<% tp.system.prompt("Enter project name") %>
<% tp.system.suggester(["Option 1", "Option 2"], ["value1", "value2"]) %>
