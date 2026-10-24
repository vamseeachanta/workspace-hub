"""Legacy empty-target commands cannot supply successful scan evidence.

Basis: FINAL_REPORT_VERIFICATION.md, retirement decision dated 2026-10-03;
historical CLI: legal-sanity-scan.sh at the parent of commit d6f08dd9c.
These tests exercise retirement, not a replacement resolver or identifier gate.
"""

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCANNER = ROOT / "scripts/legal/legal-sanity-scan.sh"


@pytest.mark.parametrize(
    ("arguments", "registration"),
    [
        pytest.param(["--repo=fixture"], "unset", id="named-repository"),
        pytest.param(["--repo="], "unset", id="empty-repository"),
        pytest.param(["--repo=missing"], "unset", id="missing-repository"),
        pytest.param(["--all"], "unset", id="all-without-registration"),
        pytest.param(["--all"], "empty", id="all-with-empty-registration"),
        pytest.param(["--all"], "existing", id="all-with-explicit-root"),
        pytest.param(["--repo=fixture"], "existing", id="named-explicit-root"),
        pytest.param(["--all"], "missing", id="all-with-missing-root"),
        pytest.param(
            ["--all"], "existing-and-missing", id="all-with-mixed-roots"
        ),
    ],
)
def test_legacy_commands_cannot_report_pass(tmp_path, arguments, registration):
    """Independent expectation: an absent entry point cannot scan any file.

    With no executable scanner, successful scan evidence is the empty set.
    Therefore a successful process status (zero) or a PASS verdict is invalid.
    The exact shell failure status is deliberately not part of this contract.
    A synthetic file demonstrates that registered content remains untouched.
    """
    assert not SCANNER.exists(), "Retirement forbids restoring the scanner"
    assert not SCANNER.is_symlink(), "A scanner link must not survive retirement"

    checkout = tmp_path / "registered root" / "fixture"
    checkout.mkdir(parents=True)
    payload = checkout / "input.txt"
    content = "Synthetic content for a retired command.\n"
    payload.write_text(content, encoding="utf-8")
    missing = tmp_path / "missing root"

    environment = os.environ.copy()
    environment.pop("LEGAL_SCAN_REPO_ROOTS", None)
    environment.pop("LEGAL_SCAN_RESOLVE_ONLY", None)
    roots = {
        "empty": "",
        "existing": str(checkout),
        "missing": str(missing),
        "existing-and-missing": f"{checkout};{missing}",
    }
    if registration != "unset":
        environment["LEGAL_SCAN_REPO_ROOTS"] = roots[registration]

    # The absence assertions above prevent executing a reintroduced scanner.
    result = subprocess.run(
        ["bash", str(SCANNER), *arguments],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "PASS" not in result.stdout
    assert "PASS" not in result.stderr
    assert payload.read_text(encoding="utf-8") == content
    assert set(tmp_path.rglob("*")) == {
        checkout.parent,
        checkout,
        payload,
    }
