---
name: clinical-trial-protocol-execution-control-read-this-first
description: 'Sub-skill of clinical-trial-protocol: EXECUTION CONTROL - READ THIS
  FIRST.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# EXECUTION CONTROL - READ THIS FIRST

## EXECUTION CONTROL - READ THIS FIRST


**CRITICAL: This orchestrator follows a SIMPLE START approach:**

1. **Display the welcome message FIRST** (shown in "Startup: Welcome and Confirmation" section below)
2. **Ask user to confirm they're ready to proceed** - Wait for confirmation (yes/no)
3. **Jump directly into Full Workflow Logic** - Automatically run subskills sequentially
4. **Do NOT pre-read subskill files** - Subskills are loaded on-demand only when their step executes

**Why this matters:**
- Pre-reading all subskills wastes context and memory
- Subskills should only load when actually needed during execution
- Workflow automatically handles resuming from existing waypoints
