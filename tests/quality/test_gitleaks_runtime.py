"""Live controls for the pinned Gitleaks detection contract.

Source: Gitleaks v8.21.2 config/gitleaks.toml, aws-access-token:
https://github.com/gitleaks/gitleaks/blob/v8.21.2/config/gitleaks.toml
The rule requires an AKIA prefix, sixteen uppercase letters/digits and entropy
above three bits. The synthetic input has twenty symbols, with one repeated
twice: entropy = log2(20) - 2/20, which exceeds three. It does not end in
the rule's excluded example suffix. This is an independent hand calculation,
not an expected value obtained from the checker. No credential is used.

CLI and redaction: https://github.com/gitleaks/gitleaks/blob/v8.21.2/README.md
History uses detect; staged content uses protect --staged, as described by
scripts/security/secrets-scan.sh. The empty custom configuration is the
counterexample from issue 3552: no extension means no default detector.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GITLEAKS = shutil.which("gitleaks")
requires_gitleaks = pytest.mark.skipif(
    GITLEAKS is None,
    reason="NOT_EVALUATED: gitleaks binary absent; live detection requires Gitleaks",
)


def _git(repo: Path, *args: str, data: bytes | None = None) -> bytes:
    # Isolate temporary Git state from caller metadata and inherited bindings.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    result = subprocess.run(
        ["git", "-C", str(repo), *args], input=data, capture_output=True, env=env,
        check=False,
    )
    if result.returncode:
        pytest.fail("temporary repository setup failed; output withheld", pytrace=False)
    return result.stdout


def _history_entry(repo: Path, content: bytes) -> None:
    # Fast-import builds disposable history with a synthetic author.
    # Format: https://git-scm.com/docs/git-fast-import (commit, data, filemodify).
    previous = _git(repo, "for-each-ref", "--format=%(objectname)", "refs/heads/main").strip()
    parent = b"from " + previous + b"\n" if previous else b""
    message = b"control\n"
    _git(repo, "fast-import", "--quiet", data=(
        b"commit refs/heads/main\ncommitter Fixture <> 0 +0000\n"
        + f"data {len(message)}\n".encode() + message + parent
        + b"M 100644 inline control.txt\n"
        + f"data {len(content)}\n".encode() + content + b"\n"
    ))


@pytest.mark.parametrize("mode", ["staged", "history"])
@pytest.mark.parametrize("positive", [False, True], ids=["benign", "positive"])
@requires_gitleaks
def test_live_detection_and_empty_config_control(
    tmp_path: Path, mode: str, positive: bool,
) -> None:
    repo = tmp_path / "repository"
    repo.mkdir()
    _git(repo, "init", "--quiet", "--initial-branch=main")
    benign = b"ordinary documentation\n"
    # Deliberately assembled only in the disposable test directory.
    token = "AKIA" + "B2C3D4E5" + "F6G7H8J9"
    content = (token + "\n").encode() if positive else benign
    if mode == "history":
        _history_entry(repo, content)
        _history_entry(repo, benign)
        _git(repo, "read-tree", "HEAD")
        (repo / "control.txt").write_bytes(benign)
    else:
        _history_entry(repo, benign)
        _git(repo, "read-tree", "HEAD")
        (repo / "control.txt").write_bytes(content)
        blob = _git(repo, "hash-object", "-w", "--stdin", data=content).decode().strip()
        _git(repo, "update-index", "--add", "--cacheinfo", "100644", blob, "control.txt")

    config = tmp_path / "repository.toml"
    config.write_bytes((ROOT / ".gitleaks.toml").read_bytes())
    empty = tmp_path / "empty.toml"
    empty.write_text('title = "empty control"\n', encoding="utf-8")
    rule_ids: dict[str, set[str]] = {}
    for label, selected in [("configured", config), ("empty", empty), ("builtin", None)]:
        enabled = label != "empty"
        report = tmp_path / f"report-{label}.json"
        command = [str(GITLEAKS), "detect" if mode == "history" else "protect"]
        if mode == "staged":
            command.append("--staged")
        command.extend([
            "--source", str(repo), "--exit-code", "1",
            "--redact=100", "--report-format", "json", "--report-path", str(report),
        ])
        if selected is not None:
            command.extend(["--config", str(selected)])
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("GIT_", "GITLEAKS_"))}
        result = subprocess.run(command, cwd=repo, capture_output=True, env=env, check=False)
        raw = report.read_bytes() if report.exists() else b"[]"
        # Avoid assertion introspection: failure output must never expose a token.
        if any(token.encode() in output for output in (result.stdout, result.stderr, raw)):
            pytest.fail("scanner leaked synthetic content; output withheld", pytrace=False)
        # Exit codes follow --exit-code 1, not the implementation under test.
        expected = 1 if enabled and positive else 0
        if result.returncode != expected:
            pytest.fail("unexpected scanner exit status; output withheld", pytrace=False)
        findings = json.loads(raw)
        rule_ids[label] = {item.get("RuleID", "") for item in findings}
        if enabled and positive:
            if not any(item.get("RuleID") == "aws-access-token"
                       and item.get("File") == "control.txt"
                       and item.get("StartLine") == 1 for item in findings):
                pytest.fail("expected file, line and rule metadata missing", pytrace=False)
        elif findings:
            pytest.fail("negative control unexpectedly produced findings", pytrace=False)
    if rule_ids["configured"] != rule_ids["builtin"]:
        pytest.fail("configured detection differs from embedded default-only control", pytrace=False)


@pytest.mark.parametrize("mode", ["staged", "history"])
def test_disposable_history_and_index_setup(tmp_path: Path, mode: str) -> None:
    """Verify fixture plumbing independently, even when Gitleaks is unavailable.

    The index contains the second input for staged mode, while history mode
    keeps the first input only in its parent commit. Values are benign.
    """
    repo = tmp_path / "repository"
    repo.mkdir()
    _git(repo, "init", "--quiet", "--initial-branch=main")
    _history_entry(repo, b"first\n")
    if mode == "history":
        _history_entry(repo, b"second\n")
        assert _git(repo, "show", "HEAD^:control.txt") == b"first\n"
        assert _git(repo, "show", "HEAD:control.txt") == b"second\n"
    else:
        _git(repo, "read-tree", "HEAD")
        blob = _git(repo, "hash-object", "-w", "--stdin", data=b"second\n").decode().strip()
        _git(repo, "update-index", "--add", "--cacheinfo", "100644", blob, "control.txt")
        assert _git(repo, "show", ":control.txt") == b"second\n"
        assert _git(repo, "show", "HEAD:control.txt") == b"first\n"


def test_fixture_setup_ignores_inherited_git_bindings(tmp_path: Path, monkeypatch) -> None:
    caller = tmp_path / "caller"
    caller.mkdir()
    _git(caller, "init", "--quiet", "--initial-branch=main")
    _history_entry(caller, b"caller content\n")
    sentinel = caller / "preserved.txt"
    sentinel.write_bytes(b"preserve caller files\n")
    before = {path.relative_to(caller): path.read_bytes()
              for path in caller.rglob("*") if path.is_file()}
    monkeypatch.setenv("GIT_DIR", str(caller / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(caller))
    monkeypatch.setenv("GIT_COMMON_DIR", str(caller / ".git"))
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    _git(fixture, "init", "--quiet", "--initial-branch=main")
    _history_entry(fixture, b"fixture content\n")
    assert _git(fixture, "show", "HEAD:control.txt") == b"fixture content\n"
    after = {path.relative_to(caller): path.read_bytes()
             for path in caller.rglob("*") if path.is_file()}
    assert before == after
