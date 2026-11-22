"""Execute the exact documented program against independent Git fixtures.

Counts in CASES are hand calculations over the literal records below: each
tracked entry counts once, including both index/worktree changes on one path;
each ?? entry counts once; rename source records do not count. Revision counts
are independently stipulated local-only and upstream-only commit sets, with
cardinalities recorded in each fixture. No expectation imports the example.
Porcelain layout and revision ordering follow git-status(1), 'Porcelain Format
Version 1', and git-rev-list(1), '--left-right' and '--count'.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]  # test file -> docs -> tests -> root
EXAMPLE = ROOT / "docs/examples/repository-origin-status.md"
HEADER = "Repo | Branch | Ahead | Behind | Uncommitted | Untracked | Status"
# Same subprocess budget as PROBE_TIMEOUT_SECONDS in the existing
# tests/docs/test_python_runner_entrypoint_contract.py::example_results fixture.
QUERY_TIMEOUT_SECONDS = 30

# Columns: name, raw porcelain, local-only IDs, upstream-only IDs, expected row.
# Commit IDs are symbolic fixture set members; their cardinalities, rather than
# a computation by the example, justify each literal revision count below.
CASES = [
    ("workspace-hub", "", [], [], ("0", "0", "0", "0", "clean")),
    ("ahead", "", ["a", "b", "c"], [], ("3", "0", "0", "0", "ahead")),
    ("behind", "", [], ["d", "e"], ("0", "2", "0", "0", "behind")),
    ("diverged", "", ["a", "b"], ["c", "d", "e"],
     ("2", "3", "0", "0", "diverged")),
    ("tracked-changes", "M  staged\0 M unstaged\0MM both\0 D deleted\0", [], [],
     ("0", "0", "4", "0", "dirty")),
    ("untracked", "?? first\0?? second\nline\0", [], [],
     ("0", "0", "0", "2", "dirty")),
    ("no-upstream", "", None, None, ("?", "?", "0", "0", "unknown upstream")),
    ("dirty-ahead", " M changed\0", ["a", "b", "c"], [],
     ("3", "0", "1", "0", "dirty")),
    ("dirty-behind", " M changed\0", [], ["d", "e"],
     ("0", "2", "1", "0", "dirty")),
    ("dirty-diverged", " M changed\0?? extra\0", ["a", "b"], ["c", "d", "e"],
     ("2", "3", "1", "1", "dirty")),
    ("untracked-diverged", "?? extra\0", ["a", "b"], ["c", "d", "e"],
     ("2", "3", "0", "1", "dirty")),
    ("dirty-no-upstream", " M changed\0", None, None,
     ("?", "?", "1", "0", "dirty (unknown upstream)")),
    # In -z format a rename has destination then source, even if the source
    # happens to resemble an untracked record or contains a newline.
    ("rename", "R  destination\0?? source\nname\0", [], [],
     ("0", "0", "1", "0", "dirty")),
    ("detached", "", None, None, ("?", "?", "0", "0", "unknown upstream")),
    ("unborn", "?? initial\0", None, None,
     ("?", "?", "0", "1", "dirty (unknown upstream)")),
]


FAKE_GIT = r'''
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
with open(os.environ["QUERY_LOG"], "a", encoding="utf-8", newline="\n") as log:
    log.write(json.dumps(args) + "\n")
allowed_env = {"GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"}
assert {k: v for k, v in os.environ.items() if k.startswith("GIT_")} == allowed_env
assert args[:1] == ["-C"], "repository must be an explicit argument"
repo = Path(args[1])
assert repo.is_absolute(), "repository must be resolved independently of caller cwd"
query = args[2:]
fixtures = json.loads(Path(os.environ["FIXTURES"]).read_text(encoding="utf-8"))
case = fixtures[repo.name]
if query == ["status", "--porcelain=v1", "-z", "--untracked-files=all",
             "--ignore-submodules=none"]:
    reply = case["status"]
elif query == ["symbolic-ref", "--quiet", "--short", "HEAD"]:
    reply = case["branch"] + "\n"
    if case["branch"] == "(detached)":
        raise SystemExit(True)  # symbolic-ref(1): detached HEAD is nonzero
elif query == ["rev-parse", "--verify", "--quiet", "@{upstream}"]:
    if case["counts"] is None:
        raise SystemExit(True)  # rev-parse(1): unresolved revision is nonzero
    reply = "upstream-object\n"
elif query == ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"]:
    assert case["counts"] is not None, "missing upstream must not be counted"
    reply = case["counts"]
else:
    raise SystemExit("forbidden Git operation")
if case.get("fail") == query[0]:
    # git-symbolic-ref(1), Exit status: 128 distinguishes fatal errors from
    # detached HEAD (one). The same fatal convention is used for other queries.
    raise SystemExit(128)
sys.stdout.write(reply)
'''


def documented_program():
    blocks = re.findall(r"^```python\n(.*?)^```$", EXAMPLE.read_text(encoding="utf-8"), re.M | re.S)
    (program,) = blocks  # exactly the runnable Python fence, without rewriting
    return program


def snapshot(directory):
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in directory.rglob("*")
        if path.is_file() and path.name != "queries.jsonl"
    }


@pytest.fixture
def sandbox(tmp_path):
    executable_dir = tmp_path / "fake tools"
    executable_dir.mkdir()
    fake = executable_dir / "git"
    fake.write_text(f"#!{sys.executable}\n" + FAKE_GIT, encoding="utf-8", newline="\n")
    fake.chmod(0o755)  # chmod(1): executable by the user, group and others
    fixtures = {}
    repos = []
    for name, status, local_ids, remote_ids, _ in CASES:
        # Spaces and shell metacharacters must survive argument-list calls.
        repo = tmp_path / "repositories ; literal" / name
        metadata = repo / ".git"
        metadata.mkdir(parents=True)
        for filename in ("HEAD", "index", "config"):
            (metadata / filename).write_text("preserve metadata\n", encoding="utf-8", newline="\n")
        (repo / "source.txt").write_text("preserve source\n", encoding="utf-8", newline="\n")
        fixtures[name] = {
            "status": status,
            "branch": "(detached)" if name == "detached" else "topic/example",
            "counts": None if local_ids is None else f"{len(local_ids)}\t{len(remote_ids)}\n",
        }
        repos.append(repo)
    fixture_file = tmp_path / "fixtures.json"
    fixture_file.write_text(json.dumps(fixtures), encoding="utf-8", newline="\n")
    program = tmp_path / "repository_origin_status.py"
    program.write_text(documented_program(), encoding="utf-8", newline="\n")
    env = os.environ.copy()
    env.update({
        "PATH": str(executable_dir) + os.pathsep + env.get("PATH", ""),
        "FIXTURES": str(fixture_file),
        "QUERY_LOG": str(tmp_path / "queries.jsonl"),
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    # The example must discard inherited repository/index/config bindings.
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0"):
        env[key] = "inherited-invalid-binding"
    return tmp_path, program, repos, env


def execute(sandbox, repos=None):
    directory, program, all_repos, env = sandbox
    selected = all_repos if repos is None else repos
    return subprocess.run(
        [sys.executable, str(program), *(str(repo) for repo in selected)],
        cwd=directory, env=env, text=True, capture_output=True,
        timeout=QUERY_TIMEOUT_SECONDS,
    )


@pytest.fixture
def result(sandbox):
    before = snapshot(sandbox[0])
    document_before = EXAMPLE.read_bytes()
    tests_before = Path(__file__).read_bytes()
    output = execute(sandbox)
    assert output.returncode == 0, output.stderr
    assert output.stderr == ""
    assert snapshot(sandbox[0]) == before
    assert EXAMPLE.read_bytes() == document_before
    assert Path(__file__).read_bytes() == tests_before
    lines = output.stdout.splitlines()
    assert lines[0] == HEADER
    rows = [line.split(" | ") for line in lines[1:]]
    assert [row[0] for row in rows] == [case[0] for case in CASES]
    return {row[0]: row[1:] for row in rows}


@pytest.mark.parametrize("name,status,local_ids,remote_ids,expected", CASES,
                         ids=[case[0] for case in CASES])
def test_verbatim_example_rows(result, name, status, local_ids, remote_ids, expected):
    branch = "(detached)" if name == "detached" else "topic/example"
    assert result[name] == [branch, *expected]


def test_only_expected_read_queries(sandbox, result):
    directory, _, repos, env = sandbox
    queries = [json.loads(line) for line in Path(env["QUERY_LOG"]).read_text(encoding="utf-8").splitlines()]
    expected = []
    for repo, case in zip(repos, CASES):
        commands = [
            ["status", "--porcelain=v1", "-z", "--untracked-files=all",
             "--ignore-submodules=none"],
            ["symbolic-ref", "--quiet", "--short", "HEAD"],
            ["rev-parse", "--verify", "--quiet", "@{upstream}"],
        ]
        if case[2] is not None:
            commands.append(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
        expected.extend([["-C", str(repo), *command] for command in commands])
    assert queries == expected


@pytest.mark.parametrize("operation", ["fetch", "pull", "push", "add", "commit", "config"])
def test_fake_git_rejects_write_operations(sandbox, operation):
    directory, _, repos, env = sandbox
    env = {key: value for key, value in env.items() if not key.startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    before = snapshot(directory)
    output = subprocess.run(
        ["git", "-C", str(repos[0]), operation], cwd=directory, env=env,
        capture_output=True, text=True, timeout=QUERY_TIMEOUT_SECONDS,
    )
    assert output.returncode != 0
    assert "forbidden Git operation" in output.stderr
    assert snapshot(directory) == before


@pytest.mark.parametrize("operation", ["status", "symbolic-ref", "rev-list"])
def test_query_failure_is_not_reported_as_clean(sandbox, operation):
    _, _, repos, env = sandbox
    fixture_file = Path(env["FIXTURES"])
    fixtures = json.loads(fixture_file.read_text(encoding="utf-8"))
    fixtures["workspace-hub"]["fail"] = operation
    fixture_file.write_text(json.dumps(fixtures), encoding="utf-8", newline="\n")
    before = snapshot(sandbox[0])
    output = execute(sandbox, repos[:1])
    assert output.returncode != 0
    assert "clean" not in output.stdout
    assert snapshot(sandbox[0]) == before


def test_requires_explicit_repository_list(sandbox):
    output = execute(sandbox, [])
    assert output.returncode != 0
    assert "usage:" in output.stderr.lower()



def test_branch_delimiter_is_encoded(sandbox):
    _, _, repos, env = sandbox
    fixture_file = Path(env["FIXTURES"])
    fixtures = json.loads(fixture_file.read_text(encoding="utf-8"))
    fixtures["workspace-hub"]["branch"] = "topic|example"
    fixture_file.write_text(json.dumps(fixtures), encoding="utf-8", newline="\n")
    output = execute(sandbox, repos[:1])
    assert output.returncode == 0, output.stderr
    assert output.stdout.splitlines() == [
        HEADER, "workspace-hub | topic%7Cexample | 0 | 0 | 0 | 0 | clean",
    ]


@pytest.mark.parametrize("change", ["tracked", "untracked"])
def test_real_git_submodule_ignore_cannot_hide_changes(tmp_path, change):
    # Disposable Git objects avoid commits or configuration changes in the caller.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")

    def git(repo, *args, data=None):
        result = subprocess.run(
            ["git", "-C", str(repo), *args], input=data, env=env,
            capture_output=True, check=True, timeout=QUERY_TIMEOUT_SECONDS,
        )
        return result.stdout.strip().decode("utf-8")

    def record_tree(repo):
        tree = git(repo, "write-tree")
        # git-commit-tree(1), Commit Information: literal synthetic object metadata.
        raw = (f"tree {tree}\nauthor Fixture <> 0 +0000\n"
               "committer Fixture <> 0 +0000\n\nFixture\n")
        oid = git(repo, "hash-object", "-t", "commit", "-w", "--stdin",
                  data=raw.encode("utf-8"))
        git(repo, "update-ref", "HEAD", oid)
        return oid

    repo = tmp_path / "parent"
    repo.mkdir()
    git(repo, "init", "--initial-branch=main")
    module = repo / "module"
    module.mkdir()
    git(module, "init", "--initial-branch=main")
    (module / "tracked.txt").write_text("initial\n", encoding="utf-8", newline="\n")
    git(module, "add", "tracked.txt")
    child_oid = record_tree(module)
    (repo / ".gitmodules").write_text(
        '[submodule "module"]\n\tpath = module\n\turl = ../unused\n',
        encoding="utf-8", newline="\n",
    )
    git(repo, "add", ".gitmodules")
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{child_oid},module")
    record_tree(repo)
    config = repo / ".git/config"
    config.write_text(
        config.read_text(encoding="utf-8")
        + '[submodule "module"]\n\tignore = all\n'
        + '[branch "main"]\n\tremote = .\n\tmerge = refs/heads/main\n',
        encoding="utf-8", newline="\n",
    )
    changed = "tracked.txt" if change == "tracked" else "extra.txt"
    (module / changed).write_text("changed\n", encoding="utf-8", newline="\n")
    # Positive control: the repository setting really suppresses this change.
    assert git(repo, "status", "--porcelain=v1") == ""
    assert git(repo, "status", "--porcelain=v1", "--ignore-submodules=none") == "M module"
    program = tmp_path / "example.py"
    program.write_text(documented_program(), encoding="utf-8", newline="\n")
    before = snapshot(repo)
    output = subprocess.run(
        [sys.executable, str(program), str(repo)], env=env,
        text=True, encoding="utf-8", capture_output=True,
        timeout=QUERY_TIMEOUT_SECONDS,
    )
    assert output.returncode == 0, output.stderr
    assert output.stdout.splitlines() == [
        HEADER, "parent | main | 0 | 0 | 1 | 0 | dirty",
    ]
    assert snapshot(repo) == before
