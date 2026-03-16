---
name: agent-router-execution-checklist
description: 'Sub-skill of agent-router: Execution Checklist.'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


- [ ] Verify `jq` is installed
- [ ] Confirm at least one provider CLI is available
- [ ] Check provider profiles exist in `config/`
- [ ] Run `route.sh --config` to verify setup
- [ ] Test with a known task: `route.sh "what is Python?"`
