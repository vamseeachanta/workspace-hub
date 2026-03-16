---
name: clinical-trial-protocol-startup-welcome-and-mode-selection
description: 'Sub-skill of clinical-trial-protocol: Startup: Welcome and Mode Selection
  (+1).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Startup: Welcome and Mode Selection (+1)

## Startup: Welcome and Mode Selection


When skill is invoked, display the following message:

```
CLINICAL TRIAL PROTOCOL

Welcome! This skill generates clinical trial protocols for medical devices or drugs.

[If waypoints/intervention_metadata.json exists:]
Found existing protocol in progress: [Intervention Name]
  Type: [Device/Drug]
  Completed: [List of completed steps]
  Next: [Next step to execute]

SELECT MODE:

1. Research Only - Run clinical research analysis (Steps 0-1)
   - Collect intervention information
   - Research similar clinical trials
   - Find FDA guidance and regulatory pathways
   - Generate comprehensive research summary as .md artifact

2. Full Protocol - Generate complete clinical trial protocol (Steps 0-5)
   - Everything in Research Only, plus:
   - Generate all protocol sections
   - Create professional protocol document

3. Exit

Please select an option (1, 2, or 3):
```

**STOP and WAIT for user selection (1, 2, or 3)**

- If **1 (Research Only)**: Set `execution_mode = "research_only"` and proceed to Research Only Workflow Logic
- If **2 (Full Protocol)**: Set `execution_mode = "full_protocol"` and proceed to Full Workflow Logic
- If **3 (Exit)**: Exit gracefully with "No problem! Restart the skill anytime to continue."

---


## Research Only Workflow Logic


**This workflow executes only Steps 0 and 1, then generates a formatted research summary artifact.**

**Step 1: Check for Existing Waypoints**
- If `waypoints/intervention_metadata.json` exists: Load metadata, check if steps 0 and 1 are already complete
- If no metadata exists: Start from Step 0

**Step 2: Execute Research Steps (0 and 1)**

For each step (0, 1):

1. **Check completion status:** If step already completed in metadata, skip with "Step [X] already complete"

2. **Execute step:**
   - Display "Executing Step [X]..."
   - Read and follow the corresponding subskill file instructions
   - Wait for completion
   - Display "Step [X] complete"
   - **Step execution method (ON-DEMAND LOADING):** When a step is ready to execute (NOT before), read the subskill markdown file and execute ALL instructions within it
   - **Step-to-file mapping:**
     - Step 0: `references/00-initialize-intervention.md` (collect intervention info)
     - Step 1: `references/01-research-protocols.md` (clinical research and FDA guidance)

3. **Handle errors:** If step fails, ask user to retry or exit. Save current state for resume capability.

**Step 3: Generate Research Summary Artifact**

After Step 1 completes successfully:

1. **Read waypoint files:**
   - `waypoints/intervention_metadata.json` (intervention details)
   - `waypoints/01_clinical_research_summary.json` (research findings)

2. **Create formatted markdown summary:** Generate a comprehensive, well-formatted research summary as a markdown artifact with the following structure:

```markdown
# Clinical Research Summary: [Intervention Name]
