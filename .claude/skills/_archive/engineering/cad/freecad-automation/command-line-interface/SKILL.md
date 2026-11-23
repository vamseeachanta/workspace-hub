---
name: freecad-automation-command-line-interface
description: 'Sub-skill of freecad-automation: Command Line Interface.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Command Line Interface

## Command Line Interface


```bash
# Show capabilities
python run_freecad_agent.py --show-capabilities

# Process single file
python run_freecad_agent.py --file model.FCStd --operation "add fillet radius 5mm"

# Batch processing
python run_freecad_agent.py \
    --pattern "*.FCStd" \
    --input-directory ./models \
    --output-directory ./exports \
    --parallel 4

# Natural language command
python run_freecad_agent.py \
    --prompt "Create a hull with 150m length and 25m beam"
```
