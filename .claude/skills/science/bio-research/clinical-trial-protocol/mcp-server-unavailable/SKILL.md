---
name: clinical-trial-protocol-mcp-server-unavailable
description: 'Sub-skill of clinical-trial-protocol: MCP Server Unavailable (+2).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# MCP Server Unavailable (+2)

## MCP Server Unavailable

- Detected in: Step 1
- Action: Display error with installation instructions
- Allow user to retry after installing MCP server
- No fallback available - MCP server is required for protocol research


## Step Fails or Returns Error

- Action: Display error message from subskill
- Ask user: "Retry step? (Yes/No)"
  - Yes: Re-run step
  - No: Save current state, exit orchestrator


## User Interruption

- All progress saved in waypoint files
- User can resume anytime by restarting the skill
- Workflow automatically detects completed steps and resumes from next step
- No data loss
