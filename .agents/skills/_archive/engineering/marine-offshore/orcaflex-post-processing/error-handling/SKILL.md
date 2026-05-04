---
name: orcaflex-post-processing-error-handling
description: 'Sub-skill of orcaflex-post-processing: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Issues


1. **Missing .sim file**
   ```python
   if not Path(sim_file).exists():
       logger.error(f"Simulation file not found: {sim_file}")
   ```

2. **Invalid variable name**
   ```python
   try:
       data = line.TimeHistory(variable_name)

*See sub-skills for full details.*
