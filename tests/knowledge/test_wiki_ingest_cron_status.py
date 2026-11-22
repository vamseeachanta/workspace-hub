"""Isolated regressions for the nightly ingest contract in issue #2293.

Independent hand calculation: a single successful or duplicate source contributes
one processed item and zero errors; an unrelated failure contributes zero items
and one error. Publication has two exclusive outcomes, determined by push status.
No expected result is calculated from the wrapper's implementation.

All wrapper commands, including utility commands, resolve to audited stubs. Only
this test driver uses read-only Git to compare the real checkout before/after.

Plan-lite
---------
Scope: this regression module only; production code will remain unchanged.
Acceptance: duplicate/error counters and exclusive publication messages will
match the independent expectations above; unexpected stub calls will fail.
Verification: the following command will run the 15 synthetic regression cases,
with <scratch> replaced by a temporary directory outside the checkout:
UV_OFFLINE=1 uv run --no-project --with pytest python -m pytest tests/knowledge/test_wiki_ingest_cron_status.py -q -rA -p no:cacheprovider --basetemp=<scratch>
Limit: synthetic helpers do not validate actual ingest, remote publication or
scheduler integration.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]  # tests/knowledge -> repository root
WRAPPER = ROOT / "scripts/knowledge/wiki-ingest-cron.sh"
# POSIX shell convention: zero succeeds, one represents a generic failure.
OK, FAILED = 0, 1
# Synthetic input, not a timestamp from a historical run.
DATE = "2000-01-01"
STAMP = f"{DATE}T00:00:00"
PUBLISHED = "Changes committed and pushed"
LOCAL_ONLY = "WARNING: push failed — changes committed but remain local"
# Fixed truth table derived from the single-source hand calculation above.
INGEST_TRUTH = {
    "success": (OK, 1, 0),
    "duplicate": (OK, 1, 0),
    "error": (FAILED, 0, 1),
}
PUSH_TRUTH = {OK: (PUBLISHED, "WARNING: push failed"), FAILED: (LOCAL_ONLY, PUBLISHED)}
STUB_COMMANDS = ("dirname", "date", "mkdir", "tee", "basename", "find", "realpath",
                 "grep", "uv", "git", "gh")

# This command stub uses only Python's standard library; it never launches a tool.
# Numeric indices below select argv fields; modes use standard octal permissions.
STUB = r'''
import json
import os
from pathlib import Path
import sys

name = Path(sys.argv[0]).name
args = sys.argv[1:]
root = Path(os.environ["FAKE_ROOT"])
audit = Path(os.environ["AUDIT"])
with audit.open("a") as stream:
    stream.write(json.dumps([name, *args]) + "\n")


def deny():
    with Path(os.environ["UNEXPECTED"]).open("a") as stream:
        stream.write(json.dumps([name, *args]) + "\n")
    sys.exit(1)


def inside(value):
    path = Path(value).resolve()
    if not path.is_relative_to(root):
        deny()
    return path


if name == "dirname" and args == [str(root / "scripts/knowledge/wiki-ingest-cron.sh")]:
    print(inside(args[0]).parent)
elif name == "date" and args in (
    ["-u", "+%Y-%m-%d"], ["-u", "+%H:%M:%S"],
    ["+%Y%m%d"], ["-u", "+%Y-%m-%dT%H:%M:%S"],
):
    print({"+%Y-%m-%d": "2000-01-01", "+%H:%M:%S": "00:00:00",
           "+%Y%m%d": "20000101", "+%Y-%m-%dT%H:%M:%S": "2000-01-01T00:00:00"}[args[-1]])
elif name == "mkdir" and args == ["-p", str(root / "logs/wiki-ingest")]:
    inside(args[-1]).mkdir(parents=True, exist_ok=True)
elif name == "tee" and args == ["-a", str(root / "logs/wiki-ingest/ingest-2000-01-01.log")]:
    text = sys.stdin.read()
    with inside(args[-1]).open("a") as stream:
        stream.write(text)
    sys.stdout.write(text)
elif name == "basename" and args == [str(root / "docs/methodology/source.md")]:
    print("source.md")
elif name == "find" and args == [
    str(root / "docs/methodology"), "-type", "f", "(",
    "-name", "*.md", "-o", "-name", "*.yaml", "-o", "-name", "*.yml", "-o",
    "-name", "*.json", "-o", "-name", "*.jsonl", "-o", "-name", "*.txt", ")", "-print0",
]:
    sys.stdout.write(str(root / "docs/methodology/source.md") + "\0")
elif name == "realpath" and args == [
    "--relative-to=" + str(root), str(root / "docs/methodology/source.md"),
]:
    print("docs/methodology/source.md")
elif name == "grep" and args == ["-qiE", "already exists|duplicate"]:
    text = sys.stdin.read().lower()
    sys.exit(0 if "already exists" in text or "duplicate" in text else 1)
elif name == "git" and args == ["diff", "--quiet", "knowledge/wikis/engineering/"]:
    # A synthetic wiki change forces the commit/push path without Git mutation.
    sys.exit(1)
elif name == "uv":
    if args == ["run", "scripts/knowledge/llm_wiki.py", "ingest",
                str(root / "docs/methodology/source.md"), "--wiki", "engineering"]:
        kind = os.environ["INGEST_KIND"]
        if kind == "duplicate":
            # Literal CLI wording: scripts/knowledge/llm_wiki.py, cmd_ingest.
            print("[WARN] Source already exists in wiki: synthetic-source")
            sys.exit(1)
        if kind == "error":
            print("[ERROR] source could not be read")
            sys.exit(1)
        if kind != "success":
            deny()
        print("Synthetic ingest completed")
    elif args == ["run", "scripts/knowledge/llm_wiki.py", "lint", "--wiki", "engineering"]:
        print("Synthetic lint passed")
    elif args != ["run", "scripts/knowledge/wiki-cross-links.py", "--apply", "--quiet"]:
        deny()
else:
    # gh and every unrecognised invocation are deliberately forbidden.
    deny()
'''

WORKSTATION_LIB = r'''
# Remove the wrapper's inherited search directories after its initial setup.
export PATH="$STUB_BIN"
ws_is() {
    printf 'ws_is %s\n' "$*" >> "$LIB_AUDIT"
    [[ "$*" == full ]] || { printf 'ws_is\n' >> "$UNEXPECTED"; return 1; }
}
'''
GIT_LIB = r'''
check_call() {
    printf '%s\n' "$1" >> "$LIB_AUDIT"
    [[ "$PWD" == "$FAKE_ROOT" ]] || { printf 'cwd\n' >> "$UNEXPECTED"; return 1; }
}
git_safe_init() {
    check_call init
    [[ "$*" == "$FAKE_ROOT" ]] || { printf 'init\n' >> "$UNEXPECTED"; return 1; }
}
git_safe_pull() {
    check_call pull
    [[ "$#" == 0 ]] || { printf 'pull\n' >> "$UNEXPECTED"; return 1; }
}
git_safe_commit() {
    check_call commit
    [[ "$#" == 3 && "$2" == knowledge/wikis/engineering/ &&
       "$3" == "$FAKE_ROOT/knowledge/wikis/engineering/.last-ingest-timestamp" ]] || {
        printf 'commit\n' >> "$UNEXPECTED"; return 1;
    }
    printf '%s\n' "$1" > "$FAKE_ROOT/commit-message"
}
git_safe_push() {
    check_call push
    [[ "$#" == 0 ]] || { printf 'push\n' >> "$UNEXPECTED"; return 1; }
    return "$PUSH_STATUS"
}
'''


def _git(*args):
    # Never let inherited repository bindings redirect the preservation probes.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=ROOT, env=env)


def _repository_state():
    """Record checkout metadata plus bytes of the wrapper and protected outputs."""
    names = _git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    metadata = {}
    for name in names.split(b"\0"):
        if name:
            path = ROOT / os.fsdecode(name)
            if path.exists() or path.is_symlink():
                stat = path.lstat()
                metadata[name] = (stat.st_mode, stat.st_size, stat.st_mtime_ns)
    protected = [WRAPPER]
    for relative in ("knowledge/wikis/engineering", "logs/wiki-ingest"):
        directory = ROOT / relative
        if directory.exists():
            protected.extend(path for path in directory.rglob("*") if path.is_file())
    digests = {str(path): hashlib.sha256(path.read_bytes()).digest() for path in protected}
    return metadata, digests, _git("status", "--porcelain", "--untracked-files=all")


@pytest.fixture
def run_wrapper(tmp_path):
    """Copy the wrapper unchanged; all writes and all fake helpers are temporary."""
    assert not tmp_path.resolve().is_relative_to(ROOT.resolve())
    root = tmp_path / "synthetic"
    binary = root / "user/.local/bin"
    binary.mkdir(parents=True)
    for relative in ("scripts/knowledge", "scripts/lib", "scripts/cron/lib",
                     "docs/methodology", "knowledge/wikis/engineering"):
        (root / relative).mkdir(parents=True, exist_ok=True)
    wrapper = root / "scripts/knowledge/wiki-ingest-cron.sh"
    wrapper.write_bytes(WRAPPER.read_bytes())
    (root / "docs/methodology/source.md").write_text("Synthetic source.\n")
    (root / "scripts/lib/workstation-lib.sh").write_text(WORKSTATION_LIB)
    (root / "scripts/cron/lib/git-safe.sh").write_text(GIT_LIB)
    audit, libraries, unexpected = (root / name for name in ("calls", "libraries", "unexpected"))
    for name in STUB_COMMANDS:
        stub = binary / name
        stub.write_text(f"#!{sys.executable}\n" + STUB)
        stub.chmod(0o755)  # POSIX executable file permissions.
    # Unknown commands must leave evidence even if the wrapper ignores failure.
    bootstrap = root / "bootstrap.sh"
    bootstrap.write_text('''# DEBUG guards also cover the wrapper's initial PATH expansion.
_guard_external() {
    local word="${1%% *}" resolved
    if [[ "$(type -t -- "$word" || :)" == file ]]; then
        resolved="$(type -P -- "$word")"
        if [[ "$resolved" != "$STUB_BIN/"* ]]; then
            printf 'external command outside stubs\\n' >> "$UNEXPECTED"
            exit 1
        fi
    fi
}
set -T
trap '_guard_external "$BASH_COMMAND"' DEBUG
command_not_found_handle() {
    printf '%s\\n' "$*" >> "$UNEXPECTED"
    return 127
}
''')  # Bash command-not-found status is 127.
    bash = shutil.which("bash")
    assert bash is not None

    def run(kind, push_status):
        before = _repository_state()
        result = subprocess.run(
            [bash, "--noprofile", "--norc", str(wrapper)],
            cwd=root,
            env={"HOME": str(root / "user"), "PATH": str(binary),
                 "BASH_ENV": str(bootstrap), "STUB_BIN": str(binary),
                 "FAKE_ROOT": str(root), "AUDIT": str(audit),
                 "LIB_AUDIT": str(libraries), "UNEXPECTED": str(unexpected),
                 "INGEST_KIND": kind, "PUSH_STATUS": str(push_status),
                 "TMPDIR": str(tmp_path), "PYTHONDONTWRITEBYTECODE": "1"},
            text=True, capture_output=True,
            timeout=30,  # Generous safety bound for this synthetic, local-only run.
        )
        (root / "stdout.log").write_text(result.stdout)
        (root / "stderr.log").write_text(result.stderr)
        assert _repository_state() == before
        assert wrapper.read_bytes() == WRAPPER.read_bytes()
        assert not unexpected.exists(), (
            unexpected.read_text() if unexpected.exists() else ""
        )
        assert not result.stderr
        calls = [json.loads(line) for line in audit.read_text().splitlines()]
        assert libraries.read_text().splitlines() == [
            "ws_is full", "init", "pull", "commit", "push"
        ]
        assert [call for call in calls if call[0] == "git"] == [
            ["git", "diff", "--quiet", "knowledge/wikis/engineering/"]]
        assert not any(call[0] == "gh" for call in calls)
        uv_calls = [call for call in calls if call[0] == "uv"]
        expected_uv = [["uv", "run", "scripts/knowledge/llm_wiki.py", "ingest",
                        str(root / "docs/methodology/source.md"), "--wiki", "engineering"]]
        if kind != "error":
            expected_uv.append(["uv", "run", "scripts/knowledge/wiki-cross-links.py", "--apply", "--quiet"])
        expected_uv.append(["uv", "run", "scripts/knowledge/llm_wiki.py", "lint", "--wiki", "engineering"])
        assert uv_calls == expected_uv
        marker = root / "knowledge/wikis/engineering/.last-ingest-timestamp"
        assert marker.read_text().strip() == STAMP
        assert (root / "commit-message").is_file()
        log = (root / f"logs/wiki-ingest/ingest-{DATE}.log").read_text()
        logged_messages = [
            line for line in log.splitlines() if line.startswith("[wiki-ingest]")
        ]
        assert logged_messages == result.stdout.splitlines()
        assert "Synthetic lint passed" in log
        code, processed, errors = INGEST_TRUTH[kind]
        assert result.returncode == code
        assert f"Ingest complete: {processed} processed, {errors} error(s)" in log
        assert f"Files ingested:  {processed}" in log
        assert f"Ingest errors:   {errors}" in log
        present, absent = PUSH_TRUTH[push_status]
        assert log.count(present) == 1  # Exactly one publication outcome per run.
        assert absent not in log
        return log

    return run


def test_duplicate_source_is_nonfatal(run_wrapper):
    log = run_wrapper("duplicate", OK)
    assert "OK (source already exists — skipped)" in log
    assert "ERROR: ingest failed" not in log


def test_push_failure_never_claims_published(run_wrapper):
    run_wrapper("success", FAILED)


def test_push_success_has_no_failure_warning(run_wrapper):
    run_wrapper("success", OK)


def test_unrelated_ingest_error_remains_an_error(run_wrapper):
    log = run_wrapper("error", OK)
    assert "ERROR: ingest failed for docs/methodology/source.md" in log
    assert "[ERROR] source could not be read" in log
    assert "OK (source already exists — skipped)" not in log


@pytest.mark.parametrize("command", STUB_COMMANDS)
def test_stub_rejects_unexpected_invocations(tmp_path, command):
    """Even ignored shell failures leave an audit record and fail the test."""
    assert not tmp_path.resolve().is_relative_to(ROOT.resolve())
    stub = tmp_path / command
    stub.write_text(f"#!{sys.executable}\n" + STUB)
    stub.chmod(0o755)  # POSIX executable file permissions.
    audit, unexpected = tmp_path / "calls", tmp_path / "unexpected"
    result = subprocess.run(
        [str(stub), "--unexpected"], cwd=tmp_path,
        env={"FAKE_ROOT": str(tmp_path), "AUDIT": str(audit),
             "UNEXPECTED": str(unexpected), "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=30,  # Same synthetic-run safety bound.
    )
    assert result.returncode == FAILED
    assert not result.stdout and not result.stderr
    assert json.loads(audit.read_text()) == [command, "--unexpected"]
    assert unexpected.read_text() == audit.read_text()
