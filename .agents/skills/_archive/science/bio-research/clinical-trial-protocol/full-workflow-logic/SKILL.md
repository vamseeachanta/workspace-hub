---
name: clinical-trial-protocol-full-workflow-logic
description: 'Sub-skill of clinical-trial-protocol: Full Workflow Logic.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Full Workflow Logic

## Full Workflow Logic


**Step 1: Check for Existing Waypoints**
- If `waypoints/intervention_metadata.json` exists: Load metadata, check `completed_steps` array, resume from next incomplete step
- If no metadata exists: Start from Step 0

**Step 2: Execute Steps in Order**

For each step (0, 1, 2, 3, 4, 5):

1. **Check completion status:** If step already completed in metadata, skip with "Step [X] already complete"

2. **Execute step:** Display "Executing Step [X]...", read and follow the corresponding subskill file instructions, wait for completion, display "Step [X] complete"
   - **Step execution method (ON-DEMAND LOADING):** When a step is ready to execute (NOT before), read the subskill markdown file and execute ALL instructions within it
   - **IMPORTANT:** Do NOT read subskill files in advance. Only read them at the moment of execution.
   - **Step-to-file mapping:**
     - Step 0: `references/00-initialize-intervention.md` (read when Step 0 executes)
     - Step 1: `references/01-research-protocols.md` (read when Step 1 executes)
     - Step 2: `references/02-protocol-foundation.md` (read when Step 2 executes - sections 1-6)
     - Step 3: `references/03-protocol-intervention.md` (read when Step 3 executes - sections 7-8)
     - Step 4: `references/04-protocol-operations.md` (read when Step 4 executes - sections 9-12)
     - Step 5: `references/05-concatenate-protocol.md` (read when Step 5 executes - final concatenation)

3. **Handle errors:** If step fails, ask user to retry or exit. Save current state for resume capability.

4. **Display progress:** "Progress: [X/6] steps complete", show estimated remaining time

5. **Step 4 Completion Pause:** After Step 4 completes, pause and display the Protocol Completion Menu (see below). Wait for user selection before proceeding.

**Step 2.5: Protocol Completion Menu**

After Step 4 completes successfully, display the EXACT menu below (do not improvise or create alternative options):

```
PROTOCOL COMPLETE: Protocol Draft Generated

Protocol Details:
  - Study Design: [Design from metadata]
  - Sample Size: [N subjects from metadata]
  - Primary Endpoint: [Endpoint from metadata]
  - Study Duration: [Duration from metadata]

Protocol file: waypoints/02_protocol_draft.md
File size: [Size in KB]

WHAT WOULD YOU LIKE TO DO NEXT?

1. Review Protocol in Artifact - click on the .md file above

2. Concatenate Final Protocol (Step 5)

3. Exit and Review Later

```

**Option 1 Logic (Review in Artifact):**
Pause, let user open the section files, wait for further instruction

**Option 2 Logic (Concatenate Protocol):**
1. Execute Step 5 by reading and following `references/05-concatenate-protocol.md`
2. Step 5 will concatenate all section files into final protocol document
3. Continue to Step 3 (Final Summary) after Step 5 completes

**Option 3 Logic (Exit):**
1. Display: "Protocol sections saved. You can resume with Step 5 anytime to concatenate."
2. Exit orchestrator gracefully

**Step 3: Final Summary**

Display completion message with:
- Intervention name, type (device/drug), indication
- Protocol details (design, sample size, endpoints, duration)
- All completed steps list
- Final deliverable: Complete protocol markdown file location (waypoints/protocol_complete.md)
- Waypoint files list for reference
- Important disclaimers (FDA Pre-Sub, biostatistician review, IRB approval required)
- Thank you message
