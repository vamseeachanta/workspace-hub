---
name: aqwa-batch-execution-detecting-success-vs-failure
description: 'Sub-skill of aqwa-batch-execution: Detecting Success vs. Failure (+2).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Detecting Success vs. Failure (+2)

## Detecting Success vs. Failure


```bash
# 1. Check .MES first (most direct failure indicator)
grep -qi "error\|fatal\|abort" analysis.mes && echo "FAILED"

# 2. Check for .RES (produced only on successful Stage 1 completion)
[ -f analysis.res ] || echo "NO RESTART FILE — run failed"

# 3. Check .LIS for completion marker (exact string is version-dependent)
grep -i "analysis complete\|normal termination" analysis.lis

# 4. Count panels processed (sanity check)
grep "TOTAL NUMBER OF PANELS" analysis.lis
```


## Parsing RAOs from `.LIS` (Python)


```python
import re
from pathlib import Path

def check_lis_success(lis_path: Path) -> bool:
    text = lis_path.read_text(errors="replace")
    if re.search(r"FATAL ERROR|ERROR DETECTED", text, re.IGNORECASE):
        return False
    if re.search(r"ANALYSIS COMPLETE|NORMAL TERMINATION", text, re.IGNORECASE):
        return True
    return False  # inconclusive

def parse_rao_block(lis_path: Path) -> list[dict]:
    """Extract RAO amplitude/phase from AQWA-LINE .LIS (fixed-column format)."""
    text = lis_path.read_text(errors="replace")
    # First RAO section = displacement RAOs; skip velocity/acceleration
    blocks = re.findall(
        r"WAVE FREQUENCY\s*=\s*([\d.]+)(.*?)(?=WAVE FREQUENCY|\Z)",
        text, re.DOTALL
    )
    results = []
    for freq_str, block in blocks:
        rows = re.findall(
            r"([\d.]+)\s+" + r"([\d.]+)\s+([-\d.]+)\s+" * 6,
            block
        )
        results.append({"freq_rad_s": float(freq_str), "rows": rows})
    return results
```


## AqwaReader Batch Export


AqwaReader extracts results to CSV without the GUI. On Windows it must run via `workbench.bat`:

```bat
rem Windows — must use workbench.bat wrapper
"C:\Program Files\ANSYS Inc\v251\aisol\workbench.bat" -cmd ^
  "C:\Program Files\ANSYS Inc\v251\aisol\bin\winx64\AqwaReader.exe" ^
  --Type Graphical ^
  --InFile analysis.plt ^
  --OutFile results\rao ^
  --Format csv ^
  --Struct 1 --Freq 1 --Dir 1 ^
  --PLT1 1 --PLT2 1 --PLT3 1 --PLT4 3
```

On Linux, run AqwaReader without the wrapper (path follows same `lnx64` convention).
After any interactive AqwaReader session, it prints the exact command-line used — copy
this into your script and loop over `--Freq` and `--Dir` indices.
