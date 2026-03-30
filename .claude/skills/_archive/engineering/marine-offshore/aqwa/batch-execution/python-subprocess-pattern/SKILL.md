---
name: aqwa-batch-execution-python-subprocess-pattern
description: 'Sub-skill of aqwa-batch-execution: Python Subprocess Pattern.'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Python Subprocess Pattern

## Python Subprocess Pattern


```python
import subprocess
from pathlib import Path

AQWA_EXE = Path("/ansys_inc/v251/aqwa/bin/lnx64/Aqwa")

def run_aqwa(work_dir: Path, job_name: str, job_type: str = "std") -> bool:
    """Run AQWA batch. Returns True on success."""
    result = subprocess.run(
        [str(AQWA_EXE), job_type, job_name],
        cwd=str(work_dir), capture_output=True, text=True,
    )
    mes = (work_dir / f"{job_name}.mes")
    if mes.exists() and any(
        kw in mes.read_text(errors="replace").upper()
        for kw in ("ERROR", "FATAL", "ABORT")
    ):
        return False
    return (work_dir / f"{job_name}.res").exists()
```
