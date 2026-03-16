---
name: development-workflow-orchestrator-complete-automation-script
description: 'Sub-skill of development-workflow-orchestrator: Complete Automation
  Script.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Complete Automation Script

## Complete Automation Script


```bash
#!/bin/bash
# scripts/workflow_orchestrator.sh

set -e

FEATURE_NAME="$1"

if [ -z "$FEATURE_NAME" ]; then
    echo "Usage: ./scripts/workflow_orchestrator.sh <feature-name>"

*See sub-skills for full details.*
