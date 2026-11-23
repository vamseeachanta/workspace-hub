---
name: background-service-manager-execution-checklist
description: 'Sub-skill of background-service-manager: Execution Checklist.'
version: 2.0.0
category: operations
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


Before creating service:
- [ ] Process command identified
- [ ] Working directory determined
- [ ] Log location decided (/tmp/ or dedicated dir)
- [ ] Environment variables documented

During setup:
- [ ] Service script created
- [ ] Made executable (chmod +x)
- [ ] SERVICE_CMD customized
- [ ] PID/LOG paths appropriate

After deployment:
- [ ] Service starts correctly
- [ ] Logs capture output
- [ ] Status shows running
- [ ] Stop gracefully terminates
- [ ] Restart works properly
