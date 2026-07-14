from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "scripts/legal/manage_rule_authority.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)], text=True, capture_output=True
    )


def test_cli_rc0_public_and_rc2_schema(tmp_path):
    valid = run(
        "validate-public",
        "--registry",
        ROOT / "config/legal-rule-registry.json",
        "--policy",
        ROOT / "config/legal-rule-authority-policy.json",
    )
    assert valid.returncode == 0 and "verdict=verified rc=0" in valid.stdout
    bad = tmp_path / "bad.json"
    bad.write_text("{}\n", encoding="utf-8")
    invalid = run(
        "validate-public",
        "--registry",
        bad,
        "--policy",
        ROOT / "config/legal-rule-authority-policy.json",
    )
    assert invalid.returncode == 2 and "verdict=schema rc=2" in invalid.stderr


def test_cli_rc4_filesystem_is_fixed_and_redacted(tmp_path):
    missing = tmp_path / "private-sensitive-name"
    result = run(
        "validate-public",
        "--registry",
        missing,
        "--policy",
        ROOT / "config/legal-rule-authority-policy.json",
    )
    assert (
        result.returncode == 4
        and result.stderr.strip() == "command=authority verdict=filesystem rc=4"
    )
    assert str(missing) not in result.stderr


def test_cli_exposes_frozen_phase_a_commands():
    result = run("--help")
    for command in (
        "validate-public",
        "seal",
        "verify",
        "audit-tree",
        "audit-history",
        "cleanup-incomplete",
        "materialize-envelope",
    ):
        assert command in result.stdout
