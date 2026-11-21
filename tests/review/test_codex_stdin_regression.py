"""Offline submit contract for issue #3442 (2026), using no assistant service.

Expected outcomes are hand-derived: the reported diagnostic means unavailable
(existing cross-review exit 7); an empty stdin has length zero; a successful
first attempt has one call; an empty first output plus success has two calls.
Synthetic sizes and deadlines are test inputs, not measured compatibility limits.
"""

import json
import os
import runpy
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SUBMIT = ROOT / "scripts/review/submit-to-codex.sh"
GUARD = ROOT / "scripts/review/lib/codex-version-guard.sh"
SHA = "a" * 40  # Synthetic commit input; issue #3442 requires --commit dispatch.
SIGNATURE = "Reading additional input from stdin..."  # Issue #3442 reproduction.


def executable(path, body):
    path.write_text(body, encoding="utf-8", newline="\n")
    path.chmod(0o755)
    return path


@pytest.fixture
def harness(tmp_path):
    """Isolate all executable discovery and outputs from installed assistants."""
    bins = tmp_path / "bin"
    bins.mkdir()
    diff = tmp_path / "diff.txt"
    diff.write_text(
        "diff --git a/example.py b/example.py\n+answer = 42\n",
        encoding="utf-8", newline="\n",
    )
    executable(
        bins / "git",
        "#!/usr/bin/env bash\n"
        '[[ "$*" == "show --stat --unified=80 ' + SHA + '" ]] || exit 99\n'
        'cat "$MOCK_DIFF"\n',
    )
    executable(
        bins / "uv",
        f'#!/bin/sh\nshift 3\nexec {shlex.quote(sys.executable)} "$@"\n',
    )
    executable(
        bins / "codex",
        f"#!{sys.executable}\n"
        + """
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

if sys.argv[1:] == ["--version"]:
    print("codex-cli " + os.environ.get("MOCK_VERSION", "0.144.1"))
    sys.exit(0)
assert sys.argv[1] == "exec"
assert "--output-schema" in sys.argv
assert sys.argv[2] != "-"
capture = Path(os.environ["MOCK_CAPTURE"])
calls = len(capture.read_text(encoding="utf-8").splitlines()) if capture.exists() else 0
with capture.open("a", encoding="utf-8", newline="\\n") as out:
    out.write(json.dumps({"prompt": sys.argv[2], "stdin": sys.stdin.read()}) + "\\n")
mode = os.environ.get("MOCK_MODE", "success")
if mode in ("retry", "retry_signature") and calls == 0:
    sys.exit(0)
if mode == "retry_signature":
    mode = "signature"
if mode == "quota":
    print("insufficient_quota", file=sys.stderr, flush=True)
    sys.exit(1)
if mode == "generic":
    print("synthetic failure", file=sys.stderr, flush=True)
    sys.exit(9)
if mode == "signature_child":
    child = subprocess.Popen([sys.executable, "-c",
        "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "time.sleep(2); "
        "from pathlib import Path; Path(__import__('sys').argv[1]).write_text('orphan', encoding='utf-8', newline='\\n')",
        os.environ["MOCK_ORPHAN"]])
    print("Reading additional input from stdin...", file=sys.stderr, flush=True)
    sys.exit(0)
if mode.startswith("signature"):
    if mode == "signature_ignore_term":
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    if mode == "signature_split":
        sys.stderr.write("Reading additional input ")
        sys.stderr.flush()
        time.sleep(0.2)
        sys.stderr.write("from stdin...\\n")
        sys.stderr.flush()
    elif mode == "signature_crlf":
        sys.stderr.write("Reading additional input from stdin...\\r\\n")
        sys.stderr.flush()
    else:
        print("Reading additional input from stdin...", file=sys.stderr, flush=True)
    if mode == "signature_exit":
        sys.exit(0)
    if mode == "signature_error":
        sys.exit(1)
    time.sleep(30)
if mode == "timeout":
    time.sleep(30)
if mode == "quoted":
    print("Quoted diagnostic: Reading additional input from stdin...", file=sys.stderr)
output = sys.argv[sys.argv.index("--output-last-message") + 1]
Path(output).write_text(json.dumps({"verdict": "APPROVE", "summary": "synthetic",
    "issues_found": [], "suggestions": [], "questions_for_author": []}),
    encoding="utf-8", newline="\\n")
""",
    )
    env = os.environ.copy()
    # Clear inherited repository bindings before fixture command resolution.
    for key in tuple(env):
        if key.startswith(("GIT_", "CODEX_")):
            env.pop(key)
    env.update(
        PATH=str(bins) + os.pathsep + env["PATH"],
        CODEX_BIN=str(bins / "codex"),
        CODEX_TIMEOUT_SECONDS="15",  # Test input: outer bound is shorter.
        REPO_ROOT=str(tmp_path),
        TMPDIR=str(tmp_path),
        MOCK_DIFF=str(diff),
        MOCK_CAPTURE=str(tmp_path / "capture.jsonl"),
        MOCK_ORPHAN=str(tmp_path / "orphan"),
    )
    return tmp_path, env


def submit(
    harness, *, mode="success", content="small", stdin="pipe", version="0.144.1"
):
    directory, env = harness
    env.update(MOCK_MODE=mode, MOCK_VERSION=version)
    if content == "full":
        # Hand count: 2,000 source lines, below the wrapper's existing argv cap.
        Path(env["MOCK_DIFF"]).write_text(
            "diff --git a/example.py b/example.py\n"
            + "".join(f"+value_{i} = {i}\n" for i in range(2000)),
            encoding="utf-8", newline="\n",
        )
    args = ["bash", str(SUBMIT), "--commit", SHA, "--prompt", "Find defects."]
    if stdin == "held":
        # Leave the write end open: a wrapper inheriting it would block forever.
        read_fd, write_fd = os.pipe()
        try:
            result = subprocess.run(
                args,
                check=False,
                env=env,
                cwd=directory,
                stdin=read_fd,
                capture_output=True,
                text=True,
                timeout=8,
            )
        finally:
            os.close(read_fd)
            os.close(write_fd)
    else:
        result = subprocess.run(
            args,
            check=False,
            env=env,
            cwd=directory,
            input="caller sentinel" if stdin == "pipe" else "",
            capture_output=True,
            text=True,
            timeout=8,
        )
    capture = Path(env["MOCK_CAPTURE"])
    calls = [json.loads(line) for line in capture.read_text(encoding="utf-8").splitlines()]
    return result, calls


@pytest.mark.parametrize("content", ["small", "full"])
@pytest.mark.parametrize("stdin", ["closed", "pipe", "held"])
def test_commit_signature_fails_fast_without_retry(harness, content, stdin):
    """One diagnostic => exit 7, one invocation, zero inherited input bytes."""
    result, calls = submit(harness, mode="signature", content=content, stdin=stdin)
    assert result.returncode == 7, result.stdout + result.stderr
    assert "UNAVAILABLE" in result.stdout
    assert "CODEX_STDIN_REGRESSION" in result.stdout
    assert len(calls) == 1
    assert calls[0]["stdin"] == ""
    assert "Find defects." in calls[0]["prompt"]
    assert "diff --git" in calls[0]["prompt"]
    if content == "full":
        assert "+value_1999 = 1999" in calls[0]["prompt"]


@pytest.mark.parametrize(
    "mode",
    [
        "signature_split",
        "signature_exit",
        "signature_error",
        "signature_crlf",
        "signature_ignore_term",
    ],
)
def test_signature_is_preserved_across_reads_and_fast_exit(harness, mode):
    result, calls = submit(harness, mode=mode)
    assert result.returncode == 7
    assert len(calls) == 1


@pytest.mark.parametrize("content", ["small", "full"])
def test_reported_version_can_succeed_without_signature(harness, content):
    result, calls = submit(harness, content=content, stdin="held")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "APPROVE" in result.stdout
    assert len(calls) == 1
    assert calls[0]["stdin"] == ""


def test_other_version_is_monitored_too(harness):
    result, calls = submit(harness, mode="signature", version="0.145.0")
    assert result.returncode == 7
    assert len(calls) == 1


def test_quoted_signature_is_not_a_stall(harness):
    result, _ = submit(harness, mode="quoted")
    assert result.returncode == 0


@pytest.mark.parametrize(
    "mode, expected, count",
    [
        ("retry", 0, 2),
        ("quota", 3, 2),
        ("generic", 9, 2),
        ("timeout", 124, 2),
    ],
)
def test_existing_failure_and_retry_contracts(harness, mode, expected, count):
    """Expected codes come from submit/cross-review contracts; two allowed attempts."""
    if mode == "timeout":
        harness[1]["CODEX_TIMEOUT_SECONDS"] = "0.2"  # Synthetic timeout input.
    result, calls = submit(harness, mode=mode)
    assert result.returncode == expected, result.stdout + result.stderr
    assert len(calls) == count


def test_signature_kills_descendants_after_leader_exit(harness):
    """A descendant cannot write its delayed marker after the group is stopped."""
    import time

    result, calls = submit(harness, mode="signature_child")
    assert result.returncode == 7
    assert len(calls) == 1
    time.sleep(2.2)  # Exceeds the synthetic child's two-second delay above.
    assert not Path(harness[1]["MOCK_ORPHAN"]).exists()


def test_version_detection_reports_limited_evidence(harness):
    result = subprocess.run(
        ["bash", "-c", 'source "$1"; codex_version_guard_check', "bash", str(GUARD)],
        check=False,
        env=harness[1],
        capture_output=True,
        text=True,
        timeout=8,
    )
    assert result.returncode == 0
    assert "0.144.1" in result.stdout
    assert "#3442" in result.stdout
    assert "scope unverified" in result.stdout


def test_configured_deny_band_still_applies(harness):
    """A configured ceiling beyond the reported version still blocks dispatch."""
    harness[1]["CODEX_VERSION_GUARD_CEILING"] = "0.145.0"  # Synthetic policy input.
    result = subprocess.run(
        ["bash", "-c", 'source "$1"; codex_version_guard_check', "bash", str(GUARD)],
        check=False,
        env=harness[1],
        capture_output=True,
        text=True,
        timeout=8,
    )
    assert result.returncode == 3
    assert "INCOMPATIBLE" in result.stdout


def test_signature_on_compact_retry_stops_further_processing(harness):
    """Empty first output permits one retry; a diagnostic on that retry exits 7."""
    result, calls = submit(harness, mode="retry_signature")
    assert result.returncode == 7
    assert "UNAVAILABLE" in result.stdout
    assert len(calls) == 2
    assert all(call["stdin"] == "" for call in calls)


@pytest.mark.parametrize(
    "chunks, expected",
    [
        ([b"Reading additional input ", b"from stdin..."], True),
        ([b"Reading additional input from stdin\r\n"], True),
        ([b"quoted: Reading additional input from stdin...\n"], False),
        ([b"x" * 100000, b"\nReading additional input from stdin...\n"], True),
        ([b"x" * 100000, b"Reading additional input from stdin...\n"], False),
    ],
)
def test_diagnostic_line_scanner(chunks, expected):
    """Literal line equality gives the expected result; a quoted suffix differs."""
    scan = runpy.run_path(str(ROOT / "scripts/review/codex-exec-watch.py"))["scan"]
    pending = b""
    found = False
    for chunk in chunks:
        matched, pending = scan(chunk, pending)
        found |= matched
    matched, _ = scan(b"", pending, eof=True)
    found |= matched
    assert found is expected


@pytest.mark.parametrize("suffix", [b" is disabled; continuing normally.\n", b"... detail\n"])
def test_partial_diagnostic_with_suffix_is_not_matched(suffix):
    scan = runpy.run_path(str(ROOT / "scripts/review/codex-exec-watch.py"))["scan"]
    matched, pending = scan(b"Reading additional input from stdin", b"")
    assert not matched
    matched, pending = scan(suffix, pending)
    assert not matched


@pytest.mark.parametrize("ending", ["", "\n"])
def test_exit_after_empty_select_drains_diagnostic(tmp_path, monkeypatch, ending):
    """An empty select followed by child exit must still retain and classify stderr."""
    module = runpy.run_path(str(ROOT / "scripts/review/codex-exec-watch.py"))
    real_selector = module["selectors"].DefaultSelector
    real_popen = subprocess.Popen
    children = []

    def launch(*args, **kwargs):
        process = real_popen(*args, **kwargs)
        children.append(process)
        return process

    class ExitBetweenSelectAndPoll(real_selector):
        first = True

        def select(self, timeout=None):
            if self.first:
                self.first = False
                children[0].wait(timeout=3)
                return []
            return super().select(timeout)

    monkeypatch.setattr(subprocess, "Popen", launch)
    monkeypatch.setattr(module["selectors"], "DefaultSelector", ExitBetweenSelectAndPoll)
    errors = tmp_path / "errors"
    diagnostic = SIGNATURE + ending
    result = module["watch"](
        [sys.executable, "-c", f"import sys; sys.stderr.write({diagnostic!r})"],
        3,
        errors,
    )
    assert result == 7
    assert errors.read_bytes() == diagnostic.encode("utf-8")


def test_delayed_non_diagnostic_suffix_completes(tmp_path):
    module = runpy.run_path(str(ROOT / "scripts/review/codex-exec-watch.py"))
    marker = tmp_path / "success"
    result = module["watch"](
        [
            sys.executable, "-c",
            (
                "import sys,time; from pathlib import Path; "
                "sys.stderr.write('Reading additional input from stdin'); sys.stderr.flush(); "
                "time.sleep(0.3); sys.stderr.write(' is disabled; continuing normally.\\n'); "
                "Path(sys.argv[1]).write_text('success', encoding='utf-8', newline='\\n')"
            ),
            str(marker),
        ],
        3,
        tmp_path / "errors",
    )
    assert result == 0
    assert marker.read_text(encoding="utf-8") == "success"


@pytest.mark.parametrize("diagnostic", [False, True])
def test_inherited_stderr_retains_deadline(tmp_path, diagnostic):
    """Leader exit is not EOF; an unclosed tail waits for the configured deadline."""
    module = runpy.run_path(str(ROOT / "scripts/review/codex-exec-watch.py"))
    prefix = SIGNATURE if diagnostic else "ordinary message"
    result = module["watch"](
        [
            sys.executable, "-c",
            (
                "import subprocess,sys; "
                "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)']); "
                f"sys.stderr.write({prefix!r}); sys.stderr.flush()"
            ),
        ],
        0.3,
        tmp_path / "errors",
    )
    assert result == 124
    assert (tmp_path / "errors").read_bytes() == (
        prefix.encode("utf-8") + b"Codex exec timed out\n"
    )
