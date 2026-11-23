"""Read-only PR status contract from issue #1308.

All identities are synthetic role words. PR number 1308 references the issue.
Counts are hand-counted from literal fixtures, independently of the wrapper:
one passing check, then pending + failed + skipped gives four checks total.
Two human output lines are the issue's explicit maximum. Exit codes use Bash
conventions: zero succeeds, one fails, two denotes incorrect usage.
"""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/github/gh-pr-status.sh"
FIELDS = "number,state,statusCheckRollup,reviewDecision,reviewRequests,reviews"
# Literal GitHub CheckRun/StatusContext examples; no values come from the wrapper.
STATUS = r'''{"number":1308,"state":"OPEN","statusCheckRollup":[{"__typename":"CheckRun","status":"COMPLETED","conclusion":"SUCCESS"}],"reviewDecision":"REVIEW_REQUIRED","reviewRequests":[{"__typename":"User","login":"reviewer"},{"__typename":"Team","name":"Review group","slug":"review-group"}],"reviews":[{"author":{"login":"maintainer"},"state":"APPROVED"}]}'''
MIXED = r'''{"number":1308,"state":"OPEN","statusCheckRollup":[{"__typename":"CheckRun","status":"COMPLETED","conclusion":"SUCCESS"},{"__typename":"CheckRun","status":"IN_PROGRESS","conclusion":""},{"__typename":"StatusContext","state":"FAILURE"},{"__typename":"CheckRun","status":"COMPLETED","conclusion":"SKIPPED"}],"reviewDecision":"REVIEW_REQUIRED","reviewRequests":[],"reviews":[]}'''
EXPECTED = (
    "PR #1308 OPEN | checks: 1 passed, 0 pending, 0 failed, 0 skipped, 0 unknown\n"
    "Review decision: REVIEW_REQUIRED | requested: reviewer, Review group | "
    "reviews: maintainer=APPROVED\n"
)


@pytest.fixture
def gh_stub(tmp_path):
    """Allow exactly three read operations; log and reject everything else."""
    binary = tmp_path / "gh"
    binary.write_text(
        f"#!{sys.executable}\n"
        + '''import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
with Path(os.environ["GH_STUB_LOG"]).open("a", encoding="utf-8", newline="\\n") as stream:
    stream.write(json.dumps(args) + "\\n")
if args == ["auth", "status"]:
    sys.exit(1 if os.environ.get("GH_STUB_FAIL") == "auth" else 0)
if args == ["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]:
    if os.environ.get("GH_STUB_FAIL") == "repo":
        sys.exit(1)
    print("maintainer/repository")
    sys.exit(0)
fields = "number,state,statusCheckRollup,reviewDecision,reviewRequests,reviews"
allowed = ["--repo", "maintainer/repository", "--json", fields]
if args[:2] == ["pr", "view"] and "--repo" in args and args[2].startswith("--"):
    print("argument required when using the --repo flag", file=sys.stderr)
    sys.exit(1)
if args in (["pr", "view", "--json", fields], ["pr", "view", "1308", *allowed]):
    if os.environ.get("GH_STUB_FAIL") == "pr":
        print("upstream diagnostic must remain private", file=sys.stderr)
        sys.exit(1)
    print(os.environ["GH_STUB_RESPONSE"])
    sys.exit(0)
print("refused: command is outside the read-only allowlist", file=sys.stderr)
sys.exit(2)
''', encoding="utf-8", newline="\n"
    )
    binary.chmod(0o755)  # POSIX executable permissions for the disposable stub.
    log = tmp_path / "calls.jsonl"
    env = dict(os.environ)
    env.update(
        PATH=f"{tmp_path}{os.pathsep}{env['PATH']}",
        GH_STUB_LOG=str(log),
        GH_STUB_RESPONSE=STATUS,
        GH_PAGER="cat",
    )
    env.pop("GH_STUB_FAIL", None)
    return env, log, tmp_path


def run_status(gh_stub, *args, response=None, failure=None):
    env, _, directory = gh_stub
    env = dict(env)
    if response is not None:
        env["GH_STUB_RESPONSE"] = response
    if failure:
        env["GH_STUB_FAIL"] = failure
    return subprocess.run(
        ["bash", str(SCRIPT), *args], cwd=directory, env=env,
        capture_output=True, text=True, check=False,
    )


def calls(gh_stub):
    return [json.loads(line) for line in gh_stub[1].read_text(encoding="utf-8").splitlines()]


def test_explicit_pr_status(gh_stub):
    result = run_status(gh_stub, "1308")
    assert result.returncode == 0, result.stderr
    assert result.stdout == EXPECTED
    assert len(result.stdout.splitlines()) == 2
    assert result.stderr == ""
    assert calls(gh_stub)[-1] == [
        "pr", "view", "1308", "--repo", "maintainer/repository", "--json", FIELDS,
    ]


def test_default_branch_status(gh_stub):
    result = run_status(gh_stub)
    assert result.returncode == 0, result.stderr
    assert result.stdout == EXPECTED
    assert len(result.stdout.splitlines()) == 2
    assert calls(gh_stub)[-1] == [
        "pr", "view", "--json", FIELDS,
    ]


@pytest.mark.parametrize("args", [("1308", "--json"), ("--json", "1308"), ("--json",)])
def test_json_status(gh_stub, args):
    result = run_status(gh_stub, *args)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == json.loads(STATUS)
    assert len(result.stdout.splitlines()) == 1
    assert result.stderr == ""


def test_pending_and_failed_checks(gh_stub):
    result = run_status(gh_stub, "1308", response=MIXED)
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "PR #1308 OPEN | checks: 1 passed, 1 pending, 1 failed, 1 skipped, 0 unknown\n"
        "Review decision: REVIEW_REQUIRED | requested: none | reviews: none\n"
    )
    assert len(result.stdout.splitlines()) == 2


@pytest.mark.parametrize("failure,action", [("auth", "gh auth login"), ("repo", "repository"), ("pr", "PR")])
def test_gh_failure_is_nonzero(gh_stub, failure, action):
    result = run_status(gh_stub, "1308", failure=failure)
    assert result.returncode != 0
    assert result.stdout == ""
    assert action in result.stderr
    assert len(result.stderr.splitlines()) == 1
    assert "upstream diagnostic" not in result.stderr


def test_no_github_writes(gh_stub):
    for args in [("1308",), (), ("--json",)]:
        assert run_status(gh_stub, *args).returncode == 0
    expected = [
        ["auth", "status"],
        ["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        ["pr", "view", "1308", "--repo", "maintainer/repository", "--json", FIELDS],
        ["auth", "status"],
        ["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        ["pr", "view", "--json", FIELDS],
        ["auth", "status"],
        ["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        ["pr", "view", "--json", FIELDS],
    ]
    assert calls(gh_stub) == expected


@pytest.mark.parametrize("args", [("--web",), ("--repo", "other"), ("1308", "1308"), ("0",), ("--json", "--json")])
def test_invalid_arguments_do_not_call_gh(gh_stub, args):
    result = run_status(gh_stub, *args)
    assert result.returncode == 2
    assert "Usage:" in result.stderr
    assert not gh_stub[1].exists()


@pytest.mark.parametrize("response", ["not json", "{}", "[]", '{"number":1308,"state":"OPEN","statusCheckRollup":"invalid"}'])
def test_invalid_payload_is_nonzero(gh_stub, response):
    result = run_status(gh_stub, "--json", response=response)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "JSON" in result.stderr


def test_no_checks_or_reviews(gh_stub):
    response = r'''{"number":1308,"state":"MERGED","statusCheckRollup":null,"reviewDecision":"","reviewRequests":[],"reviews":[]}'''
    result = run_status(gh_stub, response=response)
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "PR #1308 MERGED | checks: 0 passed, 0 pending, 0 failed, 0 skipped, 0 unknown\n"
        "Review decision: none | requested: none | reviews: none\n"
    )
    assert len(result.stdout.splitlines()) == 2


@pytest.mark.parametrize("name", [r"Review\ngroup", r"Review\u2028group"])
def test_control_characters_stay_within_line_limit(gh_stub, name):
    response = (
        r'''{"number":1308,"state":"OPEN","statusCheckRollup":[],"reviewDecision":"","reviewRequests":[{"name":"'''
        + name + r'''"}],"reviews":[]}'''
    )
    result = run_status(gh_stub, response=response)
    assert result.returncode == 0, result.stderr
    assert "requested: Review group" in result.stdout
    assert len(result.stdout.splitlines()) == 2


# Each literal fixture below contains exactly one check in the stated category.
@pytest.mark.parametrize("check,expected", [
    ('{"__typename":"CheckRun","status":"COMPLETED","conclusion":"FAILURE"}',
     "0 passed, 0 pending, 1 failed, 0 skipped, 0 unknown"),
    ('{"__typename":"CheckRun","status":"QUEUED","conclusion":""}',
     "0 passed, 1 pending, 0 failed, 0 skipped, 0 unknown"),
    ('{"__typename":"CheckRun","status":"COMPLETED","conclusion":"NEUTRAL"}',
     "0 passed, 0 pending, 0 failed, 1 skipped, 0 unknown"),
    ('{"__typename":"CheckRun","status":"COMPLETED","conclusion":"UNRECOGNIZED"}',
     "0 passed, 0 pending, 0 failed, 0 skipped, 1 unknown"),
    ('{"__typename":"StatusContext","state":"PENDING"}',
     "0 passed, 1 pending, 0 failed, 0 skipped, 0 unknown"),
    ('{"__typename":"StatusContext","state":"ERROR"}',
     "0 passed, 0 pending, 1 failed, 0 skipped, 0 unknown"),
    ('{"__typename":"UnrecognizedCheck"}',
     "0 passed, 0 pending, 0 failed, 0 skipped, 1 unknown"),
])
def test_check_state_categories(gh_stub, check, expected):
    response = (
        r'''{"number":1308,"state":"OPEN","statusCheckRollup":['''
        + check + r'''],"reviewDecision":"","reviewRequests":[],"reviews":[]}'''
    )
    result = run_status(gh_stub, response=response)
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        f"PR #1308 OPEN | checks: {expected}\n"
        "Review decision: none | requested: none | reviews: none\n"
    )
    assert len(result.stdout.splitlines()) == 2
