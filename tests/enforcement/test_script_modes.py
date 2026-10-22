"""Index policy fixtures, with independent hand-assigned Git modes.

Git 2.44.0 git-ls-files --stage documents mode/object/stage/path records;
git-update-index --chmod defines executable index changes independently of disk.
The three-file example has one non-executable shebang, one executable shebang,
and one executable text file: exactly two findings, one blocking the guard.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "scripts/enforcement/audit_script_modes.py"


def git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(root), *args], env=env, check=True,
        capture_output=True, text=True,
    ).stdout


def fixture(tmp_path):
    git(tmp_path, "init", "-q")
    for name, content, mode in (
        ("needs exec.sh", "#!/bin/sh\ntrue\n", "-x"),
        ("run.sh", "#!/bin/sh\ntrue\n", "+x"),
        ("plain.txt", "plain text\n", "+x"),
    ):
        (tmp_path / name).write_text(content)
        git(tmp_path, "add", "--", name)
        git(tmp_path, "update-index", f"--chmod={mode}", "--", name)


def audit(root, *args, env=None):
    return subprocess.run(
        [sys.executable, str(AUDIT), "--repo", str(root), *args],
        env=env, text=True, capture_output=True, check=False,
    )


def test_audit_index_modes_not_physical_modes(tmp_path):
    fixture(tmp_path)
    # Index +x remains authoritative even after the physical bit is cleared.
    (tmp_path / "run.sh").chmod(0o644)
    result = audit(tmp_path)
    assert result.returncode == 0, result.stderr
    records = json.loads(result.stdout)
    assert [(r["path"], r["mode"], r["kind"]) for r in records] == [
        ("needs exec.sh", "100644", "shebang_without_exec"),
        ("plain.txt", "100755", "exec_without_shebang"),
    ]
    table = audit(tmp_path, "--format", "table")
    assert "| needs exec.sh | 100644 | shebang_without_exec |" in table.stdout


def test_guard_new_non_executable_script_and_exact_exemption(tmp_path):
    fixture(tmp_path)
    assert audit(tmp_path, "--check").returncode == 1
    exemptions = tmp_path / "exemptions.json"
    exemptions.write_text(json.dumps({"needs exec.sh": "Sourced fixture library."}))
    assert audit(tmp_path, "--check", "--exemptions", str(exemptions)).returncode == 0
    (tmp_path / "new.sh").write_text("#!/bin/sh\ntrue\n")
    git(tmp_path, "add", "--", "new.sh")
    git(tmp_path, "update-index", "--chmod=-x", "--", "new.sh")
    assert audit(tmp_path, "--check", "--exemptions", str(exemptions)).returncode == 1


def test_audit_uses_index_bytes_and_clears_inherited_binding(tmp_path):
    fixture(tmp_path)
    before = git(tmp_path, "ls-files", "--stage")
    (tmp_path / "needs exec.sh").write_text("no shebang in working tree\n")
    result = audit(tmp_path, env=os.environ | {
        "GIT_DIR": str(ROOT / ".git"), "GIT_WORK_TREE": str(ROOT),
        "GIT_COMMON_DIR": str(ROOT / ".git"),
    })
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)[0]["kind"] == "shebang_without_exec"
    assert git(tmp_path, "ls-files", "--stage") == before


def test_guard_rejects_broad_or_reasonless_exemptions(tmp_path):
    fixture(tmp_path)
    exemptions = tmp_path / "exemptions.json"
    for payload in ({"*.sh": "Too broad"}, {"run.sh": ""}):
        exemptions.write_text(json.dumps(payload))
        result = audit(tmp_path, "--check", "--exemptions", str(exemptions))
        assert result.returncode == 2
        assert "exemption" in result.stderr.lower()


def test_binary_shebang_and_unusual_path(tmp_path):
    """First two bytes define a shebang, including a NUL-bearing payload."""
    fixture(tmp_path)
    name = "binary\tfile.sh"
    (tmp_path / name).write_bytes(b"#!/bin/sh\n\0payload")
    git(tmp_path, "add", "--", name)
    git(tmp_path, "update-index", "--chmod=-x", "--", name)
    result = audit(tmp_path)
    assert result.returncode == 0, result.stderr
    assert any(r["path"] == name for r in json.loads(result.stdout))
    assert "binary\\tfile.sh" in audit(tmp_path, "--format", "table").stdout
