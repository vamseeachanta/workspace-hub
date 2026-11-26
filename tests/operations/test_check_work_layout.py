"""Report-only layout checks against isolated repositories."""
import os
import runpy
import subprocess
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/operations/check-work-layout.py"


@pytest.fixture
def layout(tmp_path, monkeypatch):
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key)
    check = runpy.run_path(str(SCRIPT))
    workspace = tmp_path / "ws"
    repo = workspace / "demo"
    repo.mkdir(parents=True)
    for name in ("_scratch", "_pm", "_wt"):
        (workspace / name).mkdir()
    def git(*args):
        subprocess.run(
            ["git", "-C", str(repo), *args], check=True, capture_output=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    git("init")
    git("remote", "add", "origin", "git@github.com:example/demo.git")
    (repo / ".gitignore").write_text("ignored\n")
    git("add", ".gitignore")
    git("-c", "user.name=Fixture", "-c", "user.email=a@example.invalid",
        "commit", "-m", "fixture")
    return check, workspace, repo, git


def test_repository(layout):
    check, _, repo, _ = layout
    policy = {"allowed": [".gitignore"], "core": []}
    (repo / "ignored").touch()
    assert not check["repository"](repo, policy, False)
    assert check["repository"](repo, policy, True)
    (repo / "unexpected").touch()
    assert any(f["observed"] == str(repo / "unexpected")
               for f in check["repository"](repo, policy, False))


def test_worktrees(layout, tmp_path):
    check, workspace, repo, git = layout
    outside = tmp_path / "outside"
    inside = workspace / "_wt" / "inside"
    git("worktree", "add", "--detach", str(outside))
    git("worktree", "add", "--detach", str(inside))
    findings = check["workspace_children"](workspace, lambda p: "fuseblk" if p == inside else "ext4")
    assert {(f["reason"], f["observed"]) for f in findings} == {
        ("worktree outside _wt", str(outside)), ("filesystem fuseblk", str(inside))
    }


def test_alias_and_depth(layout, tmp_path):
    check, workspace, _, _ = layout
    alias = tmp_path / "ws-alias"
    if os.name == "nt":
        subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(alias), str(workspace)],
                       check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        alias.symlink_to(workspace, target_is_directory=True)
    extra = tmp_path / "one" / "two" / "ws-extra"
    extra.mkdir(parents=True)
    (extra / "ws-too-deep").mkdir()
    (tmp_path / "backups" / "ws-mirror").mkdir(parents=True)
    findings = check["scan_roots"]([tmp_path], tmp_path, workspace, [alias], [], {})
    assert [f["observed"] for f in findings] == [str(extra)]


def test_partial_volume_evidence_keeps_other_findings(layout, tmp_path, monkeypatch, capsys):
    import json

    check, workspace, repo, _ = layout
    (workspace / "loose.txt").touch()
    missing = tmp_path / "unreadable-volume"
    policy = {
        "hosts": {"fixture": {"w": str(workspace), "aliases": [], "extra_roots": []}},
        "repositories": {"demo": {"allowed": [".gitignore"], "core": []}},
    }
    config = tmp_path / "policy.yaml"
    config.write_text(json.dumps(policy))
    main = check["main"]
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setitem(main.__globals__, "volume_inventory", lambda: (
        [tmp_path], {tmp_path: "ntfs", missing: "unknown"}, [str(missing)]
    ))
    assert main(["--host", "fixture", "--config", str(config), "--repo", str(repo),
                 "--json"]) == 1
    findings = json.loads(capsys.readouterr().out)["findings"]
    assert {row["observed"] for row in findings} == {str(missing), str(workspace / "loose.txt")}


def test_same_basename_different_origin(layout):
    check, workspace, repo, _ = layout
    expected = {"demo": "github.com/approved/demo"}
    findings = check["workspace_children"](workspace, lambda p: "ntfs", expected)
    assert [(f["reason"], f["observed"]) for f in findings] == [
        ("origin identity mismatch", str(repo))
    ]


def test_clean_and_unknown_host(layout, tmp_path, monkeypatch, capsys):
    import json

    check, workspace, repo, git = layout
    git("worktree", "add", "--detach", str(workspace / "_wt" / "wt-review"))
    config = tmp_path / "policy.yaml"
    config.write_text(json.dumps({
        "hosts": {"fixture": {"w": str(workspace), "aliases": [], "extra_roots": []}},
        "origins": {"demo": "github.com/example/demo"},
        "repositories": {"demo": {"allowed": [".gitignore"], "core": []}},
    }))
    main = check["main"]
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setitem(main.__globals__, "volume_inventory",
                        lambda: ([tmp_path], {tmp_path: "ntfs"}, []))
    args = ["--config", str(config), "--repo", str(repo), "--json"]
    assert main(["--host", "fixture", *args]) == 0
    assert json.loads(capsys.readouterr().out)["findings"] == []
    assert main(["--host", "unknown", *args]) == 1
    assert "missing host evidence" in capsys.readouterr().out


def test_private_layout_merges(layout, tmp_path, monkeypatch, capsys):
    import json

    check, workspace, repo, _ = layout
    public = tmp_path / "public.yaml"
    public.write_text(json.dumps({
        "hosts": {"fixture": {"w": str(workspace), "aliases": [], "extra_roots": [],
                              "hostnames": []}},
        "origins": {}, "repositories": {},
    }))
    private = tmp_path / "private.json"
    private.write_text(json.dumps({
        "hosts": {"fixture": {"hostnames": ["hidden-name"]}},
        "origins": {"demo": "github.com/example/demo"},
        "repositories": {"demo": {"allowed": [".gitignore"], "core": []}},
    }))
    main = check["main"]
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setitem(main.__globals__, "volume_inventory",
                        lambda: ([tmp_path], {tmp_path: "ntfs"}, []))
    monkeypatch.delenv("WORK_LAYOUT_PRIVATE", raising=False)
    args = ["--host", "hidden-name", "--config", str(public), "--repo", str(repo), "--json"]
    assert main(args) == 1  # without the private file the host and repository are unknown
    capsys.readouterr()
    assert main([*args, "--private-config", str(private)]) == 0
    assert json.loads(capsys.readouterr().out)["findings"] == []
    monkeypatch.setenv("WORK_LAYOUT_PRIVATE", str(private))
    assert main(args) == 0
    capsys.readouterr()
    missing = tmp_path / "absent.json"
    assert main([*args, "--private-config", str(missing)]) == 1
    assert "private layout" in capsys.readouterr().out
