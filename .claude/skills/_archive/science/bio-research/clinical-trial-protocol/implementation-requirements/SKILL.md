---
name: clinical-trial-protocol-implementation-requirements
description: 'Sub-skill of clinical-trial-protocol: Implementation Requirements.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Implementation Requirements

## Implementation Requirements


When this skill is invoked:

1. **Display the welcome message with mode selection** (shown in "Startup: Welcome and Mode Selection" section)

2. **Wait for user mode selection** (1: Research Only, 2: Full Protocol, 3: Exit)

3. **Execute based on selected mode:**
   - **Research Only Mode (Option 1):**
     - Execute Research Only Workflow Logic (Steps 0-1 only)
     - Generate formatted research summary as .md artifact
     - Offer option to continue with full protocol or exit
   - **Full Protocol Mode (Option 2):**
     - Execute Full Workflow Logic (Steps 0-5)
     - Check for existing waypoints and resume from last completed step
     - OR start from Step 0 if no waypoints exist
     - Execute all steps sequentially until complete

4. **For each step execution (LAZY LOADING - On-Demand Only):**
   - **ONLY when a step is ready to execute**, read the corresponding subskill file
   - Do NOT read subskill files in advance or "to prepare"
   - Example: When Step 1 needs to run, THEN read `references/01-research-protocols.md` and follow its instructions
   - **For protocol development:** Execute Steps 2, 3, 4 sequentially in order
   - Do NOT try to execute multiple steps in parallel - run sequentially
   - Read each step's subskill file only when that specific step is about to execute

5. **Research summary artifact generation (Research Only Mode):**
   - After Step 1 completes, read waypoint files
   - Generate comprehensive, well-formatted markdown summary
   - Save to `waypoints/research_summary.md`
   - Display completion message with key findings

6. **Handle errors gracefully:**
   - If a step fails, give user option to retry or exit
   - If MCP server unavailable, explain how to install
   - All progress is saved automatically in waypoints

7. **Track progress:**
   - Update `waypoints/intervention_metadata.json` after each step
   - Show progress indicators to user (e.g., "Progress: 3/6 steps complete" or "Progress: 2/2 research steps complete")
   - Provide clear feedback on what's happening

8. **Final output:**
   - **Research Only:** Display research summary location and offer to continue with full protocol
   - **Full Protocol:** Congratulate user, display protocol location and next steps
   - Remind user of disclaimers
