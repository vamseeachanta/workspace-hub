---
name: yaml-workflow-executor-do
description: 'Sub-skill of yaml-workflow-executor: Do (+4).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Do (+4)

## Do


1. Keep configs in `config/workflows/` directory
2. Use descriptive filenames: `<domain>_<task>_<variant>.yaml`
3. Version control all configurations
4. Use comments to document parameters
5. Validate configs before execution with `--dry-run`
6. Log sufficient context for debugging


## Don't


1. Hardcode absolute paths
2. Skip input validation
3. Mix configuration with implementation
4. Create overly complex nested configs
5. Ignore error handling


## Configuration Design

- Keep configs in `config/workflows/` directory
- Use descriptive filenames: `<domain>_<task>_<variant>.yaml`
- Version control all configurations
- Use comments to document parameters


## Handler Development

- One handler per task type
- Validate inputs at handler start
- Log progress for long-running tasks
- Return structured results


## File Organization

```
project/
    config/
        workflows/           # Workflow configs
            analysis.yaml
            transform.yaml
        schemas/             # Validation schemas
    src/
        workflow_executor/   # Executor code
    scripts/
        run_workflow.sh      # CLI wrapper
    data/
        raw/
        processed/
        results/
```
