---
name: orcaflex-post-processing-parallel-processing-details
description: 'Sub-skill of orcaflex-post-processing: Parallel Processing Details.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Parallel Processing Details

## Parallel Processing Details


The OPP module uses `ProcessPoolExecutor` for efficient batch processing:

```python
# From opp.py - parallel processing pattern
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_sim_files_parallel(sim_files, cfg, max_workers=4):
    """Process multiple .sim files in parallel."""
    results = {}

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_single_sim, f, cfg): f
            for f in sim_files
        }

        for future in as_completed(future_to_file):
            file_name = future_to_file[future]
            try:
                result = future.result()
                results[file_name] = result
            except Exception as e:
                results[file_name] = {"error": str(e)}

    return results
```
