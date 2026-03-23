---
name: stage-08-claim-activation
description: "Stage 08: Claim / Activation"
version: 1.0.0
category: workspace-hub
type: skill
stage_order: 8
invocation: chained_agent
weight: light
human_gate: False
---

Stage 8 · Claim / Activation | chained_agent | light | single-thread
Entry: evidence/plan-final-review.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Read agent-quota-latest.json; assess proceed/pause
2. Write evidence/claim-evidence.yaml (quota snapshot, proceed decision)
3. Update working/WRK-NNN.md (status: working, activated_at)
4. Write evidence/activation.yaml (activated_at, gates_confirmed)
Exit: evidence/claim-evidence.yaml + evidence/activation.yaml + working/WRK-NNN.md
