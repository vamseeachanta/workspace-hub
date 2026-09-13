"""Synthetic adapter boundaries and disposable Git observations; no live wiring."""
from copy import deepcopy
import builtins
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/governance"))
import consumer_event as adapter
import workflow_decision as decision

FIXTURES = Path(__file__).parent / "fixtures/consumer-adapter-events-v1.json"
REASONS = {"MAPPED_EVENT", "MALFORMED_EVENT", "UNSUPPORTED_EVENT",
           "INCOMPLETE_EFFECTS", "PATH_BINDING_MISMATCH", "MISSING_CONTEXT"}


def cases():
    return json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]


def fixture_case(name):
    return deepcopy(next(item for item in cases() if item["id"] == name))


def evaluate(case):
    result = adapter.normalize_event(case["raw_event"], case["context"])
    return {"adapter_result": result, "assessment_result":
            decision.assess(result["request"]) if result["mapping_status"] == "mapped" else None}


@pytest.mark.parametrize("case", cases(), ids=lambda c: c["id"])
def test_conjectural_fixture_contract(case):
    before = deepcopy(case)
    result = evaluate(case)
    assert result["adapter_result"] == case["adapter_result"]
    assert case["provenance"] == "conjectural"
    assert "capture_reference" not in case and "provider_version" not in case
    assert set(result["adapter_result"]["reason_codes"]) <= REASONS
    assert result["adapter_result"]["reason_codes"] == sorted(set(result["adapter_result"]["reason_codes"]))
    if "assessment_expected" in case:
        for field, expected in case["assessment_expected"].items():
            assert result["assessment_result"][field] == expected
    assert before == case
    assert len({entry["id"] for entry in cases()}) == len(cases())
    if result["adapter_result"]["mapping_status"] != "mapped":
        assert result["assessment_result"] is None


def test_provider_equivalence_and_reason_namespaces_are_separate():
    claude, codex = evaluate(fixture_case("claude-write")), evaluate(fixture_case("codex-write"))
    left, right = deepcopy(claude), deepcopy(codex)
    left["adapter_result"]["request"].pop("provider", None)
    right["adapter_result"]["request"].pop("provider", None)
    assert left == right
    assert set(claude) == {"adapter_result", "assessment_result"}
    assert len(claude["assessment_result"]) == 6
    assert claude["adapter_result"]["reason_codes"] == ["MAPPED_EVENT"]
    assert "UNVERIFIED_AUTHORITY" in claude["assessment_result"]["reason_codes"]
    assert "UNVERIFIED_AUTHORITY" not in claude["adapter_result"]["reason_codes"]


def test_pure_mapping_cannot_execute_or_open_locator(monkeypatch):
    sample = fixture_case("claude-write")
    raw = json.loads(sample["raw_event"])
    raw["evidence_reference"] = "https://invalid.example/credential-locator"
    raw = json.dumps(raw)
    original = deepcopy(sample["context"])
    def denied(*args, **kwargs):
        raise AssertionError("Pure mapping attempted external I/O")
    with monkeypatch.context() as patch:
        assert "assess" not in vars(adapter)
        for owner, names in [(builtins, ["open"]), (io, ["open"]), (Path, ["open", "resolve", "read_bytes", "write_bytes", "read_text", "write_text"]),
                             (subprocess, ["run", "Popen"]), (socket, ["socket", "create_connection"]),
                             (os, ["system", "open", "fdopen", "mkdir", "remove", "rename", "stat", "lstat"])]:
            for name in names:
                patch.setattr(owner, name, denied)
        result = adapter.normalize_event(raw, sample["context"])
    assert result["mapping_status"] == "mapped"
    assert original == sample["context"]


def test_inert_marker_or_handoff_reference_does_not_authenticate():
    item = fixture_case("claude-write")
    for reference in ["unrelated-issue-marker", "old-handoff", "review-APPROVE"]:
        item["context"]["authorization_reference"] = reference
        result = evaluate(item)["assessment_result"]
        assert result["authorization_assessment"] == "unverified-reference"
        assert result["action_boundary"] == "conditional-routine"


def child_env(tmp_path):
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "LOCALAPPDATA", "LANG"}
    env = {k: v for k, v in os.environ.items() if k.upper() in allowed}
    home = tmp_path / "child-home"
    home.mkdir(exist_ok=True)
    env.update(HOME=str(home), USERPROFILE=str(home), XDG_CONFIG_HOME=str(home),
               GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0")
    return env


def git(repo, env, *args):
    assert repo.resolve().is_relative_to(Path(env["HOME"]).resolve().parent)
    result = subprocess.run(["git", "-C", str(repo), *args], env=env,
                            capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


@pytest.fixture
def repository(tmp_path, monkeypatch):
    # Deliberately hostile inherited bindings are removed only from child env.
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "forbidden-git-dir"))
    monkeypatch.setenv("GIT_WORK_TREE", str(ROOT))
    env = child_env(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, env, "-c", "init.templateDir=", "init", "-q")
    for key, value in [("user.name", "Synthetic Fixture"), ("user.email", "fixture@example.invalid"),
                       ("commit.gpgSign", "false"), ("core.autocrlf", "false")]:
        git(repo, env, "config", key, value)
    (repo / "seed.txt").write_text("base\n", encoding="utf-8")
    git(repo, env, "add", "seed.txt")
    git(repo, env, "commit", "-q", "-m", "test: synthetic base")
    git_marker = ROOT / ".git"
    metadata = git_marker if git_marker.is_file() else git_marker / "config"
    frozen = [metadata, ROOT / ".claude/hooks/plan-approval-gate.sh",
              ROOT / "scripts/enforcement/require-plan-approval.sh"]
    before = {str(path): path.read_bytes() for path in frozen}
    yield repo, env
    assert before == {str(path): path.read_bytes() for path in frozen}
    assert os.environ["GIT_WORK_TREE"] == str(ROOT)
    assert not (tmp_path / "forbidden-git-dir").exists()


def test_working_index_and_branch_content_are_distinct(repository):
    repo, env = repository
    base = git(repo, env, "rev-parse", "HEAD")
    target = repo / "seed.txt"
    target.write_text("staged\n", encoding="utf-8")
    git(repo, env, "add", "seed.txt")
    target.write_text("working\n", encoding="utf-8")
    assert git(repo, env, "show", ":seed.txt") == "staged"
    assert target.read_text(encoding="utf-8") == "working\n"
    git(repo, env, "commit", "-q", "-m", "test: staged synthetic change")
    assert git(repo, env, "diff", "--cached", "--name-only") == ""
    assert git(repo, env, "diff", "--name-only", base, "HEAD") == "seed.txt"
    assert git(repo, env, "show", "HEAD:seed.txt") == "staged"


def test_legacy_clean_index_misses_nonempty_committed_branch_diff(repository):
    repo, env = repository
    base = git(repo, env, "rev-parse", "HEAD")
    (repo / "src").mkdir()
    (repo / "src/change.py").write_text("synthetic = 1\n", encoding="utf-8")
    git(repo, env, "add", "src/change.py")
    git(repo, env, "commit", "-q", "-m", "test: synthetic branch delta")
    assert git(repo, env, "diff", "--name-only", base, "HEAD") == "src/change.py"
    assert git(repo, env, "diff", "--cached", "--name-only") == ""
    script = copied_script(repo, "scripts/enforcement/require-plan-approval.sh")
    result = subprocess.run([bash_executable(), str(script), "--strict", "--require-issue", "3615"],
                            cwd=repo, env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "No implementation changes or low-risk files only" in result.stdout
    assert not (repo / ".planning").exists()


def test_rename_diff_exposes_both_endpoints(repository):
    repo, env = repository
    git(repo, env, "mv", "seed.txt", "renamed.txt")
    output = git(repo, env, "diff", "--cached", "--name-status", "-M")
    assert output.split("\t") == ["R100", "seed.txt", "renamed.txt"]


def test_effective_hooks_path_is_not_default_or_execution_evidence(repository):
    repo, env = repository
    default = repo / ".git/hooks/pre-commit"
    default.parent.mkdir(parents=True, exist_ok=True)
    default.write_text("Synthetic unexecuted hook\n", encoding="utf-8")
    before = default.read_bytes()
    git(repo, env, "config", "core.hooksPath", ".fixture-hooks")
    effective = git(repo, env, "rev-parse", "--git-path", "hooks/pre-commit")
    assert effective.replace("\\", "/") == ".fixture-hooks/pre-commit"
    assert not (repo / effective).exists()
    assert default.read_bytes() == before
    assert git(repo, env, "config", "--get", "core.hooksPath") == ".fixture-hooks"


def test_linked_worktree_has_git_file_and_shared_object_store(repository):
    repo, env = repository
    linked = repo.parent / "linked"
    git(repo, env, "worktree", "add", "--detach", str(linked), "HEAD")
    assert (linked / ".git").is_file()
    assert not (linked / ".git/hooks").exists()
    common = Path(git(linked, env, "rev-parse", "--git-common-dir")).resolve()
    assert common == (repo / ".git").resolve()
    assert git(linked, env, "show", "HEAD:seed.txt") == "base"


def test_lexical_mapping_does_not_establish_symlink_containment(tmp_path):
    root, outside = tmp_path / "owner", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    link = root / "link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.fail(f"UNAVAILABLE: real directory symlink capability: {exc}")
    assert not (link / "new.md").resolve().is_relative_to(root.resolve())
    item = fixture_case("claude-write")
    item["context"]["changed_paths"] = ["link/new.md"]
    event = json.loads(item["raw_event"])
    event["payload"]["path"] = "link/new.md"
    result = adapter.normalize_event(json.dumps(event), item["context"])
    assert result["mapping_status"] == "mapped"  # Lexical only, never containment.
    assert set(result) == {"mapping_status", "request", "reason_codes"}
    assert not (outside / "new.md").exists()
    event["payload"]["path"] = (link / "new.md").as_posix()
    assert adapter.normalize_event(json.dumps(event), item["context"])["reason_codes"] == ["PATH_BINDING_MISMATCH"]


def test_nonexistent_and_prefix_sibling_paths_need_no_filesystem_read(tmp_path):
    owner = tmp_path / "owner"
    sibling = tmp_path / "owner-sibling"
    item = fixture_case("claude-write")
    event = json.loads(item["raw_event"])
    for absolute in [(owner / "missing.md").as_posix(), (sibling / "file.md").as_posix()]:
        event["payload"]["path"] = absolute
        result = adapter.normalize_event(json.dumps(event), item["context"])
        assert result["request"] is None
        assert result["reason_codes"] == ["PATH_BINDING_MISMATCH"]
    assert not owner.exists() and not sibling.exists()


def test_windows_junction_resolution_is_only_harness_evidence(tmp_path):
    if os.name != "nt":
        pytest.skip("UNAVAILABLE: Windows junction observation requires Windows")
    owner, outside = tmp_path / "owner", tmp_path / "outside"
    owner.mkdir()
    outside.mkdir()
    junction = owner / "junction"
    result = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(outside)],
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, "UNAVAILABLE: Windows junction capability: " + result.stderr
    try:
        assert junction.is_junction()
        assert not (junction / "future.md").resolve().is_relative_to(owner.resolve())
        assert not (outside / "future.md").exists()
    finally:
        os.rmdir(junction)  # Removes the verified junction entry, never its target.
    assert outside.is_dir()


def bash_executable():
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Git/usr/bin/bash.exe"
    result = str(local) if local.is_file() else shutil.which("bash")
    assert result, "UNAVAILABLE: Bash required for legacy fixture observation"
    return result


def copied_script(repo, relative):
    target = repo / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / relative, target)
    assert target.resolve().is_relative_to(repo.resolve())
    assert hashlib.sha256(target.read_bytes()).digest() == hashlib.sha256((ROOT / relative).read_bytes()).digest()
    return target


def legacy_hook(repository, payload):
    repo, env = repository
    script = copied_script(repo, ".claude/hooks/plan-approval-gate.sh")
    local = dict(env, WORKSPACE_HUB=repo.as_posix(), SKIP_PLAN_APPROVAL_GATE="0",
                 DISABLE_ENFORCEMENT="0", FORCE_PLAN_GATE_STRICT="1")
    local["PATH"] = str(Path(bash_executable()).parent) + os.pathsep + local["PATH"]
    supplied = payload.get("tool_input", {}).get("file_path")
    if supplied:
        assert (repo / supplied).resolve().is_relative_to(repo.resolve())
    assert (repo / ".planning/plan-approved").resolve().is_relative_to(repo.resolve())
    capability = subprocess.run([bash_executable(), "-c", "command -v jq"], env=local,
                                capture_output=True, text=True, timeout=10)
    assert capability.returncode == 0, "UNAVAILABLE: jq required for actual legacy parsing"
    result = subprocess.run([bash_executable(), str(script)], input=json.dumps(payload),
                            cwd=repo, env=local, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    return result


def test_unrelated_old_marker_satisfies_legacy_but_not_authority(repository):
    repo, _ = repository
    payload = {"tool_name": "Write", "tool_input": {"file_path": "./src/module.py"}}
    assert json.loads(legacy_hook(repository, payload).stdout)["decision"] == "block"
    marker = repo / ".planning/plan-approved/999999.md"
    marker.parent.mkdir(parents=True)
    marker.write_text("Synthetic unrelated issue reference\n", encoding="utf-8")
    old = time.time() - 3600
    os.utime(marker, (old, old))
    assert legacy_hook(repository, payload).stdout == ""
    result = evaluate(fixture_case("protected-policy"))
    assert result["assessment_result"]["action_boundary"] == "approval-required"


def test_protected_governance_path_is_legacy_exempt(repository):
    repo, _ = repository
    payload = {"tool_name": "Write", "tool_input": {"file_path": "./docs/governance/change.md"}}
    assert legacy_hook(repository, payload).stdout == ""
    assert not (repo / ".planning").exists()
    assert evaluate(fixture_case("protected-policy"))["assessment_result"]["risk_class"] == "substantial"
