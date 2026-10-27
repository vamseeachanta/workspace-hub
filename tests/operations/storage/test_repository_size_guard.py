"""G1 synthetic examples; each expected result uses independent integer arithmetic.

The policy inputs below are test data, not recommended storage limits. Tree
records follow Git git-ls-tree(1), version 2.42.0, Output Format (-l and -z):
https://git-scm.com/docs/git-ls-tree/2.42.0#_output_format
"""

import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from operations.storage import repository_size_guard as guard

SCRIPT = Path(__file__).resolve().parents[3] / (
    "scripts/operations/storage/repository_size_guard.py"
)


def policy(**changes):
    """Synthetic limits: total <= 10 bytes, ordinary blob <= 5 bytes."""
    return {"max_total_bytes": 10, "max_file_bytes": 5, "exceptions": {}, **changes}


def test_total_and_file_boundary():
    """5 + 5 = 10; equality meets both caps, so PASS."""
    result = guard.evaluate({"a": 5, "b": 5}, policy())
    assert result == {
        "status": "PASS", "total_bytes": 10, "max_total_bytes": 10,
        "file_count": 2, "total_exceeded": False, "violations": [],
    }


def test_total_over_budget_without_large_file():
    """4 + 4 + 3 = 11 > 10, while each term <= 5; total alone blocks."""
    result = guard.evaluate({"a": 4, "b": 4, "c": 3}, policy())
    assert result["status"] == "BLOCK"
    assert result["total_bytes"] == 11
    assert result["total_exceeded"] is True
    assert result["violations"] == []


def test_file_over_cap_without_total_excess():
    """6 <= 10 but 6 > 5; the individual file alone blocks."""
    result = guard.evaluate({"a": 6}, policy())
    assert result["status"] == "BLOCK"
    assert result["violations"] == [{"path": "a", "size_bytes": 6, "limit_bytes": 5}]


def test_exact_exception_has_own_cap_and_still_counts_toward_total():
    """7 + 3 = 10 passes; 7 + 4 = 11 blocks; exception cap 7 rejects 8."""
    limits = policy(exceptions={"data/a": 7})
    assert guard.evaluate({"data/a": 7, "b": 3}, limits)["status"] == "PASS"
    assert guard.evaluate({"data/a": 7, "b": 4}, limits)["status"] == "BLOCK"
    assert guard.evaluate({"data/a": 8}, limits)["status"] == "BLOCK"
    assert guard.evaluate({"data/ab": 7}, limits)["status"] == "BLOCK"


def test_multi_violation_report_is_order_independent():
    """Full reports follow path order, including exact-path exception decisions."""
    # Hand-calculated fixture bytes, not storage recommendations:
    # 9 + 7 + 6 + 7 + 5 = 34 > total cap 30 across five entries.
    # Ordinary cap 5: alpha 6 > 5, data/ab 7 > 5, zeta 9 > 5;
    # within 5 == 5 passes. Exact exception data/a 7 == 7 passes,
    # but its cap does not apply to data/ab despite the shared prefix.
    entries = {"zeta": 9, "data/a": 7, "alpha": 6, "data/ab": 7, "within": 5}
    limits = {
        "max_total_bytes": 30,
        "max_file_bytes": 5,
        "exceptions": {"data/a": 7},
    }
    expected = {
        "status": "BLOCK",
        "total_bytes": 34,
        "max_total_bytes": 30,
        "file_count": 5,
        "total_exceeded": True,
        "violations": [
            {"path": "alpha", "size_bytes": 6, "limit_bytes": 5},
            {"path": "data/ab", "size_bytes": 7, "limit_bytes": 5},
            {"path": "zeta", "size_bytes": 9, "limit_bytes": 5},
        ],
    }
    for items in (entries.items(), reversed(entries.items()), sorted(entries.items())):
        result = guard.evaluate(dict(items), limits)
        assert result == expected
        assert [item["path"] for item in result["violations"]] == [
            "alpha", "data/ab", "zeta",
        ]


def test_evaluate_preserves_inputs():
    """Repeated evaluation preserves entries and the nested exception policy."""
    # Independent fixture arithmetic: 9 + 7 + 6 = 22 > total cap 20.
    # Ordinary cap 5 rejects zeta 9 > 5 and alpha 6 > 5;
    # the exact exception permits data/a 7 == 7. These are fixture caps only.
    entries = {"zeta": 9, "data/a": 7, "alpha": 6}
    limits = {
        "max_total_bytes": 20,
        "max_file_bytes": 5,
        "exceptions": {"data/a": 7},
    }
    entries_before = deepcopy(entries)
    limits_before = deepcopy(limits)
    for _ in ("first", "repeat"):
        guard.evaluate(entries, limits)
        assert entries == entries_before
        assert limits == limits_before
        assert list(entries) == list(entries_before)
        assert list(limits) == list(limits_before)
        assert list(limits["exceptions"]) == list(limits_before["exceptions"])


def test_empty_tree_and_zero_caps():
    """An empty sum is 0; an empty blob also contributes 0, meeting zero caps."""
    limits = policy(max_total_bytes=0, max_file_bytes=0)
    assert guard.evaluate({}, limits)["status"] == "PASS"
    assert guard.evaluate({"empty": 0}, limits)["status"] == "PASS"


@pytest.mark.parametrize("change", [
    {"max_total_bytes": -1}, {"max_file_bytes": True},
    {"max_total_bytes": 1.5}, {"max_file_bytes": "5"},
    {"exceptions": []}, {"exceptions": {"a": -1}},
    {"exceptions": {"a": False}}, {"unexpected": 10},
])
def test_invalid_policy(tmp_path, change):
    """Negative, noninteger, Boolean and unrecognized limits cannot be evaluated."""
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy(**change)))
    with pytest.raises(guard.NotEvaluated):
        guard.load_policy(path)


@pytest.mark.parametrize("path", ["/data/a", "../a", "a/../b", "a//b", "./a", "", "a\\b"])
def test_exception_must_be_canonical_relative_path(tmp_path, path):
    """An exception identifies exactly one tree-relative path, never a pattern."""
    file = tmp_path / "policy.json"
    file.write_text(json.dumps(policy(exceptions={path: 7})))
    with pytest.raises(guard.NotEvaluated):
        guard.load_policy(file)


@pytest.mark.parametrize("raw", [
    '{}', '[]', '{',
    '{"max_total_bytes":10,"max_file_bytes":5,"exceptions":{},"max_file_bytes":9}',
    '{"max_total_bytes":10,"max_file_bytes":5,"exceptions":{"a":7,"a":9}}',
])
def test_incomplete_or_ambiguous_policy(tmp_path, raw):
    """Missing fields, malformed JSON and duplicate keys supply no usable criterion."""
    path = tmp_path / "policy.json"
    path.write_text(raw)
    with pytest.raises(guard.NotEvaluated):
        guard.load_policy(path)


def test_tree_records_preserve_paths_and_count_each_entry():
    """Two names for the same 3-byte blob plus a 2-byte symlink total 3+3+2=8."""
    oid = b"a" * 40  # Synthetic SHA-1 object name in the cited Git output format.
    records = (
        b"100644 blob " + oid + b" 3\ta name\nwith tab\t\0"
        b"100755 blob " + oid + b" 3\tb\0"
        b"120000 blob " + oid + b" 2\tlink\0"
    )
    assert guard.parse_tree(records) == {"a name\nwith tab\t": 3, "b": 3, "link": 2}


@pytest.mark.parametrize("records", [
    b"100644 blob abc -\ta\0", b"broken\0", b"100644 blob abc 5\ta",
    b"100644 blob abc -5\ta\0", b"160000 commit abc -\tmodule\0",
    b"100644 blob abc 1\ta\0" * 2,
])
def test_unknown_sizes_gitlinks_and_bad_records_are_not_evaluated(records):
    """Incomplete trees, duplicate paths and unmeasured submodule content cannot pass."""
    with pytest.raises(guard.NotEvaluated):
        guard.parse_tree(records)


def run_cli(repo, settings, revision="HEAD", env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), "--policy", str(settings),
         "--revision", revision], capture_output=True, text=True, env=env, check=False,
    )


def git(repo, *args, input=None):
    env = guard.git_environment()
    return subprocess.run(
        ["git", "-C", str(repo), *args], input=input, capture_output=True,
        check=True, env=env,
    ).stdout.strip()


@pytest.fixture
def tree(tmp_path):
    """Create only objects in a disposable repository; no commit or index is needed."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "--quiet")
    blob = git(repo, "hash-object", "-w", "--stdin", input=b"abc")
    tree_id = git(repo, "mktree", input=b"100644 blob " + blob + b"\ta\n").decode()
    settings = tmp_path / "policy.json"
    settings.write_text(json.dumps(policy()))
    return repo, settings, tree_id


def test_cli_real_tree_ignores_working_files_and_inherited_git_bindings(tree, tmp_path):
    """The tree contains 3 bytes; an untracked 11-byte file is outside that tree."""
    repo, settings, revision = tree
    (repo / "untracked").write_bytes(b"x" * 11)
    env = {**os.environ, "GIT_DIR": str(tmp_path / "absent"),
           "GIT_WORK_TREE": str(tmp_path), "GIT_COMMON_DIR": str(tmp_path / "absent")}
    result = run_cli(repo, settings, revision, env)
    assert result.returncode == 0
    assert json.loads(result.stdout)["total_bytes"] == 3
    assert (repo / "untracked").read_bytes() == b"x" * 11


def test_cli_block(tree):
    """A 3-byte tree exceeds an explicitly supplied 2-byte total cap."""
    repo, settings, revision = tree
    settings.write_text(json.dumps(policy(max_total_bytes=2)))
    result = run_cli(repo, settings, revision)
    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "BLOCK"


@pytest.mark.parametrize("revision", ["missing", "--all"])
def test_cli_unreadable_revision(tree, revision):
    """Unknown revisions and option-like inputs supply no measured tree."""
    repo, settings, _ = tree
    # Equals form ensures argparse passes an option-like value to Git validation.
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), "--policy", str(settings),
         f"--revision={revision}"], capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"
    assert result.stderr == ""


def test_cli_missing_policy_does_not_publish_absolute_path(tree, tmp_path):
    """Unavailable settings produce an unknown outcome with no local path disclosure."""
    repo, _, revision = tree
    result = run_cli(repo, tmp_path / "missing", revision)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"
    assert str(tmp_path) not in result.stdout + result.stderr


def test_large_byte_counts_are_not_rounded():
    """10**20 + 1 is strictly greater than 10**20 by one byte; BLOCK."""
    cap = 10**20  # Synthetic integer-arithmetic stress input, not a storage criterion.
    result = guard.evaluate({"a": cap + 1}, policy(max_file_bytes=cap, max_total_bytes=cap))
    assert result["status"] == "BLOCK"
    assert result["total_bytes"] == cap + 1


def test_offline_environment_forbids_transport(monkeypatch):
    """An empty protocol allow-list permits no Git transport, even on older Git."""
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "https")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "remote.origin.url")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "untrusted")
    env = guard.git_environment()
    assert env["GIT_ALLOW_PROTOCOL"] == ""
    assert env["GIT_NO_LAZY_FETCH"] == "1"
    assert "GIT_CONFIG_COUNT" not in env
    assert "GIT_CONFIG_KEY_0" not in env


def test_cli_missing_git_is_not_evaluated(tree, tmp_path):
    """An unavailable Git executable is unknown, never a zero-byte PASS."""
    repo, settings, revision = tree
    env = {**os.environ, "PATH": str(tmp_path / "absent")}
    result = run_cli(repo, settings, revision, env)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"
    assert result.stderr == ""


@pytest.mark.parametrize("kind", ["integer", "nesting"])
def test_policy_parser_resource_limits_return_unknown(tree, kind):
    """Exceed the interpreter's own parsing limit by one, never infer a byte cap."""
    repo, settings, revision = tree
    if kind == "integer":
        limit = sys.get_int_max_str_digits()
        if not limit:
            pytest.skip("interpreter integer parsing limit disabled")
        raw = '{"max_total_bytes":' + "9" * (limit + 1) + '}'
    else:
        depth = sys.getrecursionlimit() + 1
        raw = "[" * depth + "0" + "]" * depth
    settings.write_text(raw)
    result = run_cli(repo, settings, revision)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"
    assert result.stderr == ""


def test_missing_blob_is_not_evaluated(tree):
    """A tree naming an absent blob has no known byte sum and cannot pass."""
    repo, settings, existing_tree = tree
    # Match this disposable repository's object-name width; the repeated digit
    # creates an absent identifier, not an assumed content-size value.
    missing = b"1" * len(existing_tree)
    revision = git(repo, "mktree", "--missing",
                   input=b"100644 blob " + missing + b"\tmissing\n").decode()
    result = run_cli(repo, settings, revision)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "NOT_EVALUATED"
    assert result.stderr == ""
