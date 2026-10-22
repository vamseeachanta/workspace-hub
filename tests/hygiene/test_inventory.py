"""Synthetic fixtures use independent hand calculations, stated beside each test."""

import importlib.util
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/hygiene/inventory.py"


def load_module():
    spec = importlib.util.spec_from_file_location("inventory", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def inventory():
    return load_module()


def config(root, **extra):
    # Fixture bound: the examples contain fewer than 100 files (hand count).
    return {
        "root": str(root),
        "repos": [],
        "cache_allow": ["cache*"],
        "max_files": 100,
        **extra,
    }


def test_core_prunes_repositories_worktrees_cache_and_loop(tmp_path, inventory):
    """Two repositories + cache + loop excluded; one stray of 3 bytes remains."""
    root = tmp_path / "tree"
    root.mkdir()
    (root / "repo" / ".git").mkdir(parents=True)
    (root / "repo" / "tracked").write_bytes(b"ignored")
    (root / "worktree").mkdir()
    (root / "worktree" / ".git").write_text("gitdir: ../metadata")
    (root / "worktree" / "tracked").write_bytes(b"ignored")
    (root / "cache-output").mkdir()
    (root / "cache-output" / "artifact").write_bytes(b"ignored")
    (root / "stray").write_bytes(b"abc")
    (root / "loop").symlink_to(root, target_is_directory=True)
    files, repos = inventory.scan(config(root))
    assert [item["path"] for item in files] == ["stray"]
    assert files[0]["size"] == 3
    assert files[0]["mtime"] == (root / "stray").stat().st_mtime
    assert [path.name for path in repos] == ["repo", "worktree"]


def test_explicit_repository_and_followed_loop(tmp_path, inventory):
    """One declared repo is pruned; loop is visited zero extra times: 1 file."""
    (tmp_path / "declared").mkdir()
    (tmp_path / "declared" / "hidden").write_bytes(b"hidden")
    (tmp_path / "visible").write_bytes(b"x")
    (tmp_path / "loop").symlink_to(tmp_path, target_is_directory=True)
    files, repos = inventory.scan(
        config(tmp_path, repos=["declared"], follow_symlinks=True)
    )
    assert [item["path"] for item in files] == ["visible"]
    assert repos == [tmp_path / "declared"]


def test_never_opens_stray_contents(tmp_path, inventory, monkeypatch):
    """One unreadable-content probe still yields its 3-byte metadata."""
    (tmp_path / "file").write_bytes(b"abc")

    def forbidden(*args, **kwargs):
        raise AssertionError("content opened")

    monkeypatch.setattr(Path, "open", forbidden)
    files, _ = inventory.scan(config(tmp_path))
    assert files[0]["size"] == 3


def test_limit_fails_instead_of_silently_truncating(tmp_path, inventory):
    """Two files exceed the configured hand-count bound of one."""
    (tmp_path / "a").touch()
    (tmp_path / "b").touch()
    with pytest.raises(ValueError, match="max_files"):
        inventory.scan(config(tmp_path, max_files=1))


@pytest.mark.parametrize(
    "extra",
    [
        {"max_files": -1},
        {"max_files": True},
        {"follow_symlinks": "yes"},
        {"repos": "repo"},
        {"cache_allow": [1]},
    ],
)
def test_invalid_config_rejected(tmp_path, inventory, extra):
    """Reject type errors and a negative limit; no files are required."""
    with pytest.raises(ValueError):
        inventory.scan(config(tmp_path, **extra))


@pytest.mark.parametrize(
    "name,category",
    [
        ("run.py", "script"),
        ("notes.md", "document"),
        ("rows.csv", "data"),
        ("view.png", "image"),
        ("bundle.zip", "archive"),
        ("run.log", "log"),
        ("unit.o", "build output"),
        ("mystery.xyz", "unknown"),
        ("UPPER.PY", "script"),
        ("plain", "unknown"),
    ],
)
def test_classification_conventions(tmp_path, inventory, name, category):
    """Each explicit example has one byte and its declared conventional category."""
    (tmp_path / name).write_bytes(b"x")
    result = inventory.build_manifest(config(tmp_path), clock=lambda: FIXED)
    assert result["files"][0]["category"] == category
    assert result["totals"]["categories"][category]["bytes"] == 1


# Fixed synthetic instant, not a measured acceptance limit (hand-worked fixture).
FIXED = datetime(2026, 1, 3, tzinfo=UTC)


def test_groups_mtime_and_largest(tmp_path, inventory):
    """Sizes 1+2+3=6; times 10,20,30 give oldest 10/newest 30.

    Top-level '.' has one file/1 byte; 'notes' has two files/5 bytes.
    The three largest sort 3,2,1; no model-derived expected values.
    """
    (tmp_path / "notes").mkdir()
    for name, size, stamp in [
        ("a.md", 1, 10),
        ("notes/b.md", 2, 20),
        ("notes/c.md", 3, 30),
    ]:
        path = tmp_path / name
        path.write_bytes(b"x" * size)
        os.utime(path, (stamp, stamp))
    result = inventory.build_manifest(config(tmp_path), clock=lambda: FIXED)
    totals = result["totals"]
    assert {
        key: totals[key] for key in ("count", "bytes", "oldest_mtime", "newest_mtime")
    } == {"count": 3, "bytes": 6, "oldest_mtime": 10, "newest_mtime": 30}
    assert totals["categories"]["document"]["count"] == 3
    assert totals["top_level"]["."]["bytes"] == 1
    assert totals["top_level"]["notes"]["bytes"] == 5
    assert [row["size"] for row in totals["largest_files"]] == [3, 2, 1]
    assert [
        row["size"] for row in totals["categories"]["document"]["largest_files"]
    ] == [3, 2, 1]


def test_custom_name_and_extension_table(tmp_path, inventory):
    """Two files, one custom name and one extension; both map to document."""
    (tmp_path / "SPECIAL").touch()
    (tmp_path / "x.note").touch()
    cfg = config(
        tmp_path,
        categories={"document": {"extensions": [".note"], "names": ["special"]}},
    )
    result = inventory.build_manifest(cfg, clock=lambda: FIXED)
    assert [row["category"] for row in result["files"]] == ["document", "document"]


def test_largest_twenty_and_tie_break(tmp_path, inventory):
    """21 equal 1-byte files: top 20 are lexically first 20 (task slice 2)."""
    for index in range(21):
        (tmp_path / f"item{index:02}.md").write_bytes(b"x")
    totals = inventory.build_manifest(config(tmp_path), clock=lambda: FIXED)["totals"]
    assert len(totals["largest_files"]) == 20
    assert totals["largest_files"][-1]["path"] == "item19.md"


def test_manifest_determinism_and_root_as_given(tmp_path, inventory, monkeypatch):
    """Two fixed-clock runs on one 3-byte file must have identical JSON bytes."""
    monkeypatch.chdir(tmp_path)
    Path("tree").mkdir()
    Path("tree/a").write_bytes(b"abc")
    Path("cfg.json").write_text(json.dumps(config("tree")))
    for output in ("first.json", "second.json"):
        assert (
            inventory.main(
                ["--config", "cfg.json", "--out", output], clock=lambda: FIXED
            )
            == 0
        )
    assert Path("first.json").read_bytes() == Path("second.json").read_bytes()
    result = json.loads(Path("first.json").read_text())
    assert result["schema"] == 1  # README Manifest format defines revision 1.
    assert result["root"] == "tree"
    assert result["generated_utc"] == "2026-01-03T00:00:00Z"


@pytest.mark.parametrize("threshold,expected", [(0, 1), (1, 0), (2, 0)])
def test_threshold_exit_codes(tmp_path, inventory, capsys, threshold, expected):
    """One file exceeds 0, equals 1, is below 2; task slice 3 says 'exceed'."""
    root = tmp_path / "tree"
    root.mkdir()
    (root / "a").write_bytes(b"abc")
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config(root)))
    out = tmp_path / "manifest.json"
    assert (
        inventory.main(
            ["--config", str(cfg), "--out", str(out), "--fail-above", str(threshold)],
            clock=lambda: FIXED,
        )
        == expected
    )
    assert capsys.readouterr().out == "stray_files=1 bytes=3 repositories=0\n"
    assert json.loads(out.read_text())["totals"]["count"] == 1


def test_empty_root(tmp_path, inventory):
    """Empty set: count=0, sum=0, extrema=null and largest list empty."""
    result = inventory.build_manifest(config(tmp_path), clock=lambda: FIXED)
    assert result["totals"] == {
        "count": 0,
        "bytes": 0,
        "oldest_mtime": None,
        "newest_mtime": None,
        "largest_files": [],
        "categories": {},
        "top_level": {},
    }


def test_missing_root_is_clear_error_exit_two(tmp_path, inventory, capsys):
    """Task slice 3 specifies exit 2 for missing root, with no manifest."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config(tmp_path / "missing")))
    out = tmp_path / "manifest.json"
    assert inventory.main(["--config", str(cfg), "--out", str(out)]) == 2
    captured = capsys.readouterr()
    assert "root does not exist" in captured.err
    assert not captured.out
    assert not out.exists()


@pytest.mark.parametrize("payload", ["{", "[]", '{"root": "x"}'])
def test_bad_config_does_not_publish_manifest(tmp_path, inventory, payload):
    """Three invalid inputs produce no output, rather than incomplete evidence."""
    cfg = tmp_path / "cfg.json"
    cfg.write_text(payload)
    out = tmp_path / "manifest.json"
    assert inventory.main(["--config", str(cfg), "--out", str(out)]) == 2
    assert not out.exists()


def test_direct_isolated_cli(tmp_path):
    """Zero files plus a zero threshold is a successful isolated invocation."""
    import subprocess
    import sys

    root = tmp_path / "tree"
    root.mkdir()
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config(root)))
    out = tmp_path / "manifest.json"
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(SCRIPT),
            "--config",
            str(cfg),
            "--out",
            str(out),
            "--fail-above",
            "0",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == "stray_files=0 bytes=0 repositories=0\n"


def git(repo, *args, env=None):
    import subprocess

    clean = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    clean.update(env or {})
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        env=clean,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def init_repo(path):
    path.mkdir()
    git(path, "init", "--initial-branch=trunk")
    # Synthetic throwaway identities have no routable address; repository unchanged.
    git(path, "config", "user.name", "Fixture")
    git(path, "config", "user.email", "fixture.invalid")
    git(path, "config", "commit.gpgsign", "false")
    return path


def commit(repo, name, date):
    (repo / name).write_bytes(b"x")
    git(repo, "add", name)
    git(
        repo,
        "commit",
        "-m",
        "fixture",
        env={"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date},
    )


def test_repository_state_clean_dirty_old_and_no_remote(tmp_path, inventory):
    """At Jan 3, default 24h cutoff is Jan 2. Hand counts:

    clean unborn: dirty=0, old=0; dirty unborn: one untracked => 1,0;
    old branch: Jan 1 commit => 0,1; recent/no remote: Jan 3 commit => 0,0.
    All four repositories are pruned from stray files, so total stray=0.
    """
    root = tmp_path / "tree"
    root.mkdir()
    clean = init_repo(root / "clean")
    dirty = init_repo(root / "dirty")
    (dirty / "untracked").touch()
    old = init_repo(root / "old")
    commit(old, "a", "2026-01-01T00:00:00Z")
    recent = init_repo(root / "recent")
    commit(recent, "a", "2026-01-03T00:00:00Z")
    result = inventory.build_manifest(config(root), clock=lambda: FIXED)
    states = {
        row["path"]: (row["dirty_count"], row["unpushed_old_count"])
        for row in result["repos"]
    }
    assert states == {"clean": (0, 0), "dirty": (1, 0), "old": (0, 1), "recent": (0, 0)}
    assert result["totals"]["count"] == 0
    assert clean.is_dir()


def test_remote_reachability_deduplicates_branches_and_rename(tmp_path, inventory):
    """Remote reaches commit A; local branches both reach B => only B is old.

    One staged rename is one porcelain record despite two NUL-separated paths.
    An untracked newline-containing filename adds one record: dirty=2, old=1.
    """
    repo = init_repo(tmp_path / "repo")
    commit(repo, "a", "2026-01-01T00:00:00Z")
    git(repo, "update-ref", "refs/remotes/example/trunk", "HEAD")
    commit(repo, "b", "2026-01-01T01:00:00Z")
    git(repo, "branch", "duplicate")
    git(repo, "mv", "a", "renamed\nfile")
    (repo / "untracked\nfile").touch()
    result = inventory.build_manifest(
        config(tmp_path, repos=["repo"]), clock=lambda: FIXED
    )
    assert result["repos"][0]["dirty_count"] == 2
    assert result["repos"][0]["unpushed_old_count"] == 1


def test_custom_age_boundary_and_detached_head(tmp_path, inventory):
    """At Jan 3, cutoff 48h is Jan 1: a commit exactly at cutoff is not older.

    At 47h cutoff, that same detached commit is older => 1 unique commit.
    """
    repo = init_repo(tmp_path / "repo")
    commit(repo, "a", "2026-01-01T00:00:00Z")
    git(repo, "checkout", "--detach")
    git(repo, "branch", "-D", "trunk")
    for hours, expected in [(48, 0), (47, 1)]:
        result = inventory.build_manifest(
            config(tmp_path, unpushed_hours=hours), clock=lambda: FIXED
        )
        assert result["repos"][0]["unpushed_old_count"] == expected


def test_git_environment_isolation_and_no_index_write(tmp_path, inventory, monkeypatch):
    """Caller repo stays dirty=1; scanned repo stays clean=0 and index unchanged."""
    caller = init_repo(tmp_path / "caller")
    target = init_repo(tmp_path / "target")
    commit(target, "tracked", "2026-01-01T00:00:00Z")
    (caller / "dirty").touch()
    before = (target / ".git/index").read_bytes()
    index_stamp = (target / ".git/index").stat().st_mtime_ns
    for key, value in {
        "GIT_DIR": str(caller / ".git"),
        "GIT_WORK_TREE": str(caller),
        "GIT_COMMON_DIR": str(caller / ".git"),
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "alias.status",
        "GIT_CONFIG_VALUE_0": "invalid",
    }.items():
        monkeypatch.setenv(key, value)
    result = inventory.build_manifest(config(target), clock=lambda: FIXED)
    assert result["repos"][0]["dirty_count"] == 0
    assert (target / ".git/index").read_bytes() == before
    assert (target / ".git/index").stat().st_mtime_ns == index_stamp


def test_git_failure_does_not_report_zero(tmp_path, inventory):
    """One invalid Git marker must cause an error, never false clean counters."""
    repo = tmp_path / "broken"
    repo.mkdir()
    (repo / ".git").write_text("invalid marker")
    with pytest.raises(ValueError, match="Git"):
        inventory.build_manifest(config(tmp_path), clock=lambda: FIXED)


def test_declared_ancestor_excludes_entire_root(tmp_path, inventory):
    """A scan root inside a declared repository has zero stray files, not one."""
    repo = init_repo(tmp_path / "repo")
    nested = repo / "subdir"
    nested.mkdir()
    (nested / "inside").touch()
    result = inventory.build_manifest(
        config(nested, repos=[str(repo)]), clock=lambda: FIXED
    )
    assert result["files"] == []
    assert len(result["repos"]) == 1


def test_follow_links_stays_in_root_and_prunes_cache_and_repo(tmp_path, inventory):
    """Only ordinary and its file alias count: 2 entries * 3 bytes = 6.

    External, broken, looping, cache-target and repository-target links exclude
    their files. A directory alias to ordinary's parent cannot duplicate walking.
    """
    root = tmp_path / "tree"
    root.mkdir()
    external = tmp_path / "external"
    external.write_bytes(b"external")
    (root / "ordinary").write_bytes(b"abc")
    (root / "alias").symlink_to(root / "ordinary")
    (root / "external").symlink_to(external)
    (root / "broken").symlink_to(root / "missing")
    (root / "cycle").symlink_to(root / "cycle")
    (root / "loop").symlink_to(root, target_is_directory=True)
    (root / "cache").mkdir()
    (root / "cache" / "hidden").write_bytes(b"hidden")
    (root / "cache-alias").symlink_to(root / "cache", target_is_directory=True)
    (root / "cache-file-alias").symlink_to(root / "cache/hidden")
    (root / "repo/.git").mkdir(parents=True)
    (root / "repo/hidden").write_bytes(b"hidden")
    (root / "repo-alias").symlink_to(root / "repo", target_is_directory=True)
    (root / "repo-file-alias").symlink_to(root / "repo/hidden")
    files, _ = inventory.scan(config(root, follow_symlinks=True))
    assert [row["path"] for row in files] == ["alias", "ordinary"]
    assert sum(row["size"] for row in files) == 6


@pytest.mark.parametrize(
    "hours", [-1, True, "24", float("nan"), float("inf"), 1e100, 10**400]
)
def test_invalid_age_rejected(tmp_path, inventory, hours):
    """Nonfinite, negative, nonnumeric or unrepresentable ages are not evidence."""
    with pytest.raises(ValueError, match="unpushed_hours"):
        inventory.build_manifest(
            config(tmp_path, unpushed_hours=hours), clock=lambda: FIXED
        )


@pytest.mark.parametrize(
    "table",
    [
        [],
        {},
        {"other": {}},
        {"script": []},
        {"script": {"extensions": ["py"]}},
        {"script": {"extensions": ".py"}},
        {"script": {"names": ["x", "X"]}},
        {"script": {"names": [1]}},
        {"script": {"typo": []}},
        {"script": {"names": ["a/b"]}},
    ],
)
def test_invalid_category_table_rejected(tmp_path, inventory, table):
    """Each invalid mapping is rejected rather than silently misclassifying files."""
    with pytest.raises((TypeError, ValueError)):
        inventory.build_manifest(
            config(tmp_path, categories=table), clock=lambda: FIXED
        )


def test_output_cannot_overwrite_configuration_alias(tmp_path, inventory):
    """The output hard link aliases the config: zero bytes may change."""
    root = tmp_path / "tree"
    root.mkdir()
    cfg = tmp_path / "cfg.json"
    payload = json.dumps(config(root))
    cfg.write_text(payload)
    alias = tmp_path / "alias.json"
    os.link(cfg, alias)
    assert inventory.main(["--config", str(cfg), "--out", str(alias)]) == 2
    assert cfg.read_text() == payload


def test_output_symlink_and_negative_threshold(tmp_path, inventory):
    """Invalid output or threshold returns 2 and preserves the target content."""
    root = tmp_path / "tree"
    root.mkdir()
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config(root)))
    target = tmp_path / "target"
    target.write_bytes(b"abc")
    out = tmp_path / "out"
    out.symlink_to(target)
    assert inventory.main(["--config", str(cfg), "--out", str(out)]) == 2
    assert (
        inventory.main(
            ["--config", str(cfg), "--out", str(target), "--fail-above", "-1"]
        )
        == 2
    )
    assert target.read_bytes() == b"abc"


def test_real_linked_worktree_counter(tmp_path, inventory):
    """Two clean repos share one old commit; per-repo old=1, total stray=0."""
    repo = init_repo(tmp_path / "repo")
    commit(repo, "tracked", "2026-01-01T00:00:00Z")
    worktree = tmp_path / "linked"
    git(repo, "worktree", "add", "--detach", str(worktree))
    assert (worktree / ".git").is_file()
    result = inventory.build_manifest(config(tmp_path), clock=lambda: FIXED)
    assert result["files"] == []
    assert [
        (row["dirty_count"], row["unpushed_old_count"]) for row in result["repos"]
    ] == [(0, 1), (0, 1)]


def test_symlink_root_loop_is_clear_cli_error(tmp_path, inventory, capsys):
    """An unresolvable root loop produces exit 2 with no path disclosure."""
    loop = tmp_path / "cycle"
    loop.symlink_to(loop)
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config(loop)))
    out = tmp_path / "out.json"
    assert inventory.main(["--config", str(cfg), "--out", str(out)]) == 2
    assert str(tmp_path) not in capsys.readouterr().err
    assert not out.exists()


def test_traversal_failure_preserves_previous_output(
    tmp_path, inventory, monkeypatch, capsys
):
    """Denied traversal cannot replace the previous manifest or print its path."""
    root = tmp_path / "tree"
    root.mkdir()
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config(root)))
    out = tmp_path / "out.json"
    out.write_bytes(b"previous")

    def deny(*args):
        raise PermissionError(str(root))

    monkeypatch.setattr(inventory.os, "scandir", deny)
    assert inventory.main(["--config", str(cfg), "--out", str(out)]) == 2
    assert out.read_bytes() == b"previous"
    assert str(root) not in capsys.readouterr().err


def test_repository_labels_are_sorted_with_external_roots(tmp_path, inventory):
    """Two empty repos: one external absolute label must precede 'inside'."""
    root = tmp_path / "a-root"
    root.mkdir()
    init_repo(root / "inside")
    external = init_repo(tmp_path / "z-repo")
    result = inventory.build_manifest(
        config(root, repos=["inside", str(external)]), clock=lambda: FIXED
    )
    assert [row["path"] for row in result["repos"]] == [str(external), "inside"]
