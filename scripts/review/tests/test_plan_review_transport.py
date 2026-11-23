"""Offline transport/diagnostic examples for issue #3462.

Expected delivery is independently composed as prompt + framing + original plan.
The 32,089-character case comes from issue #3462 (2026-07-11). Adjacent
sizes bracket it; the larger case exceeds it. These are fixture sizes, not
platform limits. No real provider executable is invoked.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
WRAPPER = ROOT / "scripts/review/plan-review-fanout.sh"
PROMPT = ROOT / "scripts/review/plan-review-prompt.md"

FAKE = r'''
import json, os, pathlib, stat, sys, time
provider = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
mode = os.environ.get("FAKE_MODE", "ok")
if args == ["--version"]:
    if mode == "version-failure":
        print("PRIVATE_DIAGNOSTIC")
        sys.exit(1)
    if mode == "bad-version":
        print("codex-cli 0.128.0")
        sys.exit(0)
    print({"codex": "codex-cli 0.144.1", "claude": "2.1.206 (Claude Code)",
           "agy": "agy 1.0.0"}[provider])
    sys.exit(0)
if args in (["login", "status"], ["auth", "status"]):
    if mode == "auth-timeout":
        time.sleep(3)
    if mode == "auth-malformed":
        print("not JSON")
        sys.exit(0)
    if mode == "auth-runtime-failure":
        print("PRIVATE_DIAGNOSTIC")
        sys.exit(2)
    if provider == "claude":
        print(json.dumps({"loggedIn": mode != "auth-required", "authMethod": "none"}))
    else:
        print("Not logged in" if mode == "auth-required" else "Logged in using ChatGPT")
    sys.exit(1 if mode == "auth-required" else 0)
pathlib.Path(os.environ["CAPTURE"]).write_text(json.dumps({
    "args": args, "stdin": sys.stdin.read(), "CLAUDECODE": os.getenv("CLAUDECODE"),
    "stdin_is_file": stat.S_ISREG(os.fstat(0).st_mode),
    "stdin_permissions": stat.S_IMODE(os.fstat(0).st_mode)}))
if mode == "timeout":
    print("## Verdict\nAPPROVE", flush=True)
    time.sleep(3)
if mode == "failure":
    print("PRIVATE_DIAGNOSTIC", file=sys.stderr)
    print("PRIVATE_PLAN_ECHO")
    sys.exit(1)
if mode == "auth-runtime":
    print("Please run claude auth login", file=sys.stderr)
    sys.exit(1)
if mode == "garbage":
    print("PRIVATE_PLAN_ECHO")
    sys.exit(0)
if mode == "bad-verdict":
    print("## Verdict\nSUCCESS\n\n## Findings\n(none)\n\n## Blockers\n(none)")
    sys.exit(0)
print("## Verdict\nMINOR\n\n## Retrieval\nSynthetic input.\n\n## Findings\n(none)\n\n## Blockers\n(none)")
'''


@pytest.fixture
def invoke(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for provider in ("codex", "claude", "agy"):
        executable = bin_dir / provider
        executable.write_text(f"#!{sys.executable}\n{FAKE}")
        executable.chmod(0o700)
    temp_dir = tmp_path / "private"
    temp_dir.mkdir()
    out_dir = tmp_path / "results"
    capture = tmp_path / "capture.json"

    def run(provider="codex", body="example\n", mode="ok"):
        plan = tmp_path / "2026-07-11-issue-3462-example.md"
        plan.write_text(body)
        env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
                   TMPDIR=str(temp_dir), CAPTURE=str(capture), FAKE_MODE=mode,
                   CLAUDECODE="1", REPO_ROOT=str(tmp_path),
                   PLAN_REVIEW_PROVIDER_TIMEOUT_SEC="1",
                   PLAN_REVIEW_PREFLIGHT_TIMEOUT_SEC="1")
        result = subprocess.run(
            ["bash", str(WRAPPER), str(plan), f"--providers={provider}",
             f"--output-dir={out_dir}"], env=env, capture_output=True,
            input="UNRELATED_PARENT_INPUT", text=True, timeout=15, check=False,
        )
        assert result.returncode == 0, result.stderr
        artifact = next(out_dir.glob(f"*-{provider}.md")).read_text()
        assert not list(temp_dir.iterdir()), "temporary payload or diagnostics leaked"
        return artifact, json.loads(capture.read_text()) if capture.exists() else None, plan

    return run


@pytest.mark.parametrize("size", [32088, 32089, 32090, 32766, 32767, 32768, 65536])
def test_large_payload_uses_finite_stdin(invoke, size):
    """Hand composition: framing plus size original characters, including EOF.

    Microsoft CreateProcessW, lpCommandLine (retrieved 2026-10-22), documents
    32,767 characters including NUL. Bracket that size as synthetic input.
    The serialized command itself has 5+1+4+1+1=12 ASCII code units, independent
    of payload size. This is simulation on Unix, not native Windows execution.
    """
    body = "λ" * (size - 2) + "\n\n"
    artifact, capture, plan = invoke(body=body)
    assert capture["args"] == ["exec", "-"]
    assert capture["stdin"] == PROMPT.read_text() + f"\n\n--- PLAN ({plan}) ---\n" + body
    assert capture["CLAUDECODE"] is None
    assert capture["stdin_is_file"]
    assert capture["stdin_permissions"] == 0o600
    assert subprocess.list2cmdline(["codex", *capture["args"]]) == "codex exec -"
    assert "codex-cli 0.144.1" in artifact
    assert "stdin" in artifact
    assert "UNAVAILABLE" not in artifact


@pytest.mark.parametrize("provider", ["claude", "codex"])
def test_auth_required_is_distinct_and_does_not_review(invoke, provider):
    artifact, capture, _ = invoke(provider=provider, mode="auth-required")
    assert "UNAVAILABLE" in artifact
    assert "AUTH_REQUIRED" in artifact
    assert "auth login" in artifact or "codex login" in artifact
    assert capture is None


@pytest.mark.parametrize("mode", ["auth-timeout", "auth-malformed", "auth-runtime-failure"])
@pytest.mark.parametrize("provider", ["claude", "codex"])
def test_auth_probe_failure_is_not_reported_as_logged_out(invoke, mode, provider):
    artifact, capture, _ = invoke(provider=provider, mode=mode)
    assert "AUTH_CHECK_FAILED" in artifact
    assert "AUTH_REQUIRED" not in artifact
    assert capture is None


@pytest.mark.parametrize("mode,category", [
    ("failure", "RUNTIME_FAILURE"), ("timeout", "TIMEOUT"),
    ("garbage", "INVALID_OUTPUT"), ("auth-runtime", "AUTH_REQUIRED"),
    ("bad-verdict", "INVALID_OUTPUT"),
])
def test_failures_are_conservative_and_do_not_echo_raw_output(invoke, mode, category):
    artifact, _, _ = invoke(mode=mode)
    assert "UNAVAILABLE" in artifact
    assert category in artifact
    assert "PRIVATE_" not in artifact
    assert "\nAPPROVE\n" not in artifact
    assert "codex-cli 0.144.1" in artifact
    if mode == "auth-runtime":
        assert "Authentication: AUTH_REQUIRED" in artifact


@pytest.mark.parametrize("mode,category", [
    ("version-failure", "VERSION_CHECK_FAILED"), ("bad-version", "INCOMPATIBLE"),
])
def test_version_probe_and_guard_fail_closed(invoke, mode, category):
    artifact, capture, _ = invoke(mode=mode)
    assert "UNAVAILABLE" in artifact
    assert category in artifact
    assert "PRIVATE_" not in artifact
    assert capture is None


def test_claude_path_reference_and_version_are_preserved(invoke):
    artifact, capture, plan = invoke(provider="claude", body="PRIVATE_PLAN\n")
    assert "2.1.206 (Claude Code)" in artifact
    assert "path-reference" in artifact
    assert "AUTHENTICATED" in artifact
    assert str(plan) in capture["args"][1]
    assert "PRIVATE_PLAN" not in " ".join(capture["args"])
    assert capture["stdin"] == ""
