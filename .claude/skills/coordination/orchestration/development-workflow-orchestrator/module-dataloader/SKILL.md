---
name: development-workflow-orchestrator-module-dataloader
description: 'Sub-skill of development-workflow-orchestrator: Module: DataLoader.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Module: DataLoader

## Module: DataLoader


```
FUNCTION load_csv(file_path, config):
  VALIDATE file_path is relative
  CHECK file_size <= config.max_size_mb
  READ csv_data FROM file_path

  IF validation_enabled:
    VALIDATE required_columns exist
    VALIDATE data_types are correct

  IF validation_fails:
    RAISE ValidationError with details

  RETURN csv_data
```
