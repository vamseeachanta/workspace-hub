"""Footprint reporting is observational; fixtures never contact a remote."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts/workstations/repo_footprint.py"
CHECKER = ROOT / "scripts/workstations/check-tier1-repo-baseline.py"


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location("repo_footprint", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(path, *args):
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-C", str(path), *args],
        check=True, capture_output=True, text=True,
    )


def repo(root, name="core"):
    path = root / name
    path.mkdir()
    git(path, "init", "-q")
    (path / "source with spaces.py").write_text("pass\n")
    return path


def registry(root, required=None):
    return {"machines": {"fixture": {
        "hostname": "not-the-current-host", "tier1_repo_root": str(root),
        "repos": ["core", "optional"],
        "tier1_baseline": {"required": required or ["core"]},
    }}}


def report(mod, root, **kwargs):
    return mod.measure_machine(registry(root), "fixture", **kwargs)


def test_selection_categories_and_budget_are_explicit(mod, tmp_path):
    core = repo(tmp_path)
    repo(tmp_path, "optional")
    for directory, size in [(".venv", 11), ("data", 13), ("docs", 17)]:
        (core / directory).mkdir()
        (core / directory / "payload").write_bytes(b"x" * size)
    result = report(mod, tmp_path, budget_bytes=1)
    assert result["selected_repositories"] == ["core"]
    assert result["selection_source"] == "machines.fixture.tier1_baseline.required"
    assert result["excluded_repositories"] == ["optional"]
    sizes = result["totals"]
    assert sizes["checkout"]["logical_bytes"] == (core / "source with spaces.py").stat().st_size + 17
    assert sizes["dependencies"]["logical_bytes"] == 11
    assert sizes["heavy_data_candidates"]["logical_bytes"] == 13
    assert sizes["git"]["logical_bytes"] > 0
    assert result["budget"]["status"] == ("indeterminate" if result["total"]["allocated_bytes"] is None else "exceeded")
    assert result["budget"]["scope"] == "all_selected_local_bytes_including_git_and_dependencies"
    assert result["configured_hostname"] == "not-the-current-host"
    assert result["observed_hostname"]
    assert result["runtime_readiness"] == "not_verified"


def test_missing_selected_repo_never_passes_budget(mod, tmp_path):
    repo(tmp_path)
    result = mod.measure_machine(registry(tmp_path, ["core", "missing"]), "fixture", budget_bytes=10**12)
    assert result["unavailable_repositories"] == ["missing"]
    assert result["budget"]["status"] == "indeterminate"
    assert result["complete"] is False
    assert result["total"]["allocated_bytes"] is None
    assert result["total"]["logical_bytes"] is None
    assert result["total"]["known_logical_bytes"] > 0


@pytest.mark.parametrize("name", ["../escape", "/absolute", "a/b", "a\\b", "C:escape", "..", "bad\nname"])
def test_registry_names_cannot_escape_root(mod, tmp_path, name):
    with pytest.raises(ValueError):
        mod.measure_machine(registry(tmp_path, [name]), "fixture")


def test_registered_selection_does_not_claim_a_core_profile(mod, tmp_path):
    repo(tmp_path)
    data = registry(tmp_path)
    del data["machines"]["fixture"]["tier1_baseline"]
    data["machines"]["fixture"]["repos"] = ["core"]
    result = mod.measure_machine(data, "fixture", selection="registered")
    assert result["selection_source"] == "machines.fixture.repos"
    assert result["core_profile_verified"] is False
    with pytest.raises(ValueError):
        mod.measure_machine(data, "fixture")


def test_unavailable_allocation_does_not_fall_back_to_logical(mod, tmp_path, monkeypatch):
    repo(tmp_path)
    monkeypatch.setattr(mod, "_file_allocation", lambda path, value: None)
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result["total"]["allocated_bytes"] is None
    assert result["total"]["logical_bytes"] > 0
    assert result["budget"]["status"] == "indeterminate"


def test_allocation_uses_blocks_and_reports_unsupported(mod):
    assert mod.allocated_bytes(SimpleNamespace(st_blocks=3)) == 1536
    assert mod.allocated_bytes(SimpleNamespace(st_size=2000)) is None


def test_windows_reparse_directory_is_an_excluded_redirect(mod):
    junction = SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
    ordinary = SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0)
    assert mod.is_redirect(junction)
    assert not mod.is_redirect(ordinary)


def test_symlinks_and_nested_repos_are_excluded_explicitly(mod, tmp_path):
    core = repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "private").write_bytes(b"x" * 123456)
    (core / "linked-data").symlink_to(outside, target_is_directory=True)
    repo(core, "nested")
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result["budget"]["status"] == "indeterminate"
    codes = {e["code"] for e in result["issues"]}
    assert {"symlink_target_excluded", "nested_repository_excluded"} <= codes
    assert result["totals"]["checkout"]["known_logical_bytes"] < 123456


def test_symlink_selected_repo_is_unavailable(mod, tmp_path):
    target = repo(tmp_path, "target")
    (tmp_path / "core").symlink_to(target, target_is_directory=True)
    result = report(mod, tmp_path)
    assert result["unavailable_repositories"] == ["core"]
    assert result["complete"] is False


def test_symlink_ancestor_of_root_is_not_followed(mod, tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    root = real / "repos"
    root.mkdir()
    repo(root)
    alias = tmp_path / "alias"
    alias.symlink_to(real, target_is_directory=True)
    result = report(mod, alias / "repos", budget_bytes=10**12)
    assert result["complete"] is False
    assert result["total"]["files"] == 0


def test_symlink_ancestor_of_git_metadata_is_not_followed(mod, tmp_path):
    real = repo(tmp_path, "real")
    alias = tmp_path / "alias"
    alias.symlink_to(real, target_is_directory=True)
    core = tmp_path / "core"
    core.mkdir()
    (core / ".git").write_text(f"gitdir: {alias / '.git'}\n")
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result["complete"] is False
    assert result["unavailable_repositories"] == ["core"]


def test_git_objects_lfs_recovery_and_other_are_separate(mod, tmp_path):
    core = repo(tmp_path)
    for name, size in [("objects", 7), ("lfs", 11), ("recovery-backups", 13)]:
        directory = core / ".git" / name
        directory.mkdir(exist_ok=True)
        (directory / "synthetic-payload").write_bytes(b"x" * size)
    result = report(mod, tmp_path)
    parts = result["git_breakdown"]
    assert parts["objects"]["logical_bytes"] == 7
    assert parts["lfs"]["logical_bytes"] == 11
    assert parts["recovery_backups"]["logical_bytes"] == 13
    assert sum(v["logical_bytes"] for v in parts.values()) == result["totals"]["git"]["logical_bytes"]


def test_shared_git_store_counted_once(mod, tmp_path):
    core = repo(tmp_path)
    git(core, "add", ".")
    git(core, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
    git(core, "worktree", "add", "--detach", str(tmp_path / "linked"), "HEAD")
    both = mod.measure_machine(registry(tmp_path, ["core", "linked"]), "fixture")
    first = report(mod, tmp_path)
    assert len(both["git_stores"]) == 1
    assert both["git_stores"][0]["bytes"] == first["git_stores"][0]["bytes"]
    assert both["totals"]["git"]["logical_bytes"] == (
        first["totals"]["git"]["logical_bytes"] + (tmp_path / "linked/.git").stat().st_size
    )
    assert both["git_stores"][0]["repositories"] == ["core", "linked"]
    assert both["totals"]["checkout"]["logical_bytes"] == sum((tmp_path / name / "source with spaces.py").stat().st_size for name in ["core", "linked"])


def test_external_alternates_prevent_complete_claim(mod, tmp_path):
    core = repo(tmp_path)
    (core / ".git/objects/info/alternates").write_text("/not/scanned/object/store\n")
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result["budget"]["status"] == "indeterminate"
    assert any(e["code"] == "external_git_alternates" for e in result["issues"])


def test_stat_failure_is_explicit_and_budget_indeterminate(mod, tmp_path, monkeypatch):
    core = repo(tmp_path)
    real_stat = mod.os.lstat
    def fail(path, *args, **kwargs):
        if Path(path) == core / "source with spaces.py":
            raise PermissionError("fixture denied")
        return real_stat(path, *args, **kwargs)
    monkeypatch.setattr(mod.os, "lstat", fail)
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result["budget"]["status"] == "indeterminate"
    assert any(e["code"] == "scan_error" for e in result["issues"])


def test_inaccessible_root_is_an_unverifiable_receipt(mod, tmp_path, monkeypatch):
    real_stat = mod.os.lstat
    def fail(path, *args, **kwargs):
        if Path(path) == tmp_path:
            raise PermissionError("fixture denied")
        return real_stat(path, *args, **kwargs)
    monkeypatch.setattr(mod.os, "lstat", fail)
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result["budget"]["status"] == "indeterminate"
    assert any(e["code"] == "root_unavailable" for e in result["issues"])


@pytest.mark.parametrize("failure", ["unavailable", "timeout", "nonzero", "malformed", "missing-directory", "not-directory"])
def test_failed_git_inspection_reports_unknown_not_zero(mod, tmp_path, monkeypatch, failure):
    core = repo(tmp_path)
    def fail(cmd, **kwargs):
        assert "rev-parse" in cmd
        assert kwargs["env"]["GIT_NO_LAZY_FETCH"] == "1"
        if failure == "unavailable":
            raise FileNotFoundError("git unavailable")
        if failure == "timeout":
            raise subprocess.TimeoutExpired(cmd, 15)
        if failure == "nonzero":
            return subprocess.CompletedProcess(cmd, 128, "", "metadata unavailable")
        if failure == "malformed":
            return subprocess.CompletedProcess(cmd, 0, "not-absolute\n", "")
        path = core / ("missing" if failure == "missing-directory" else "source with spaces.py")
        return subprocess.CompletedProcess(cmd, 0, f"{path}\n{path}\n", "")
    monkeypatch.setattr(mod.subprocess, "run", fail)
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result["complete"] is False
    assert result["budget"]["status"] == "indeterminate"
    assert result["total"]["logical_bytes"] is None
    assert result["total"]["allocated_bytes"] is None
    assert result["totals"]["git"]["logical_bytes"] is None


@pytest.mark.parametrize("relative", ["", "core", "core/.git", "core/.git/objects"])
def test_failed_directory_enumeration_keeps_only_observed_lower_bounds(mod, tmp_path, monkeypatch, relative):
    repo(tmp_path)
    denied = tmp_path / relative
    real_scan = mod.os.scandir
    def fail(path):
        if Path(path) == denied:
            raise PermissionError("cannot enumerate")
        return real_scan(path)
    monkeypatch.setattr(mod.os, "scandir", fail)
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result["complete"] is False
    assert result["budget"]["status"] == "indeterminate"
    assert result["total"]["logical_bytes"] is None
    assert result["total"]["allocated_bytes"] is None
    assert result["total"]["known_allocated_bytes"] >= 0


def test_promisor_config_scan_only_uses_local_rev_parse_and_preserves_files(mod, tmp_path, monkeypatch):
    core = repo(tmp_path)
    git(core, "config", "remote.origin.promisor", "true")
    git(core, "config", "remote.origin.partialclonefilter", "blob:none")
    git(core, "config", "core.sparseCheckout", "true")
    before = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in core.rglob("*") if p.is_file()}
    real_run = mod.subprocess.run
    calls = []
    def probe(cmd, **kwargs):
        calls.append(cmd)
        assert "rev-parse" in cmd
        assert kwargs["env"]["GIT_NO_LAZY_FETCH"] == "1"
        assert kwargs["env"]["GIT_OPTIONAL_LOCKS"] == "0"
        assert "GIT_DIR" not in kwargs["env"]
        assert kwargs["timeout"] <= 30
        return real_run(cmd, **kwargs)
    monkeypatch.setattr(mod.subprocess, "run", probe)
    monkeypatch.setenv("GIT_DIR", "/bad/inherited/location")
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert calls
    assert result["budget"]["status"] == ("indeterminate" if result["total"]["allocated_bytes"] is None else "within_budget")
    after = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in core.rglob("*") if p.is_file()}
    assert before == after


def test_real_sparse_checkout_is_not_expanded(mod, tmp_path):
    core = repo(tmp_path)
    (core / "data").mkdir()
    (core / "data" / "held-evidence").write_bytes(b"x" * 5000)
    (core / "src").mkdir()
    (core / "src" / "module.py").write_text("pass\n")
    git(core, "add", ".")
    git(core, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
    git(core, "sparse-checkout", "set", "--cone", "src")
    assert not (core / "data").exists()
    before = (core / ".git/index").read_bytes()
    result = report(mod, tmp_path)
    assert result["totals"]["heavy_data_candidates"]["files"] == 0
    assert not (core / "data").exists()
    assert (core / ".git/index").read_bytes() == before


def test_cli_footprint_is_separate_from_placement_and_rejects_invalid_modes(tmp_path):
    repo(tmp_path)
    data = registry(tmp_path)
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(data))
    command = [sys.executable, str(CHECKER), "--registry", str(path), "--machine", "fixture", "--footprint-only"]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode in {0, 1}, result.stderr
    receipt = json.loads(result.stdout)
    assert result.returncode == (1 if receipt["budget"]["status"] in {"indeterminate", "exceeded"} else 0)
    assert "dispatchable" not in receipt
    assert receipt["selected_repositories"] == ["core"]
    for extra in [["--budget-bytes", "0"], ["--format", "html"], ["--budget-bytes", "-1"]]:
        assert subprocess.run(command + extra, capture_output=True).returncode == 2


def test_declared_membership_and_missing_optional_are_explicit(mod, tmp_path):
    repo(tmp_path)
    result = report(mod, tmp_path)
    assert result["registered_repositories"] == ["core", "optional"]
    assert result["registered_not_selected"] == ["optional"]
    assert result["registered_not_observed"] == ["optional"]
    assert result["selected_not_registered"] == []


def test_required_members_not_in_machine_repos_remain_visible(mod, tmp_path):
    repo(tmp_path)
    data = registry(tmp_path, ["core", "required-gap"])
    result = mod.measure_machine(data, "fixture")
    assert result["selected_not_registered"] == ["required-gap"]
    assert result["unavailable_repositories"] == ["required-gap"]
    assert result["budget"]["status"] == "indeterminate"

@pytest.mark.parametrize("invalid", [None, "core", ["../bad"], [42]])
def test_malformed_declared_membership_is_rejected(mod, tmp_path, invalid):
    data = registry(tmp_path)
    data["machines"]["fixture"]["repos"] = invalid
    with pytest.raises(ValueError):
        mod.measure_machine(data, "fixture")


def test_direct_footprint_cli_creates_no_import_bytecode(tmp_path):
    repo(tmp_path)
    data = registry(tmp_path)
    registry_path = tmp_path / 'registry.yaml'
    registry_path.write_text(json.dumps(data))
    helpers = tmp_path / 'checker-probe'
    helpers.mkdir()
    for original in [CHECKER, HELPER]:
        shutil.copyfile(original, helpers / original.name)
    # A cold local dependency also must not acquire bytecode during observation.
    (helpers / 'yaml.py').write_text('import json\ndef safe_load(text): return json.loads(text)\n')
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONDONTWRITEBYTECODE'}
    result = subprocess.run([sys.executable, str(helpers / CHECKER.name), '--registry',
        str(registry_path), '--machine', 'fixture', '--footprint-only'],
        env=env, capture_output=True, text=True)
    assert result.returncode in {0, 1}, result.stderr
    assert json.loads(result.stdout)['selected_repositories'] == ['core']
    assert not list(helpers.rglob('__pycache__'))

def test_native_windows_failure_keeps_budget_unknown(mod, tmp_path, monkeypatch):
    repo(tmp_path)
    monkeypatch.setattr(mod, '_WINDOWS', True)
    def fail(path, value): raise OSError('denied')
    monkeypatch.setattr(mod, '_windows_allocation', fail)
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result['budget']['status'] == 'indeterminate'
    assert result['total']['allocated_bytes'] is None
    assert any(i['code'] == 'allocation_unavailable' for i in result['issues'])


def test_changed_file_is_not_counted_as_stable(mod, tmp_path, monkeypatch):
    target = repo(tmp_path) / 'source with spaces.py'
    original = mod._file_allocation
    def change(path, value):
        result = original(path, value)
        if path == target: path.write_text('changed after metadata\n')
        return result
    monkeypatch.setattr(mod, '_file_allocation', change)
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result['budget']['status'] == 'indeterminate'
    assert any(i['code'] == 'file_changed_during_scan' for i in result['issues'])


def test_external_environment_is_explicit_and_counted_once(mod, tmp_path):
    core = repo(tmp_path)
    env = tmp_path / 'shared-python'; env.mkdir()
    (env / 'package.py').write_bytes(b'x' * 19)
    (core / '.venv').mkdir(); (core / '.venv' / 'local.py').write_bytes(b'x' * 7)
    result = report(mod, tmp_path, environment_paths=[env, env, core / '.venv'])
    assert result['totals']['dependencies']['known_logical_bytes'] == 26
    assert result['environment_accounting']['unlisted_external_environments'] == 'excluded'
    assert len(result['environment_accounting']['explicit_paths']) == 2
    assert result['environment_accounting']['inside_selected_roots'] == 'included'


def test_missing_explicit_environment_blocks_budget(mod, tmp_path):
    repo(tmp_path)
    result = report(mod, tmp_path, environment_paths=[tmp_path / 'missing-env'], budget_bytes=10**12)
    assert result['budget']['status'] == 'indeterminate'
    assert result['total']['logical_bytes'] is None
    assert any(i['code'] == 'environment_unavailable' for i in result['issues'])


def test_relative_environment_rejected(mod, tmp_path):
    repo(tmp_path)
    with pytest.raises(ValueError, match='absolute'):
        report(mod, tmp_path, environment_paths=[Path('relative-env')])


def test_explicit_environment_cli_requires_footprint_mode(mod, tmp_path):
    core = repo(tmp_path); config = tmp_path / 'registry.yml'
    config.write_text(yaml.safe_dump(registry(tmp_path)))
    result = subprocess.run([sys.executable, '-B', str(CHECKER), '--registry', str(config), '--machine', 'fixture', '--footprint-environment', str(core)], capture_output=True, text=True)
    assert result.returncode == 2
    assert 'requires --footprint-only' in result.stderr


@pytest.mark.skipif(os.name != 'nt', reason='Windows native metadata fixture')
def test_windows_native_rounding_hardlink_sparse_compression_redirect(mod, tmp_path):
    root = tmp_path / 'native'; root.mkdir()
    ordinary = root / 'ordinary'; ordinary.write_bytes(b'x' * 1048577)
    os.link(ordinary, root / 'alias')
    sparse = root / 'sparse'; sparse.touch()
    subprocess.run(['fsutil', 'sparse', 'setflag', str(sparse)], check=True, capture_output=True)
    with sparse.open('r+b') as handle:
        handle.write(b'a'); handle.seek(64 * 1024 * 1024 - 1); handle.write(b'z'); handle.flush(); os.fsync(handle.fileno())
    compressed = root / 'compressed'; compressed.write_bytes(b'c' * 1048576)
    subprocess.run(['compact', '/C', '/I', str(compressed)], check=True, capture_output=True)
    target = tmp_path / 'outside'; target.mkdir(); (target / 'excluded').write_bytes(b'j' * 9999)
    subprocess.run(['cmd', '/c', 'mklink', '/J', str(root / 'redirect'), str(target)], check=True, capture_output=True)
    expected = {p.name: mod._windows_allocation(p, os.lstat(p)) for p in [ordinary, sparse, compressed]}
    assert expected['ordinary'] >= ordinary.stat().st_size
    ranges = subprocess.run(['fsutil', 'file', 'queryallocranges', 'offset=0', 'length=67108864', str(sparse)], capture_output=True, text=True, check=True)
    import re
    assert expected['sparse'] == sum(int(x, 16) for x in re.findall(r'Length: 0x([0-9a-fA-F]+)', ranges.stdout))
    assert 0 < expected['compressed'] < compressed.stat().st_size
    scanner = mod._Scanner(); buckets = scanner.scan(root)
    assert scanner.hardlink_aliases == 1
    assert buckets['checkout']['known_allocated_bytes'] == sum(expected.values())
    assert any(i['code'] == 'symlink_target_excluded' for i in scanner.issues)

def test_posix_allocation_keeps_blocks_without_native_calls(mod, tmp_path, monkeypatch):
    monkeypatch.setattr(mod, '_WINDOWS', False)
    monkeypatch.setattr(mod, '_windows_allocation', lambda *args: pytest.fail('native API used on POSIX'))
    assert mod._file_allocation(tmp_path / 'not-opened', SimpleNamespace(st_blocks=7)) == 3584


def test_redirected_environment_blocks_budget_without_following(mod, tmp_path):
    repo(tmp_path)
    target = tmp_path / 'target'; target.mkdir(); (target / 'private').write_bytes(b'x' * 13)
    alias = tmp_path / 'alias'
    if os.name == 'nt':
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(alias), str(target)], check=True, capture_output=True)
    else:
        alias.symlink_to(target, target_is_directory=True)
    result = report(mod, tmp_path, environment_paths=[alias], budget_bytes=10**12)
    assert result['budget']['status'] == 'indeterminate'
    assert not result['environment_accounting']['explicit_measurements']
    assert any(i['code'] == 'environment_unavailable' for i in result['issues'])


def test_directory_mutation_is_incomplete(mod, tmp_path, monkeypatch):
    core = repo(tmp_path)
    original = mod._Scanner.file
    changed = False
    def mutate(self, path, value, bucket):
        nonlocal changed
        result = original(self, path, value, bucket)
        if path.parent == core and not changed:
            (core / 'late-file').write_bytes(b'late'); changed = True
        return result
    monkeypatch.setattr(mod._Scanner, 'file', mutate)
    result = report(mod, tmp_path, budget_bytes=10**12)
    assert result['budget']['status'] == 'indeterminate'
    assert any(i['code'] == 'directory_changed_during_scan' for i in result['issues'])
