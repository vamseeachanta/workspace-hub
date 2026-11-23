---
name: yaml-workflow-executor-command-line-interface
description: 'Sub-skill of yaml-workflow-executor: Command-Line Interface (+1).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Command-Line Interface (+1)

## Command-Line Interface


```python
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Execute YAML-defined workflows'
    )
    parser.add_argument(
        'config',

*See sub-skills for full details.*

## Bash Wrapper


```bash
#!/bin/bash
# scripts/run_workflow.sh

CONFIG_FILE="${1:?Usage: $0 <config.yaml> [--override key=value]}"
shift

# Activate environment if needed
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run workflow
python -m workflow_executor "$CONFIG_FILE" "$@"
```
