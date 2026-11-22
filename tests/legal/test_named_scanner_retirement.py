"""Issue 3854 after retirement: absence must never become scan coverage.

The oracle is independent of the removed resolver: a missing executable cannot
inspect a fixture or establish PASS. Issue 3936 and FINAL_REPORT_VERIFICATION.md
require retirement rather than resolver repair. Fixture contents are synthetic.
"""

import importlib.util
import subprocess
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCANNER = Path("scripts/legal/legal-sanity-scan.sh")
SPEC = importlib.util.spec_from_file_location(
    "identifier_gate_retirement", ROOT / "tests/legal/test_identifier_gate_retirement.py"
)
RETIREMENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RETIREMENT)


@pytest.mark.parametrize("entry", ["file", "directory", "dangling-link"])
def test_absence_guard_rejects_any_recreated_scanner(tmp_path, entry):
    """Hand oracle: each created directory entry contradicts retirement.

    A dangling link has a directory entry even though Path.exists() is false.
    A file printing PASS would recreate precisely the unsupported success claim.
    """
    scanner = tmp_path / SCANNER
    scanner.parent.mkdir(parents=True)
    if entry == "file":
        scanner.write_text("printf 'PASS\\n'\n", encoding="utf-8")
    elif entry == "directory":
        scanner.mkdir()
    else:
        scanner.symlink_to(scanner.parent / "missing-target")
    case = RETIREMENT.RetirementTests(
        "test_scanner_is_removed_not_replaced_with_fake_pass"
    )
    with mock.patch.object(RETIREMENT, "ROOT", tmp_path), pytest.raises(AssertionError):
        case.test_scanner_is_removed_not_replaced_with_fake_pass()


@pytest.mark.parametrize("layout", ["nested", "sibling"])
@pytest.mark.parametrize(
    "argument", ["--repo=fixture-repo", "--repo=", "--repo=missing-repo", "--all"]
)
def test_legacy_invocation_cannot_claim_coverage(tmp_path, layout, argument):
    """Hand oracle: no scanner means failure, no scan, and no PASS.

    Nested: workspace/hub/fixture-repo. Sibling: workspace/fixture-repo.
    A synthetic marker establishes that a real input exists; retirement means
    the input is NOT inspected. This test makes no identifier-screening claim.
    """
    hub = tmp_path / "workspace" / "hub"
    hub.mkdir(parents=True)
    fixture = (hub if layout == "nested" else hub.parent) / "fixture-repo"
    fixture.mkdir()
    marker = fixture / "sentinel.txt"
    contents = "synthetic coverage marker\n"
    marker.write_text(contents, encoding="utf-8")
    # Use the actual checkout entry point, never a copied or replacement scanner.
    result = subprocess.run(
        ["bash", str(ROOT / SCANNER), argument],
        cwd=hub,
        env={"PATH": "/usr/bin:/bin", "LEGAL_SCAN_REPO_ROOTS": str(hub.parent)},
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "PASS" not in result.stdout + result.stderr
    assert "Scanning:" not in result.stdout + result.stderr
    assert marker.read_text(encoding="utf-8") == contents
