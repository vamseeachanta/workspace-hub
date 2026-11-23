"""Tests for verdict normalization across review providers (#1736)."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
NORMALIZER = REPO_ROOT / "scripts" / "review" / "normalize-verdicts.sh"


def _normalize(text: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
        handle.write(text)
        path = Path(handle.name)
    try:
        result = subprocess.run(
            ["bash", str(NORMALIZER), str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    finally:
        path.unlink(missing_ok=True)


def test_normalizes_request_changes_variants_to_major():
    assert _normalize("### Verdict: REQUEST_CHANGES\n### Summary\ntext\n### Issues Found\n- [P1] bad\n### Suggestions\n- fix\n### Questions for Author\n- none") == "MAJOR"
    assert _normalize("### Verdict: changes-requested\n### Summary\ntext\n### Issues Found\n- [P2] bad\n### Suggestions\n- fix\n### Questions for Author\n- none") == "MAJOR"
    assert _normalize("### Verdict: REVISION NEEDED\n### Summary\ntext\n### Issues Found\n- [P2] bad\n### Suggestions\n- fix\n### Questions for Author\n- none") == "MAJOR"


def test_normalizes_no_findings_to_approve():
    assert _normalize("### Verdict: No findings\n### Summary\nclean\n### Issues Found\n- None.\n### Suggestions\n- None.\n### Questions for Author\n- None.") == "APPROVE"
