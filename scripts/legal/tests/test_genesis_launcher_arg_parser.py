"""RED strict canonical launcher argument transport contract."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from genesis_launcher_args import parse_launcher_args

def test_parser_preserves_canonical_pairs_and_rejects_unknowns():
    argv = ["genesis-current", "--tool-repo", "repo", "--tool-sha", "a"*40,
            "--out-parent", "/home/user/out", "--transaction-id", "12345678-1234-4234-9234-123456789abc",
            "--approval-record", "approval.json", "--approval-sha256", "b"*64,
            "--python-realpath", "/usr/bin/python3", "--python-sha256", "c"*64]
    parsed = parse_launcher_args(argv)
    assert parsed["command"] == "genesis-current"
    assert parsed["tool_repo"] == "repo"
    with pytest.raises(ValueError):
        parse_launcher_args(argv + ["--unknown", "x"])
