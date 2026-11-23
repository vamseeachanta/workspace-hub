---
name: hardware-assessment-workflow-multi-machine-inventory
description: 'Sub-skill of hardware-assessment: Workflow: Multi-Machine Inventory.'
version: 1.1.0
category: operations
type: reference
scripts_exempt: true
---

# Workflow: Multi-Machine Inventory

## Workflow: Multi-Machine Inventory


```bash
# 1. Copy script to each machine and run
scp hardware-assess.sh user@machine1:~/
ssh user@machine1 'bash ~/hardware-assess.sh -p -q'
scp user@machine1:~/hardware-assessment-*.json ./inventory/

# 2. Compare results
python3 -c "
import json, glob
for f in sorted(glob.glob('inventory/*.json')):
    d = json.load(open(f))
    cpu = d['cpu']
    mem = d['memory']
    gpus = d.get('gpu', [])
    gpu_str = gpus[0]['name'] if gpus else 'None'
    print(f\"{d['os']['hostname']:20s} | {cpu['model']:40s} | {cpu['total_cores']}C/{cpu['total_threads']}T | {mem['total_gb']} GB | {gpu_str}\")
"
```
