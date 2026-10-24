"""Synthetic examples for the contract in issue #4221.

All counts and byte totals below are independent hand calculations over literal
fixtures, not values obtained from the implementation under test.
"""

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/hygiene/plan_moves.py"


@pytest.fixture
def tool():
    spec = importlib.util.spec_from_file_location("plan_moves", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def sample(tmp_path):
    root = tmp_path / "tree"
    (root / "repos/alpha").mkdir(parents=True)
    (root / "repos/beta").mkdir(parents=True)
    (root / "loose").mkdir()
    (root / "loose/a.txt").write_bytes(b"abc")
    manifest = {
        "schema": 1,  # Issue #4221: inventory manifest version 1.
        "root": str(root),
        "repos": [
            {"path": "repos/alpha", "name": "alpha"},
            {"path": "repos/beta", "name": "beta"},
        ],
        "files": [
            {
                "path": "loose/a.txt",
                "size": 3,
                "mtime": "2026-01-01T00:00:00Z",
                "category": "work",
            },
        ],
    }
    config = {"rules": [{"match": "loose", "repo": "alpha", "dest": "docs"}]}
    return root, manifest, config


def test_first_match_wins(tool, sample):
    """Rule 0 precedes rule 1; docs/a.txt preserves the basename a.txt."""
    _, manifest, config = sample
    config["rules"].append({"match": "*.txt", "repo": "beta", "dest": "other"})
    entry = tool.build_plan(manifest, config)["entries"][0]
    assert (entry["repo"], entry["dest"], entry["reason"]) == (
        "alpha",
        "repos/alpha/docs/a.txt",
        0,
    )


def test_unmatched_and_default(tool, sample):
    """Without rules a.txt is unmatched; a default maps it to the repo root."""
    _, manifest, _ = sample
    assert (
        tool.build_plan(manifest, {"rules": []})["entries"][0]["status"] == "unmatched"
    )
    entry = tool.build_plan(manifest, {"rules": [], "default_repo": "beta"})["entries"][
        0
    ]
    assert entry["dest"] == "repos/beta/a.txt"
    assert entry["reason"] == "default_repo"


def test_ignore(tool, sample):
    """The sole input matches loose/*, leaving zero proposed entries."""
    _, manifest, config = sample
    config["ignore"] = ["loose/*"]
    plan = tool.build_plan(manifest, config)
    assert plan["entries"] == []
    assert plan["summary"]["ignored"] == 1


def test_two_sources_collide(tool, sample):
    """Both basenames are a.txt; both target docs/a.txt and must conflict."""
    root, manifest, config = sample
    (root / "other").mkdir()
    (root / "other/a.txt").write_bytes(b"abc")
    manifest["files"].append({**manifest["files"][0], "path": "other/a.txt"})
    config["rules"][0]["match"] = "*.txt"
    entries = tool.build_plan(manifest, config)["entries"]
    assert [entry["status"] for entry in entries] == ["conflict", "conflict"]


def test_existing_destination(tool, sample):
    """An existing docs/a.txt is never silently replaced."""
    root, manifest, config = sample
    (root / "repos/alpha/docs").mkdir()
    (root / "repos/alpha/docs/a.txt").write_bytes(b"keep")
    assert tool.build_plan(manifest, config)["entries"][0]["status"] == "conflict"


def test_prefix_boundary(tool, sample):
    """lo does not prefix a path component named loose."""
    _, manifest, config = sample
    config["rules"][0]["match"] = "lo"
    assert tool.build_plan(manifest, config)["entries"][0]["status"] == "unmatched"


@pytest.mark.parametrize(
    "bad",
    [
        "../escape",
        "/absolute",
        "a/../escape",
        "a\\b",
        ".git/config",
        ".GIT/config",
        "docs./file",
        "AUX",
        "nul.txt",
    ],
)
def test_unsafe_source_rejected(tool, sample, bad):
    """Traversal, absolute paths, nonportable separators and Git metadata fail closed."""
    _, manifest, config = sample
    manifest["files"][0]["path"] = bad
    with pytest.raises(ValueError):
        tool.build_plan(manifest, config)


def test_dry_run_tree_unchanged(tool, sample, tmp_path):
    """One file contains abc (3 bytes); only the external plan may change."""
    _, manifest, config = sample
    manifest_path, config_path = tmp_path / "m.json", tmp_path / "rules.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8", newline="\n")
    config_path.write_text(json.dumps(config), encoding="utf-8", newline="\n")
    out = tmp_path / "plan.json"

    def snapshot():
        return {
            str(p.relative_to(tmp_path)): (
                p.is_dir(),
                None if p.is_dir() else p.read_bytes(),
            )
            for p in tmp_path.rglob("*")
            if p != out
        }

    before = snapshot()
    assert (
        tool.main(
            [
                "--manifest",
                str(manifest_path),
                "--config",
                str(config_path),
                "--out",
                str(out),
            ]
        )
        == 0
    )
    assert snapshot() == before
    summary = json.loads(out.read_text(encoding="utf-8"))["summary"]
    assert summary["repos"] == {"alpha": {"count": 1, "bytes": 3}}
    assert summary["conflicts"] == summary["unmatched"] == 0


@pytest.fixture
def reviewed(tool, sample, tmp_path):
    root, manifest, config = sample
    plan = tmp_path / "plan.json"
    tool.write_plan(tool.build_plan(manifest, config), plan)
    return root, plan, tmp_path / "apply.jsonl", tool.digest(plan)


def events(log):
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


def test_apply_verified_copy_and_clock(tool, reviewed):
    """abc is copied unchanged before its original is removed; clock is literal."""
    root, plan, log, token = reviewed
    tool.apply_plan(plan, log, token, clock=lambda: "2026-01-01T00:00:00Z")
    assert not (root / "loose/a.txt").exists()
    assert (root / "repos/alpha/docs/a.txt").read_bytes() == b"abc"
    assert [e["result"] for e in events(log)] == ["copied", "done"]
    assert all(e["time"] == "2026-01-01T00:00:00Z" for e in events(log))
    assert events(log)[-1]["hash"] == hashlib.sha256(b"abc").hexdigest()


def test_destination_corruption_keeps_source(tool, reviewed, monkeypatch):
    """A faulty writer emits xyz instead of abc, same size but different hash."""
    root, plan, log, token = reviewed
    monkeypatch.setattr(tool, "copy_stream", lambda _src, dst: dst.write(b"xyz"))
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, token)
    assert (root / "loose/a.txt").read_bytes() == b"abc"
    assert events(log)[-1]["result"] == "error"
    assert "done" not in [e["result"] for e in events(log)]


def test_copy_write_error_keeps_source(tool, reviewed, monkeypatch):
    """A write error may leave a partial copy; the original abc must remain."""
    root, plan, log, token = reviewed

    def fail(_src, dst):
        dst.write(b"a")
        raise OSError("synthetic write error")

    monkeypatch.setattr(tool, "copy_stream", fail)
    with pytest.raises(OSError):
        tool.apply_plan(plan, log, token)
    assert (root / "loose/a.txt").read_bytes() == b"abc"


def test_interrupted_run_resumes(tool, reviewed, monkeypatch):
    """A stop after the durable copied event resumes without copying again."""
    root, plan, log, token = reviewed
    original = tool.remove_verified_source

    def interrupt(*_args):
        raise KeyboardInterrupt

    monkeypatch.setattr(tool, "remove_verified_source", interrupt)
    with pytest.raises(KeyboardInterrupt):
        tool.apply_plan(plan, log, token)
    assert events(log)[-1]["result"] == "copied"
    assert (root / "loose/a.txt").exists()
    monkeypatch.setattr(tool, "remove_verified_source", original)
    monkeypatch.setattr(tool, "copy_stream", lambda *_: pytest.fail("copy repeated"))
    tool.apply_plan(plan, log, token)
    assert not (root / "loose/a.txt").exists()
    assert events(log)[-1]["result"] == "done"
    before = log.read_bytes()
    tool.apply_plan(plan, log, token)
    assert log.read_bytes() == before


@pytest.mark.parametrize("last_result", ["copied", "done"])
def test_unterminated_log_refused_without_mutation(
    tool, sample, tmp_path, monkeypatch, last_result
):
    """Missing LF must refuse before changing either move or the receipt log."""
    root, manifest, config = sample
    (root / "loose/b.txt").write_bytes(b"xyz")
    manifest["files"].append({**manifest["files"][0], "path": "loose/b.txt"})
    plan, log = tmp_path / "plan.json", tmp_path / "apply.jsonl"
    tool.write_plan(tool.build_plan(manifest, config), plan)
    token = tool.digest(plan)
    append = tool.append_event

    def interrupt(log_path, event):
        append(log_path, event)
        if event["result"] == last_result:
            raise KeyboardInterrupt

    with monkeypatch.context() as patch:
        patch.setattr(tool, "append_event", interrupt)
        with pytest.raises(KeyboardInterrupt):
            tool.apply_plan(plan, log, token)
    assert events(log)[-1]["result"] == last_result
    raw = log.read_bytes()
    assert raw.endswith(b"\n")
    log.write_bytes(raw[:-1])

    def snapshot():
        return {
            path.relative_to(root).as_posix(): (
                path.stat().st_ino,
                path.read_bytes() if path.is_file() else None,
            )
            for path in root.rglob("*")
        }

    before = snapshot()
    with pytest.raises(tool.SafetyError, match="final newline"):
        tool.apply_plan(plan, log, token)
    assert log.read_bytes() == raw[:-1]
    assert snapshot() == before
    # After inspection, restoring exactly the missing LF permits resume and undo.
    log.write_bytes(raw)
    tool.apply_plan(plan, log, token)
    undo = tmp_path / "undo.json"
    tool.write_plan(tool.build_undo(log), undo)
    tool.apply_plan(undo, tmp_path / "undo.jsonl", tool.digest(undo))
    assert (root / "loose/a.txt").read_bytes() == b"abc"
    assert (root / "loose/b.txt").read_bytes() == b"xyz"
    assert not (root / "repos/alpha/docs/a.txt").exists()
    assert not (root / "repos/alpha/docs/b.txt").exists()


def test_append_event_refuses_unterminated_log(tool, tmp_path):
    """An append must preserve an existing incomplete record without extending it."""
    log = tmp_path / "apply.jsonl"
    raw = b'{"result":"copied"}'
    log.write_bytes(raw)
    with pytest.raises(tool.SafetyError, match="final newline"):
        tool.append_event(log, {"result": "done"})
    assert log.read_bytes() == raw


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (b"", []),
        (b"{}\r\n", [{}]),
        ('{"note":"\u2028"}\n'.encode("utf-8"), [{"note": "\u2028"}]),
    ],
)
def test_log_uses_lf_record_boundaries(tool, tmp_path, raw, expected):
    """Empty logs, CRLF and Unicode within JSON retain their record meaning."""
    log = tmp_path / "apply.jsonl"
    log.write_bytes(raw)
    assert tool.read_events(log) == expected


def test_interruption_after_source_removal_resumes(tool, reviewed, monkeypatch):
    """The copied receipt also covers a stop between unlink and done receipt."""
    root, plan, log, token = reviewed
    append = tool.append_event

    def stop(log_path, event):
        if event["result"] == "done":
            raise KeyboardInterrupt
        append(log_path, event)

    monkeypatch.setattr(tool, "append_event", stop)
    with pytest.raises(KeyboardInterrupt):
        tool.apply_plan(plan, log, token)
    assert not (root / "loose/a.txt").exists()
    monkeypatch.setattr(tool, "append_event", append)
    tool.apply_plan(plan, log, token)
    assert events(log)[-1]["result"] == "done"


def test_wrong_confirm_refused(tool, reviewed):
    """An arbitrary string cannot confirm the reviewed file bytes."""
    root, plan, log, _ = reviewed
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, "wrong")
    assert (root / "loose/a.txt").exists()
    assert not log.exists()


def test_conflict_refused(tool, sample, tmp_path):
    """Any conflict stops the entire apply before copies or log creation."""
    root, manifest, config = sample
    (root / "repos/alpha/docs").mkdir()
    target = root / "repos/alpha/docs/a.txt"
    target.write_bytes(b"keep")
    plan, log = tmp_path / "plan.json", tmp_path / "apply.jsonl"
    tool.write_plan(tool.build_plan(manifest, config), plan)
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, tool.digest(plan))
    assert target.read_bytes() == b"keep"
    assert not log.exists()


def test_stale_source_refused(tool, reviewed):
    """Replacing abc with xyz keeps size 3 but invalidates the reviewed digest."""
    root, plan, log, token = reviewed
    (root / "loose/a.txt").write_bytes(b"xyz")
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, token)
    assert (root / "loose/a.txt").read_bytes() == b"xyz"
    assert not (root / "repos/alpha/docs/a.txt").exists()


def test_racing_destination_never_overwritten(tool, reviewed):
    """A destination created after review is retained, even if content matches."""
    root, plan, log, token = reviewed
    target = root / "repos/alpha/docs/a.txt"
    target.parent.mkdir()
    target.write_bytes(b"abc")
    with pytest.raises((ValueError, FileExistsError)):
        tool.apply_plan(plan, log, token)
    assert (root / "loose/a.txt").exists()
    assert target.read_bytes() == b"abc"


def test_symlink_parent_refused(tool, reviewed, tmp_path):
    """Replacing docs with a symlink cannot redirect a copy outside root."""
    root, plan, log, token = reviewed
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "repos/alpha/docs").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, token)
    assert list(outside.iterdir()) == []
    assert (root / "loose/a.txt").exists()


@pytest.mark.parametrize("dangling", [False, True])
@pytest.mark.parametrize("location", ["root", "parent", "endpoint"])
def test_directory_reparse_point_refused(tool, sample, monkeypatch, location, dangling):
    """Directory reparse points must be refused even without a symlink flag."""
    from types import SimpleNamespace

    root, manifest, config = sample
    target = {"root": root, "parent": root.parent, "endpoint": root / "loose"}[location]
    original = Path.lstat

    def reparse_stat(path, *args, **kwargs):
        result = original(path, *args, **kwargs)
        if path == target:
            return SimpleNamespace(
                st_mode=result.st_mode,
                st_file_attributes=tool.stat.FILE_ATTRIBUTE_REPARSE_POINT,
            )
        return result

    if dangling:
        exists = Path.exists
        monkeypatch.setattr(
            Path, "exists", lambda path: False if path == target else exists(path)
        )
    monkeypatch.setattr(Path, "lstat", reparse_stat)
    with pytest.raises(tool.SafetyError):
        tool.build_plan(manifest, config)


def test_log_cannot_be_source(tool, reviewed):
    """An append-only log must never append JSON into the original abc."""
    root, plan, _, token = reviewed
    with pytest.raises(ValueError):
        tool.apply_plan(plan, root / "loose/a.txt", token)
    assert (root / "loose/a.txt").read_bytes() == b"abc"


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        env=clean_git_env(),
    ).stdout


def clean_git_env():
    import os

    return {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }


def test_git_add_is_explicit(tool, reviewed, monkeypatch):
    """Only docs/a.txt is staged; unrelated.txt remains untracked."""
    root, plan, log, token = reviewed
    repo = root / "repos/alpha"
    git(repo, "init", "--quiet")
    (repo / "unrelated.txt").write_bytes(b"keep")
    calls, original = [], tool.git_run

    def record(repository, args):
        calls.append(args)
        return original(repository, args)

    monkeypatch.setattr(tool, "git_run", record)
    tool.apply_plan(plan, log, token, git_add=True)
    assert git(repo, "diff", "--cached", "--name-only").decode().splitlines() == [
        "docs/a.txt"
    ]
    assert [args for args in calls if args[0] == "add"] == [["add", "--", "docs/a.txt"]]
    assert not any(args[0] in {"commit", "push"} for args in calls)
    assert events(log)[-1]["staged_paths"] == ["docs/a.txt"]


def test_lfs_stage_refused_before_move(tool, reviewed):
    """The filter=lfs rule covers a.txt, so neither move nor staging begins."""
    root, plan, log, token = reviewed
    repo = root / "repos/alpha"
    git(repo, "init", "--quiet")
    (repo / ".gitattributes").write_text(
        "*.txt filter=lfs\n", encoding="utf-8", newline="\n"
    )
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, token, git_add=True)
    assert (root / "loose/a.txt").exists()
    assert git(repo, "diff", "--cached", "--name-only") == b""


def test_git_off_by_default(tool, reviewed, monkeypatch):
    """Ordinary moves invoke no Git command, even without a .git directory."""
    _, plan, log, token = reviewed
    monkeypatch.setattr(tool, "git_run", lambda *_: pytest.fail("unexpected Git call"))
    tool.apply_plan(plan, log, token)


def test_undo_same_verified_protocol(tool, reviewed, tmp_path):
    """Moving abc forward then backward restores its bytes at loose/a.txt."""
    root, plan, log, token = reviewed
    tool.apply_plan(plan, log, token)
    undo = tmp_path / "undo.json"
    tool.write_plan(tool.build_undo(log), undo, (log,))
    tool.apply_plan(undo, tmp_path / "undo.jsonl", tool.digest(undo))
    assert (root / "loose/a.txt").read_bytes() == b"abc"
    assert not (root / "repos/alpha/docs/a.txt").exists()


def test_undo_cannot_overwrite_recreated_original(tool, reviewed, tmp_path):
    """A newly recreated original is retained when reverse copy is refused."""
    root, plan, log, token = reviewed
    tool.apply_plan(plan, log, token)
    (root / "loose/a.txt").write_bytes(b"new")
    undo = tmp_path / "undo.json"
    reverse = tool.build_undo(log)
    assert reverse["entries"][0]["status"] == "conflict"
    tool.write_plan(reverse, undo, (log,))
    with pytest.raises(ValueError):
        tool.apply_plan(undo, tmp_path / "undo.jsonl", tool.digest(undo))
    assert (root / "loose/a.txt").read_bytes() == b"new"
    assert (root / "repos/alpha/docs/a.txt").read_bytes() == b"abc"


def test_git_filename_wildcard_is_literal(tool, sample, tmp_path):
    """A filename a*.txt must not also stage the unrelated file ab.txt."""
    root, manifest, config = sample
    source = root / "loose/a*.txt"
    source.write_bytes(b"abc")
    manifest["files"][0]["path"] = "loose/a*.txt"
    repo = root / "repos/alpha"
    git(repo, "init", "--quiet")
    (repo / "docs").mkdir()
    (repo / "docs/ab.txt").write_bytes(b"keep")
    plan = tmp_path / "plan.json"
    tool.write_plan(tool.build_plan(manifest, config), plan)
    tool.apply_plan(plan, tmp_path / "apply.jsonl", tool.digest(plan), git_add=True)
    assert git(repo, "diff", "--cached", "--name-only").decode().splitlines() == [
        "docs/a*.txt"
    ]


def test_log_hardlink_refused(tool, sample, tmp_path):
    """An empty source hardlinked as the log must not gain JSON contents."""
    root, manifest, config = sample
    source = root / "loose/a.txt"
    source.write_bytes(b"")
    manifest["files"][0]["size"] = 0
    plan, log = tmp_path / "plan.json", tmp_path / "apply.jsonl"
    tool.write_plan(tool.build_plan(manifest, config), plan)
    log.hardlink_to(source)
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, tool.digest(plan))
    assert source.read_bytes() == b""


def test_apply_cli_reports_lfs(tool, reviewed, capsys):
    """A staging refusal must identify LFS, without exposing file contents."""
    root, plan, log, token = reviewed
    repo = root / "repos/alpha"
    git(repo, "init", "--quiet")
    (repo / ".gitattributes").write_text(
        "*.txt filter=lfs\n", encoding="utf-8", newline="\n"
    )
    assert (
        tool.main(
            ["--apply", str(plan), "--log", str(log), "--confirm", token, "--git-add"]
        )
        == 1
    )
    assert "LFS" in capsys.readouterr().err


def test_later_source_changes_during_copy(tool, reviewed, monkeypatch):
    """Changing abc to xyz after copying must preserve the changed source."""
    root, plan, log, token = reviewed
    original = tool.copy_stream

    def change(src, dst):
        original(src, dst)
        (root / "loose/a.txt").write_bytes(b"xyz")

    monkeypatch.setattr(tool, "copy_stream", change)
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, token)
    assert (root / "loose/a.txt").read_bytes() == b"xyz"


def test_staging_failure_resumes(tool, reviewed, monkeypatch):
    """A failed add leaves a done move; retry stages exactly the moved file."""
    root, plan, log, token = reviewed
    repo = root / "repos/alpha"
    git(repo, "init", "--quiet")
    original = tool.git_run

    def fail_add(repository, args):
        if args[0] == "add":
            raise subprocess.CalledProcessError(1, "git")
        return original(repository, args)

    monkeypatch.setattr(tool, "git_run", fail_add)
    with pytest.raises(subprocess.CalledProcessError):
        tool.apply_plan(plan, log, token, git_add=True)
    assert not (root / "loose/a.txt").exists()
    assert "done" in [e["result"] for e in events(log)]
    monkeypatch.setattr(tool, "git_run", original)
    tool.apply_plan(plan, log, token, git_add=True)
    assert git(repo, "diff", "--cached", "--name-only").decode().splitlines() == [
        "docs/a.txt"
    ]


def test_plan_whitespace_change_requires_new_confirmation(tool, reviewed):
    """Even semantically identical JSON has different reviewed bytes after a newline."""
    root, plan, log, token = reviewed
    plan.write_bytes(plan.read_bytes() + b"\n")
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, token)
    assert (root / "loose/a.txt").exists()


def test_other_plan_log_refused(tool, reviewed):
    """Receipts from a different plan digest cannot authorize a resume."""
    root, plan, log, token = reviewed
    tool.apply_plan(plan, log, token)
    plan.write_bytes(plan.read_bytes() + b"\n")
    before = log.read_bytes()
    with pytest.raises(ValueError):
        tool.apply_plan(plan, log, tool.digest(plan))
    assert log.read_bytes() == before
    assert (root / "repos/alpha/docs/a.txt").read_bytes() == b"abc"


def test_documented_example_end_to_end(tmp_path):
    """Execute the documented shell block verbatim: abc moves out and back.

    The literal abc contains three ASCII bytes; after undo the sole stray file
    again contains those bytes and the repository destination is absent.
    """
    document = SCRIPT.with_name("PLAN_MOVES.md").read_text(encoding="utf-8")
    commands = document.split("```sh\n", 1)[1].split("\n```", 1)[0]
    env = clean_git_env()
    env["EXAMPLE_DIR"] = str(tmp_path / "example")
    env["PATH"] = str(Path(sys.executable).parent) + ":" + env["PATH"]
    result = subprocess.run(
        ["bash", "-c", commands],
        cwd=SCRIPT.parents[2],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    root = tmp_path / "example/tree"
    assert (root / "loose/a.txt").read_bytes() == b"abc"
    assert not (root / "repos/notes/docs/a.txt").exists()
    for name in ("apply.log.jsonl", "undo.log.jsonl"):
        log = tmp_path / "example" / name
        assert [e["result"] for e in events(log)] == ["copied", "done"]


def test_ignore_is_a_glob_not_a_prefix(tool, sample):
    """The literal glob loose matches no file named loose/a.txt."""
    _, manifest, config = sample
    config["ignore"] = ["loose"]
    assert len(tool.build_plan(manifest, config)["entries"]) == 1


def test_destination_parent_is_a_file(tool, sample):
    """A regular file named docs cannot contain the proposed docs/a.txt."""
    root, manifest, config = sample
    (root / "repos/alpha/docs").write_bytes(b"keep")
    assert tool.build_plan(manifest, config)["entries"][0]["status"] == "conflict"


def test_destination_is_another_destination_parent(tool, sample):
    """docs/a.txt cannot be both a copied file and the directory of b.txt."""
    root, manifest, config = sample
    (root / "loose/b.txt").write_bytes(b"abc")
    manifest["files"].append({**manifest["files"][0], "path": "loose/b.txt"})
    config["rules"].insert(
        0, {"match": "loose/b.txt", "repo": "alpha", "dest": "docs/a.txt"}
    )
    assert [e["status"] for e in tool.build_plan(manifest, config)["entries"]] == [
        "conflict",
        "conflict",
    ]


def test_inherited_git_binding_does_not_redirect(tool, reviewed, tmp_path, monkeypatch):
    """A caller Git binding cannot send staged files to another repository."""
    root, plan, log, token = reviewed
    repo, unrelated = root / "repos/alpha", tmp_path / "unrelated"
    unrelated.mkdir()
    git(repo, "init", "--quiet")
    git(unrelated, "init", "--quiet")
    monkeypatch.setenv("GIT_DIR", str(unrelated / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(unrelated))
    tool.apply_plan(plan, log, token, git_add=True)
    assert git(unrelated, "diff", "--cached", "--name-only") == b""
    assert git(repo, "diff", "--cached", "--name-only").decode().splitlines() == [
        "docs/a.txt"
    ]


def test_multistep_resume_skips_completed_first_move(
    tool, sample, tmp_path, monkeypatch
):
    """After a.txt finishes, interruption at b.txt must not repeat a.txt."""
    root, manifest, config = sample
    (root / "loose/b.txt").write_bytes(b"def")
    manifest["files"].append({**manifest["files"][0], "path": "loose/b.txt"})
    plan, log = tmp_path / "plan.json", tmp_path / "apply.jsonl"
    tool.write_plan(tool.build_plan(manifest, config), plan)
    original = tool.remove_verified_source

    def interrupt(root_path, entry):
        if entry["source"] == "loose/b.txt":
            raise KeyboardInterrupt
        original(root_path, entry)

    monkeypatch.setattr(tool, "remove_verified_source", interrupt)
    with pytest.raises(KeyboardInterrupt):
        tool.apply_plan(plan, log, tool.digest(plan))
    assert (root / "repos/alpha/docs/a.txt").read_bytes() == b"abc"
    assert not (root / "loose/a.txt").exists()
    assert (root / "loose/b.txt").read_bytes() == b"def"
    monkeypatch.setattr(tool, "remove_verified_source", original)
    monkeypatch.setattr(
        tool, "copy_stream", lambda *_: pytest.fail("completed copy repeated")
    )
    tool.apply_plan(plan, log, tool.digest(plan))
    assert not (root / "loose/b.txt").exists()
    assert (root / "repos/alpha/docs/b.txt").read_bytes() == b"def"
    assert [e["source"] for e in events(log) if e["result"] == "done"] == [
        "loose/a.txt",
        "loose/b.txt",
    ]
