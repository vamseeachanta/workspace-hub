"""Report-only layout checks against isolated repositories."""
import os
import json
import ctypes
from types import SimpleNamespace
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
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    template = tmp_path / "git-template"
    template.mkdir()
    monkeypatch.setenv("GIT_TEMPLATE_DIR", str(template))
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
        "origins": {}, "repositories": {},
    }))
    private = tmp_path / "private.json"
    private.write_text(json.dumps({
        "hosts": {"fixture": {"w": str(workspace), "aliases": [], "extra_roots": [],
                              "excluded_parents": [], "hostnames": ["hidden-name"]}},
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


PUBLIC_REPOSITORIES = {
    "aceengineer-website", "assethold", "assetutilities", "digitalmodel",
    "raw-to-knowledge-playbook", "workspace-hub", "worldenergydata", "worldenergydata-wiki",
}


def test_public_baseline_contains_only_public_repositories():
    config = json.loads((SCRIPT.parents[2] / "config/workstations/work-layout.yaml").read_text())
    assert set(config) == {"version", "source", "origins", "repositories"}
    assert set(config["origins"]) == PUBLIC_REPOSITORIES
    assert set(config["repositories"]) == PUBLIC_REPOSITORIES


def test_private_host_fields_and_names_merge(layout, tmp_path):
    check, workspace, _, _ = layout
    config = {"hosts": {"fixture": {"hostnames": ["one"], "w": "old"}}}
    extra = {"w": str(workspace), "aliases": [str(tmp_path / "alias")],
             "extra_roots": [str(tmp_path / "extra")], "hostnames": ["one", "two"],
             "excluded_parents": [str(tmp_path / "excluded")]}
    check["merge_private"](config, {"hosts": {"fixture": extra}})
    assert config["hosts"]["fixture"] == extra


@pytest.mark.parametrize("section", ["origins", "repositories", "hosts", "root", "host-entry"])
def test_malformed_private_layout_is_reported(layout, tmp_path, monkeypatch, capsys, section):
    check, workspace, _, _ = layout
    public = tmp_path / "public.json"
    public.write_text(json.dumps({
        "hosts": {"fixture": {"w": str(workspace), "aliases": [], "extra_roots": []}},
    }))
    private = tmp_path / "private.json"
    value = [] if section == "root" else (
        {"hosts": {"fixture": []}} if section == "host-entry" else {section: [1]})
    private.write_text(json.dumps(value))
    main = check["main"]
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setitem(main.__globals__, "volume_inventory",
                        lambda: ([tmp_path], {tmp_path: "ext4"}, []))
    assert main(["--host", "fixture", "--config", str(public),
                 "--private-config", str(private), "--json"]) == 1
    rows = json.loads(capsys.readouterr().out)["findings"]
    assert any(row["reason"].startswith("missing private layout") for row in rows)


def test_invalid_private_json(layout, tmp_path, capsys):
    check, _, _, _ = layout
    public = tmp_path / "public.json"
    public.write_text("{}")
    private = tmp_path / "private.json"
    private.write_text("{")
    assert check["main"](["--host", "fixture", "--config", str(public),
                          "--private-config", str(private), "--json"]) == 1
    assert any(row["reason"].startswith("missing private layout")
               for row in json.loads(capsys.readouterr().out)["findings"])


def test_canonical_clone_on_network_filesystem(layout):
    check, workspace, repo, _ = layout
    findings = check["workspace_children"](workspace, lambda path: "nfs4")
    assert [(row["reason"], row["observed"]) for row in findings] == [
        ("filesystem nfs4", str(repo))
    ]


def test_configured_excluded_parents(layout, tmp_path):
    check, workspace, _, _ = layout
    excluded = tmp_path / "data-disk"
    extra = excluded / "other" / "ws-extra"
    extra.mkdir(parents=True)
    scan = check["scan_roots"]
    assert any(row["observed"] == str(extra)
               for row in scan([tmp_path], tmp_path, workspace, [], [], {}))
    assert not scan([tmp_path, extra], tmp_path, workspace, [], [], {}, [excluded])
    assert not check["_excluded"](workspace, tmp_path, workspace, [workspace.parent])


def test_configured_exclusions_from_private_file(layout, tmp_path, monkeypatch, capsys):
    check, workspace, _, _ = layout
    extra = tmp_path / "data-disk" / "other" / "ws-extra"
    extra.mkdir(parents=True)
    public = tmp_path / "public.json"
    public.write_text("{}")
    private = tmp_path / "private.json"
    private.write_text(json.dumps({"origins": {"demo": "github.com/example/demo"},
                                 "hosts": {"fixture": {
        "w": str(workspace), "aliases": [], "extra_roots": [],
        "excluded_parents": [str(extra.parents[1])],
    }}}))
    main = check["main"]
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setitem(main.__globals__, "volume_inventory",
                        lambda: ([tmp_path], {tmp_path: "ext4"}, []))
    assert main(["--host", "fixture", "--config", str(public),
                 "--private-config", str(private), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["findings"] == []


def test_alias_mismatch_and_unexpected_link(layout, tmp_path):
    check, workspace, _, _ = layout
    alias = tmp_path / "alias"
    linked = tmp_path / "linked"
    for link, target in ((alias, tmp_path), (linked, workspace)):
        if os.name == "nt":
            subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                           check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            link.symlink_to(target, target_is_directory=True)
    rows = check["scan_roots"]([linked], tmp_path, workspace, [alias], [], {})
    assert {(row["reason"], row["observed"]) for row in rows} == {
        ("alias target mismatch", str(alias)), ("unexpected linked root", str(linked))
    }


def test_foreign_scan_root(layout, tmp_path):
    check, workspace, _, _ = layout
    rows = check["scan_roots"]([], tmp_path, workspace, [], [], {tmp_path: "nfs4"})
    assert [row["reason"] for row in rows] == ["foreign scan root"]


def test_scan_preserves_tree_and_git_metadata(layout, tmp_path):
    check, workspace, repo, git = layout
    git("worktree", "add", "--detach", str(workspace / "_wt" / "inside"))
    def snapshot():
        return {str(p.relative_to(tmp_path)): (p.lstat().st_mode, p.lstat().st_mtime_ns,
                p.read_bytes() if p.is_file() else None) for p in tmp_path.rglob("*")}
    before = snapshot()
    assert not check["workspace_children"](workspace, lambda path: "ext4")
    assert not check["repository"](repo, {"allowed": [".gitignore"]}, False)
    assert not check["scan_roots"]([tmp_path], tmp_path, workspace, [], [], {})
    assert snapshot() == before


def test_linux_mountinfo_parsing(tmp_path, monkeypatch):
    check = runpy.run_path(str(SCRIPT))
    monkeypatch.setitem(check["volume_inventory"].__globals__, "os", SimpleNamespace(name="posix"))
    volume = tmp_path / "local disk"
    volume.mkdir()
    network = tmp_path / "network"
    network.mkdir()
    file_mount = tmp_path / "file"
    file_mount.touch()
    encoded = str(volume).replace(" ", r"\040")
    text = (f"1 0 8:1 / {encoded} rw - ext4 /dev/disk rw\n"
            f"2 0 0:2 / {network} rw - nfs4 server:/export rw\n"
            f"3 0 8:1 / {file_mount} rw - ext4 /dev/disk rw\n")
    original = Path.read_text
    monkeypatch.setattr(Path, "read_text", lambda p, *a, **kw:
                        text if p == Path("/proc/self/mountinfo") else original(p, *a, **kw))
    roots, mounts, unavailable = check["volume_inventory"]()
    assert roots == [volume]
    assert mounts == {volume: "ext4", network: "nfs4", file_mount: "ext4"}
    assert unavailable == []


def test_linux_no_local_mount_roots(tmp_path, monkeypatch):
    check = runpy.run_path(str(SCRIPT))
    monkeypatch.setitem(check["volume_inventory"].__globals__, "os", SimpleNamespace(name="posix"))
    monkeypatch.setattr(Path, "read_text", lambda p: "")
    with pytest.raises(OSError, match="no local filesystem roots"):
        check["volume_inventory"]()


def test_windows_volume_enumeration(tmp_path, monkeypatch):
    check = runpy.run_path(str(SCRIPT))
    from ctypes import wintypes

    class Call:
        def __init__(self, fn):
            self.fn = fn
        def __call__(self, *args):
            return self.fn(*args)

    state = {"index": 0, "error": 0, "closed": [], "sizes": []}
    good, bad, remote = (str(tmp_path / n) for n in ("good", "bad", "remote"))
    volumes = [good, bad, remote]
    def first(buffer, size):
        buffer.value = volumes[0]
        return 1
    def next_volume(handle, buffer, size):
        state["index"] += 1
        if state["index"] == len(volumes):
            state["error"] = 18
            return 0
        buffer.value = volumes[state["index"]]
        return 1
    def paths(guid, buffer, size, required):
        state["sizes"].append(size)
        if size == 256 and guid == good:
            ctypes.cast(required, ctypes.POINTER(wintypes.DWORD))[0] = 512
            state["error"] = 234
            return 0
        buffer.value = guid
        return 1
    def information(name, label, label_size, serial, max_component, flags, kind, size):
        kind.value = "NTFS"
        return int(name != bad)
    api = SimpleNamespace(
        FindFirstVolumeW=Call(first), FindNextVolumeW=Call(next_volume),
        FindVolumeClose=Call(lambda handle: state["closed"].append(handle)),
        GetDriveTypeW=lambda guid: 4 if guid == remote else 3,
        GetVolumePathNamesForVolumeNameW=paths, GetVolumeInformationW=information,
    )
    monkeypatch.setattr(ctypes, "WinDLL", lambda *a, **kw: api, raising=False)
    monkeypatch.setattr(ctypes, "get_last_error", lambda: state["error"], raising=False)
    roots, mounts, unavailable = check["_windows_volumes"]()
    assert roots == [Path(good)]
    assert mounts == {Path(good): "ntfs", Path(bad): "unknown"}
    assert unavailable == [bad]
    assert state["sizes"] == [256, 512, 256]
    assert state["closed"] == [1]
