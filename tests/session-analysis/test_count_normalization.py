"""Count regressions using synthetic records and a disposable script copy.

Hand calculation: four pending records below; only beta and gamma meet the
script's documented occurrences >= 5 rule. Expected totals: four scripts,
two agents; an empty record set contributes zero of either kind.
"""

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/analysis/session-analysis.sh"
RECORDS = (
    {"signal": "alpha", "occurrences": 4, "tool_sequence": "alpha"},
    {"signal": "beta", "occurrences": 5, "tool_sequence": "beta"},
    {"signal": "gamma", "occurrences": 8, "tool_sequence": "gamma"},
    {"signal": "delta", "occurrences": 0, "tool_sequence": "delta"},
)
# An arbitrary fixed date selects an otherwise empty signal directory.
ANALYSIS_DATE = "2000-01-01"

GIT_STUB = r'''
import json
import os
import sys

args = sys.argv[1:]
with open(os.environ["GIT_CALLS"], "a") as log:
    log.write(json.dumps(args) + "\n")
if args == ["-C", os.environ["TEST_WORKSPACE"], "rev-parse", "--git-dir"]:
    sys.exit(1)  # No repository: prevents the aggregation pull.
sys.exit("git operation rejected by test stub")
'''

JQ_STUB = r'''
import json
import os
import sys

args = sys.argv[1:]
if args[:1] == ["-r"]:
    args = args[1:]
query, filename = args
with open(filename) as source:
    records = [json.loads(line) for line in source]
if query == "select(.occurrences >= 5) | .tool_sequence":
    # Threshold cited from the script's agent-candidate rule.
    for record in records:
        if record["occurrences"] >= 5:
            print(json.dumps(record["tool_sequence"]))
elif query.startswith('select(.signal != null and .signal != "")'):
    for record in records:
        print(record["signal"])
else:
    with open(os.environ["JQ_ERRORS"], "a") as log:
        log.write("unsupported query\n")
    sys.exit("unsupported query")
'''

WC_STUB = r'''
import os
import sys

if sys.argv[1:] != ["-l"]:
    sys.exit("only line counting is supported")
count = sys.stdin.buffer.read().count(b"\n")
style = os.environ["COUNT_STYLE"]
if style == "embedded":
    output = f" \t\n{count}\v\f \n"
elif style == "crlf":
    output = f" \r\n\t{count}\r\n"
else:
    output = f"{count}\n"
sys.stdout.buffer.write(output.encode("ascii"))
'''


def _executable(path, body):
    path.write_text(f"#!{sys.executable}\n{body}", encoding="utf-8")
    # The current user must be able to execute the isolated command stubs.
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


@pytest.fixture
def workspace(tmp_path):
    copied_script = tmp_path / "scripts/analysis/session-analysis.sh"
    copied_script.parent.mkdir(parents=True)
    shutil.copyfile(SCRIPT, copied_script)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    # Only these utilities are reachable; no assistant or real Git executable.
    for name in (
        "bash", "dirname", "date", "mkdir", "find", "head", "grep", "tr",
        "awk", "sed", "sort", "uniq", "basename",
    ):
        utility = shutil.which(name)
        assert utility is not None, f"required test utility unavailable: {name}"
        (bin_dir / name).symlink_to(utility)
    _executable(bin_dir / "git", GIT_STUB)
    _executable(bin_dir / "jq", JQ_STUB)
    _executable(bin_dir / "wc", WC_STUB)
    for name in ("private", "tmp"):
        (tmp_path / name).mkdir()
    # Build a fresh environment: inherited Git bindings and shell startup files
    # must not redirect the copied script into the caller's repository.
    env = {
        "PATH": str(bin_dir),
        "HOME": str(tmp_path / "private"),
        "TMPDIR": str(tmp_path / "tmp"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C",
        "TEST_WORKSPACE": str(tmp_path),
        "GIT_CALLS": str(tmp_path / "git-calls.jsonl"),
        "JQ_ERRORS": str(tmp_path / "jq-errors.txt"),
    }
    # Preserve the shared cache setting if supplied by the test runner.
    if "UV_CACHE_DIR" in os.environ:
        env["UV_CACHE_DIR"] = os.environ["UV_CACHE_DIR"]
    return tmp_path, copied_script, env


def _run_analysis(workspace, style, records, expected_summary):
    root, script, env = workspace
    pending = root / ".claude/state/pending-reviews"
    pending.mkdir(parents=True)
    (pending / "skill-candidates.jsonl").write_text(
        "".join(json.dumps(record) + "\n" for record in records), encoding="utf-8"
    )
    env["COUNT_STYLE"] = style
    result = subprocess.run(
        [str(root / "bin/bash"), str(script), "--date", ANALYSIS_DATE],
        cwd=root, env=env, capture_output=True, text=True, timeout=30,
    )
    # The timeout is a safety bound for this small local fixture, not a benchmark.
    assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in Path(env["GIT_CALLS"]).read_text().splitlines()]
    assert calls == [["-C", str(root), "rev-parse", "--git-dir"]]
    assert not Path(env["JQ_ERRORS"]).exists()
    assert result.stderr == (
        "[session-analysis] WARN: git not available — skipping cross-machine aggregation\n"
    ), result.stderr
    summary = (root / f".claude/state/session-analysis/{ANALYSIS_DATE}.md").read_text()
    assert expected_summary in summary.splitlines(), summary


def test_agent_count_strips_embedded_whitespace(workspace):
    _run_analysis(
        workspace, "embedded", RECORDS,
        "Candidates identified: 4 script, 0 skill, 0 hook, 2 agent, 0 mcp",
    )


def test_agent_count_accepts_crlf(workspace):
    _run_analysis(
        workspace, "crlf", RECORDS,
        "Candidates identified: 4 script, 0 skill, 0 hook, 2 agent, 0 mcp",
    )


def test_normal_count_unchanged(workspace):
    _run_analysis(
        workspace, "ordinary", RECORDS,
        "Candidates identified: 4 script, 0 skill, 0 hook, 2 agent, 0 mcp",
    )


def test_empty_input_count(workspace):
    _run_analysis(
        workspace, "crlf", (),
        "Candidates identified: 0 script, 0 skill, 0 hook, 0 agent, 0 mcp",
    )


def test_git_stub_rejects_mutations(workspace):
    root, _, env = workspace
    # The allowlist rejects every other invocation, including read operations.
    for operation in (
        "pull", "push", "fetch", "add", "commit", "reset", "checkout", "clean",
        "merge", "rebase", "config", "status",
    ):
        result = subprocess.run(
            [str(root / "bin/git"), "-C", str(root), operation],
            cwd=root, env=env, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode != 0
        assert result.stderr.strip() == "git operation rejected by test stub"
