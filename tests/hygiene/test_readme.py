"""Run the documented example verbatim, with temporary output outside the tree."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("inherited", [False, True])
def test_readme_example(tmp_path, inherited):
    """Hand calculation: 1 stray 'abc' = 3 bytes; one repo/cache excluded.

    mtime is set to 10 seconds, so both extrema are 10. The README excerpt
    must match the actual fields and its summary must match actual stdout.
    """
    readme = (ROOT / "scripts/hygiene/README.md").read_text(encoding="utf-8")
    code = re.search(r"```python\n(.*?)\n```", readme, re.DOTALL).group(1)
    env = dict(os.environ, TMPDIR=str(tmp_path))
    caller = tmp_path / "caller"
    caller.mkdir()
    clean = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    subprocess.run(["git", "init", "--quiet", str(caller)], env=clean, check=True)
    (caller / "untouched").write_bytes(b"preserve")
    before = {
        path.relative_to(caller).as_posix(): path.read_bytes()
        for path in caller.rglob("*")
        if path.is_file()
    }
    if inherited:
        env.update(
            {
                "GIT_DIR": str(caller / ".git"),
                "GIT_WORK_TREE": str(caller),
                "GIT_COMMON_DIR": str(caller / ".git"),
            }
        )
    result = subprocess.run(
        [sys.executable, "-I", "-c", code],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == "stray_files=1 bytes=3 repositories=1\n"
    (manifest_path,) = tmp_path.glob("inventory-example-*/manifest.json")
    actual = json.loads(manifest_path.read_text(encoding="utf-8"))
    excerpt = json.loads(re.search(r"```json\n(.*?)\n```", readme, re.DOTALL).group(1))
    assert {key: actual[key] for key in excerpt} == excerpt
    assert actual["totals"]["bytes"] == 3
    assert actual["totals"]["count"] == 1
    assert actual["totals"]["oldest_mtime"] == 10
    assert actual["totals"]["newest_mtime"] == 10
    assert "```text\n" + result.stdout + "```" in readme

    after = {
        path.relative_to(caller).as_posix(): path.read_bytes()
        for path in caller.rglob("*")
        if path.is_file()
    }
    assert after == before
    assert (manifest_path.parent / "tree/repo/.git").is_dir()
    assert {path.name for path in tmp_path.iterdir()} == {
        caller.name,
        manifest_path.parent.name,
    }
