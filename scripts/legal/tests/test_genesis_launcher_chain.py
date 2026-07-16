"""RED contracts for launcher-to-broker argv/environment/FD chaining."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAUNCHER = ROOT / "scripts/legal/launch_rule_authority_genesis.sh"


def test_chain_uses_exact_internal_entry_and_clean_environment():
    source = LAUNCHER.read_text(encoding="utf-8")
    assert "LC_ALL=C" in source
    assert "LEGAL_RULE_OWNER_GENESIS=1" in source
    assert "--outer-identity-fd" in source
    assert "--approval-record" in source
    assert "--execution-manifest-fd" in source or "execution_manifest" in source
    assert "--internal-genesis" in source


def test_chain_rejects_actions_and_does_not_emit_child_output():
    result = subprocess.run(
        ["/bin/bash", str(LAUNCHER), "genesis-current"],
        env={"LEGAL_RULE_OWNER_GENESIS": "1", "GITHUB_ACTIONS": "true"},
        text=True, capture_output=True, check=False,
    )
    assert result.returncode != 0
    assert result.stdout == ""


def test_chain_does_not_forward_unrelated_fd(tmp_path):
    fd = os.open("/dev/null", os.O_RDONLY)
    try:
        result = subprocess.run(
            ["/bin/bash", str(LAUNCHER), "genesis-current"],
            env={"LEGAL_RULE_OWNER_GENESIS": "1"}, pass_fds=(fd,),
            text=True, capture_output=True, check=False,
        )
    finally:
        os.close(fd)
    assert result.returncode != 0
    assert result.stdout == ""
