"""Extract VBA source from .xlsm files. Safety: VBA is NEVER eval'd."""

from __future__ import annotations

import re
from typing import Any, Dict, List

# VBA Function/Sub signature pattern
_VBA_SIG_RE = re.compile(
    r"^\s*(?:Public\s+|Private\s+)?"
    r"(Function|Sub)\s+"
    r"(\w+)\s*"
    r"\(([^)]*)\)",
    re.IGNORECASE | re.MULTILINE,
)


def extract_vba_modules(filepath: str) -> List[Dict[str, Any]]:
    """Extract VBA source from .xlsm files.

    Returns list of dicts compatible with VbaModule dataclass fields:
        filename, code, block_type, signatures.

    Requires oletools (olevba). If not installed, raises ImportError.
    VBA code is returned as a string — it is NEVER executed.
    """
    try:
        from oletools.olevba import VBA_Parser
    except ImportError:
        raise ImportError(
            "oletools is required for VBA extraction. "
            "Install with: uv add oletools"
        )

    modules: List[Dict[str, Any]] = []
    vba_parser = VBA_Parser(filepath)

    if not vba_parser.detect_vba_macros():
        vba_parser.close()
        return modules

    for filename, stream_path, vba_filename, vba_code in vba_parser.extract_macros():
        sigs = parse_vba_signatures(vba_code)
        block_type = "module"
        if sigs:
            first_type = sigs[0].split("(")[0].strip().split()[-2].lower()
            if first_type == "function":
                block_type = "function"
            elif first_type == "sub":
                block_type = "subroutine"

        modules.append(
            {
                "filename": vba_filename or filename or "unknown",
                "code": vba_code,
                "block_type": block_type,
                "signatures": sigs,
            }
        )

    vba_parser.close()
    return modules


def parse_vba_signatures(code: str) -> List[str]:
    """Extract Function/Sub signatures from VBA source code.

    Args:
        code: Raw VBA source text.

    Returns:
        List of signature strings, e.g. ['Function CalcArea(w, h)'].
    """
    if not code:
        return []

    sigs: List[str] = []
    for m in _VBA_SIG_RE.finditer(code):
        kind = m.group(1)  # Function or Sub
        name = m.group(2)
        params = m.group(3).strip()
        sigs.append(f"{kind} {name}({params})")

    return sigs
