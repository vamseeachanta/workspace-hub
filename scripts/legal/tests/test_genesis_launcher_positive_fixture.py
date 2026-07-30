"""RED positive child-capture contract; no authority activation."""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAUNCHER = ROOT / "scripts/legal/launch_rule_authority_genesis.sh"

def test_launcher_forwards_canonical_argv_and_clean_env(tmp_path):
    child = tmp_path / "internal_entry.py"
    child.write_text("import json,os,sys; print(json.dumps({'argv':sys.argv[1:],'env':dict(os.environ),'fds':sorted(int(x) for x in os.listdir('/proc/self/fd') if x.isdigit())}))")
    result = subprocess.run(["/bin/bash", str(LAUNCHER), "genesis-current",
        "--tool-repo", "repo", "--tool-sha", "a"*40, "--out-parent", str(tmp_path),
        "--transaction-id", "12345678-1234-4234-9234-123456789abc",
        "--approval-record", str(child), "--approval-sha256", "b"*64,
        "--python-realpath", sys.executable, "--python-sha256", "c"*64,
        "--outer-identity-fd", "9", "--outer-bootstrap-sha256", "d"*64],
        env={"LEGAL_RULE_OWNER_GENESIS":"1"}, text=True, capture_output=True)
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["env"] == {"LC_ALL":"C", "LEGAL_RULE_OWNER_GENESIS":"1"}
    assert payload["argv"][0] == "genesis-current"
