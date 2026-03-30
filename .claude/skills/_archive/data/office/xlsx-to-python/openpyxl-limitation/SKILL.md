---
name: xlsx-to-python-openpyxl-limitation
description: 'Sub-skill of xlsx-to-python: openpyxl Limitation (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# openpyxl Limitation (+3)

## openpyxl Limitation


openpyxl can *preserve* VBA with `keep_vba=True` but treats `vbaProject.bin` as an
opaque binary blob — it cannot read the VBA source code.


## oletools/olevba — VBA Source Extraction


```python
from oletools.olevba import VBA_Parser

def extract_vba_code(filepath: str) -> list[dict]:
    """Extract VBA macro source code from .xlsm/.xls files."""
    macros = []
    try:
        vba_parser = VBA_Parser(filepath)
        if vba_parser.detect_vba_macros():
            for filename, stream_path, vba_filename, vba_code in vba_parser.extract_macros():
                macros.append({
                    "filename": vba_filename,
                    "stream_path": stream_path,
                    "code": vba_code,
                    "type": _classify_vba(vba_code),
                })
        vba_parser.close()
    except Exception as exc:
        macros.append({"error": str(exc)})
    return macros

def _classify_vba(code: str) -> str:
    """Classify VBA code block type."""
    code_lower = code.lower()
    if "function " in code_lower:
        return "function"       # Custom functions called from cell formulas
    elif "sub " in code_lower:
        return "subroutine"     # Macros / event handlers
    elif "type " in code_lower:
        return "type_definition" # User-defined types
    return "module"             # Module-level code
```


## VBA → Python Translation Patterns


| VBA Pattern | Python Equivalent |
|-------------|------------------|
| `Function CalcStress(P, D, t) As Double` | `def calc_stress(p: float, d: float, t: float) -> float:` |
| `Dim x As Double` | `x: float` (type annotation) |
| `If ... Then ... ElseIf ... End If` | `if ... elif ... else:` |
| `For i = 1 To N ... Next i` | `for i in range(1, n + 1):` |
| `Do While ... Loop` | `while ...:` |
| `Application.WorksheetFunction.VLookup(...)` | `np.interp(...)` or dict lookup |
| `GoTo ErrorHandler` | `try/except` |
| `ReDim arr(1 To N)` | `arr = [0.0] * n` |
| `Cells(row, col).Value` | Function parameter or return value |


## When VBA Exists — Enhanced Extraction Flow


```
1. Detect .xlsm → extract VBA via oletools
2. Parse VBA Function/Sub signatures → Python function stubs
3. Extract formulas via openpyxl dual-pass (values + formulas)
4. Cross-reference: cell formulas that call VBA functions
5. VBA function body → Python implementation
6. Cell values → pytest assertions (same as non-macro path)
```

VBA functions are often called from cell formulas as UDFs (User Defined Functions).
When a formula like `=CalcStress(B2, B3, B4)` is found, the VBA `Function CalcStress`
provides the implementation and the cell value provides the test assertion.
