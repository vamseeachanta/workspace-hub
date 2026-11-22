"""Sentinel control-flow regressions using isolated process boundaries.

Exit values follow scripts/monitoring/equivalence-sentinel.sh's documented
contract. Expected ordering follows issue #3506: remote presence must be
established before successful health, independently of comparison drift.
No real fingerprint collector, Git publisher or assistant executable runs.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def windows_sentinel(monkeypatch, request):
    """Emulate Windows text writes while generating the isolated fixtures."""
    write_text = Path.write_text

    def windows_write_text(path, data, *args, **kwargs):
        kwargs.setdefault("newline", "\r\n")
        return write_text(path, data, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "write_text", windows_write_text)
        return request.getfixturevalue("sentinel")


@pytest.fixture
def sentinel(tmp_path):
    monitoring = tmp_path / "scripts" / "monitoring"
    library = tmp_path / "scripts" / "lib"
    monitoring.mkdir(parents=True)
    library.mkdir()
    shutil.copyfile(ROOT / "scripts/monitoring/equivalence-sentinel.sh",
                    monitoring / "equivalence-sentinel.sh")
    (library / "python-resolver.sh").write_text(
        f"PYTHON_CMD=({shlex.quote(sys.executable)})\n", encoding="utf-8", newline="\n")
    (monitoring / "equivalence-fingerprint.sh").write_text(
        '#!/usr/bin/env bash\n'
        'printf \'{"role":"contribute-minimal","machine_id":"sample"}\\n\' > "$2"\n',
        encoding="utf-8",
        newline="\n",
    )
    (monitoring / "equivalence_state.py").write_text('''
import json
import os
from pathlib import Path
import sys

def record(event):
    with open("events.txt", "a", encoding="utf-8") as handle:
        handle.write(event + "\\n")

def collect(repo):
    record("collect")
    return []

if __name__ == "__main__":
    command = sys.argv[1]
    record(command)
    if command == "publish":
        sys.exit(int(os.environ.get("PUBLISH_RC", "0")))
    if command == "verify-publish":
        sys.exit(int(os.environ.get("VERIFY_RC", "0")))
    if command == "write-health":
        if os.environ.get("HEALTH_FAIL"):
            sys.exit(1)
        args = dict(zip(sys.argv[2::2], sys.argv[3::2]))
        Path(args["--health"]).write_text(json.dumps({
            "phase": args["--phase"], "rc": int(args["--rc"]),
            "duration_s": float(args["--duration"]),
        }), encoding="utf-8")
''', encoding="utf-8")
    (monitoring / "equivalence_compare.py").write_text('''
import os
CRITICAL = "CRITICAL"
WARNING = "WARNING"
def load_expected_machines(path):
    return []
def compare(fps, expected_machines=None):
    return []
def worst_severity(divs):
    return WARNING if os.environ.get("DRIFT") else "INFO"
''', encoding="utf-8")
    binary = tmp_path / "bin"
    binary.mkdir()
    # Force the script's documented cwd fallback; no Git repository is needed.
    git = binary / "git"
    git.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8", newline="\n")
    git.chmod(0o755)

    def run(**overrides):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith("GIT_") and key not in {
                   "EQUIV_ALERT_ISSUE", "PUBLISH_RC", "VERIFY_RC", "HEALTH_FAIL", "DRIFT",
               }}
        env.update(PATH=str(binary) + os.pathsep + os.environ["PATH"], **overrides)
        result = subprocess.run(["bash", str(monitoring / "equivalence-sentinel.sh")],
                                check=False, cwd=tmp_path, env=env, capture_output=True, text=True,
                                # Same process bound as test_windows_scheduler_single_source.py.
                                timeout=30)
        events = (tmp_path / "events.txt").read_text().splitlines()
        health = json.loads((tmp_path / ".claude/state/equivalence/publish-health.json").read_text()) \
            if not overrides.get("HEALTH_FAIL") else None
        return result, events, health

    return run


def test_generated_shell_fixtures_use_lf(windows_sentinel, tmp_path):
    """Shell fixtures retain LF bytes even when text writes default to CRLF."""
    for relative in (
        "scripts/lib/python-resolver.sh",
        "scripts/monitoring/equivalence-fingerprint.sh",
        "bin/git",
    ):
        content = (tmp_path / relative).read_bytes()
        assert b"\n" in content, relative
        assert b"\r" not in content, relative

    result, events, health = windows_sentinel()
    assert result.returncode == 0, result.stderr
    assert events == ["prepare", "publish", "verify-publish", "write-health", "collect"]
    assert health["rc"] == 0


@pytest.mark.parametrize("verify_rc", ["1", "2", "3"])
def test_readback_failure_never_records_success_or_compares(sentinel, verify_rc):
    """Hand trace: push succeeds, read-back fails, health retains failure;
    the controller exits with its documented store-failure code, before collect.
    """
    result, events, health = sentinel(VERIFY_RC=verify_rc)
    assert result.returncode == 3, result.stderr
    assert events == ["prepare", "publish", "verify-publish", "write-health"]
    assert health["phase"] == "publish"
    assert health["rc"] == int(verify_rc)
    assert "publish failed" in result.stderr


def test_verified_success_records_health_before_comparing(sentinel):
    """Hand trace: verification precedes successful health, then collection."""
    result, events, health = sentinel()
    assert result.returncode == 0, result.stderr
    assert events == ["prepare", "publish", "verify-publish", "write-health", "collect"]
    assert health["rc"] == 0
    assert health["phase"] == "publish"
    assert health["duration_s"] >= 0


def test_publish_failure_keeps_precedence_and_skips_readback(sentinel):
    """A failed push already disproves success; verification must not run."""
    result, events, health = sentinel(PUBLISH_RC="3")
    assert result.returncode == 3, result.stderr
    assert events == ["prepare", "publish", "write-health"]
    assert health["rc"] == 3


def test_other_drift_preserves_verified_publish_health(sentinel):
    """Comparison WARNING exits one but must retain successful publish health."""
    result, events, health = sentinel(DRIFT="1")
    assert result.returncode == 1, result.stderr
    assert events[-1] == "collect"
    assert health["rc"] == 0


def test_health_persistence_failure_after_verification_exits_four(sentinel):
    """The documented health-write failure dominates a successful read-back."""
    result, events, health = sentinel(HEALTH_FAIL="1")
    assert result.returncode == 4, result.stderr
    assert events == ["prepare", "publish", "verify-publish", "write-health"]
    assert health is None
