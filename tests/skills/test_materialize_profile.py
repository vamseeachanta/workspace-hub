"""Synthetic six-payload materialization contracts; no native/user settings."""
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/skills"))
PAYLOADS = ["data/ecosystem-data-sources/SKILL.md", "data/drive-file-search/SKILL.md",
            "research/wiki-context/SKILL.md", "coordination/pre-completion-cleanup-audit/SKILL.md",
            "data/drive-file-search/references/context-extraction.md",
            "coordination/pre-completion-cleanup-audit/references/user-facing-scratch-artifacts.md"]


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


@pytest.fixture
def setup(tmp_path):
    source, target = tmp_path / "source", tmp_path / "target"
    source.mkdir(); target.mkdir()
    (tmp_path / "transactions").mkdir()
    subprocess.run(["git", "init", str(source)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(source), "-c", "user.name=Synthetic", "-c",
                    "user.email=synthetic@example.test", "commit", "--allow-empty", "-m", "fixture"],
                   check=True, capture_output=True)
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    entries = []
    for relative in PAYLOADS:
        name = relative.split("/")[1]
        raw = (f"---\nname: {name}\n---\nSynthetic UTF-8: caf\u00e9\n" if relative.endswith("SKILL.md")
               else "Reference\n").encode()
        write(source / ".claude/skills" / relative, raw)
        entries.append({"path": ".claude/skills/" + relative, "sha256": hashlib.sha256(raw).hexdigest()})
    profile = {"schema_version": 1, "name": "foundation", "canonical_source": ".claude/skills",
               "activation": {"skills": entries[:4], "references": entries[4:]}, "adapters": {
                   "repository_installation": {"mode": "family-preserving-project",
                   "provider_roots": {"claude": ".claude/skills", "codex": ".agents/skills"}}}}
    profile_path = source / "config/skills/profiles/foundation.yaml"
    write(profile_path, yaml.safe_dump(profile).encode())
    return dict(source=source, target=target, revision=revision, profile=profile_path,
                transaction=tmp_path / "transactions/one", data=profile)


def module():
    return importlib.import_module("materialize_profile")


def report(s):
    return module().report(s["source"], s["revision"], s["profile"], s["target"], "codex", s["transaction"])


def apply(s, manifest):
    return module().apply_report(manifest, s["source"], s["target"], s["transaction"])


def files(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_report_no_writes_deterministic_and_six_mappings(setup):
    before = files(setup["source"].parent)
    a = report(setup)
    assert a == report(setup) and len(a["entries"]) == 6
    assert files(setup["source"].parent) == before
    assert not setup["transaction"].exists()


def test_apply_preserves_unrelated_and_is_idempotent(setup):
    write(setup["target"] / ".agents/skills/unrelated/SKILL.md", b"---\nname: unrelated\n---\n")
    m = report(setup)
    result = apply(setup, m)
    assert result["status"] == "complete"
    for relative in PAYLOADS:
        assert (setup["target"] / ".agents/skills" / relative).read_bytes() == (
            setup["source"] / ".claude/skills" / relative).read_bytes()
    before = files(setup["source"].parent)
    assert apply(setup, m)["status"] == "noop"
    assert files(setup["source"].parent) == before


def test_same_checkout_disjoint_subtrees_allowed(setup):
    setup["target"] = setup["source"]
    assert len(report(setup)["entries"]) == 6


def test_preimage_drift_rejects_without_writes(setup):
    m = report(setup)
    path = setup["target"] / ".agents/skills/research/wiki-context/SKILL.md"
    write(path, b"later writer")
    with pytest.raises(ValueError):
        apply(setup, m)
    assert path.read_bytes() == b"later writer" and not setup["transaction"].exists()


def test_absent_manifest_cannot_rebind_target(setup):
    m = report(setup)
    other = setup["target"].parent / "other"; other.mkdir()
    with pytest.raises(ValueError):
        module().apply_report(m, setup["source"], other, setup["transaction"])


@pytest.mark.parametrize("case", ["digest", "prefix", "mode", "normalization", "duplicate"])
def test_bad_profile_fails_without_writes(setup, case):
    d = setup["data"]
    if case == "digest": d["activation"]["skills"][0]["sha256"] = "0" * 64
    if case == "prefix": d["activation"]["skills"][0]["path"] = "../escape/SKILL.md"
    if case == "mode": d["adapters"]["repository_installation"]["mode"] = "flat"
    if case == "normalization": d["activation"]["skills"][0]["sha256_normalization"] = "automatic"
    raw = yaml.safe_dump(d).encode()
    if case == "duplicate": raw += b"schema_version: 1\n"
    setup["profile"].write_bytes(raw)
    with pytest.raises(ValueError): report(setup)
    assert not setup["transaction"].exists()


@pytest.mark.parametrize("relative,raw", [("_archive/old/SKILL.md", b"---\nname: wiki-context\n---\n"),
    ("old/wiki-context/SKILL.md", b"malformed")])
def test_archive_and_malformed_basename_collisions(setup, relative, raw):
    write(setup["target"] / ".agents/skills" / relative, raw)
    with pytest.raises(ValueError): report(setup)


def test_reference_closure_rejects_new_required_reference(setup):
    entry = setup["data"]["activation"]["skills"][1]
    path = setup["source"] / entry["path"]
    path.write_bytes(path.read_bytes() + b"Read `references/mock-envelope.json`.\n")
    entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    setup["profile"].write_text(yaml.safe_dump(setup["data"]), encoding="utf-8")
    with pytest.raises(ValueError): report(setup)


def test_source_drift_after_report_blocks(setup):
    m = report(setup)
    path = setup["source"] / setup["data"]["activation"]["skills"][0]["path"]
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError): apply(setup, m)


def test_rollback_restores_old_and_removes_owned_files(setup):
    path = setup["target"] / ".agents/skills/research/wiki-context/SKILL.md"
    write(path, b"---\nname: wiki-context\n---\nold")
    receipt = apply(setup, report(setup))
    module().rollback(receipt, setup["source"], setup["target"], setup["transaction"])
    assert path.read_bytes().endswith(b"old")
    assert not (setup["target"] / ".agents/skills/data/drive-file-search/SKILL.md").exists()


def test_rollback_preserves_later_writer(setup):
    receipt = apply(setup, report(setup))
    path = setup["target"] / ".agents/skills/research/wiki-context/SKILL.md"
    path.write_bytes(b"concurrent edit")
    with pytest.raises(ValueError): module().rollback(receipt, setup["source"], setup["target"], setup["transaction"])
    assert path.read_bytes() == b"concurrent edit"


@pytest.mark.parametrize("variant", ["bom", "crlf"])
def test_source_bytes_are_preserved(setup, variant):
    entry = setup["data"]["activation"]["skills"][0]; path = setup["source"] / entry["path"]
    raw = path.read_bytes()
    raw = b"\xef\xbb\xbf" + raw if variant == "bom" else raw.replace(b"\n", b"\r\n")
    path.write_bytes(raw)
    entry["sha256"] = hashlib.sha256(raw.replace(b"\r\n", b"\n") if variant == "crlf" else raw).hexdigest()
    if variant == "crlf": entry["sha256_normalization"] = "crlf-to-lf"
    setup["profile"].write_text(yaml.safe_dump(setup["data"]), encoding="utf-8")
    apply(setup, report(setup))
    assert (setup["target"] / ".agents/skills" / PAYLOADS[0]).read_bytes() == raw


@pytest.mark.parametrize("field,value", [("adapters", []), ("activation", "bad"),
                                       ("skills", {}), ("entry", []), ("mode", [])])
def test_nested_profile_types_reject_structurally(setup, field, value):
    d = setup["data"]
    if field in {"adapters", "activation"}: d[field] = value
    elif field == "skills": d["activation"]["skills"] = value
    elif field == "entry": d["activation"]["skills"][0] = value
    else: d["adapters"]["repository_installation"] = value
    setup["profile"].write_text(yaml.safe_dump(d), encoding="utf-8")
    with pytest.raises(ValueError): report(setup)


def test_swapped_skill_reference_groups_rejected(setup):
    d = setup["data"]["activation"]
    d["skills"], d["references"] = d["references"], d["skills"]
    setup["profile"].write_text(yaml.safe_dump(setup["data"]), encoding="utf-8")
    with pytest.raises(ValueError): report(setup)


def test_empty_selected_basename_is_collision(setup):
    (setup["target"] / ".agents/skills/_archive/wiki-context").mkdir(parents=True)
    with pytest.raises(ValueError): report(setup)


def cli_args(setup):
    return [sys.executable, "-B", str(Path(module().__file__)), "--source-root", str(setup["source"]),
            "--target-root", str(setup["target"]), "--transaction-dir", str(setup["transaction"]),
            "--source-revision", setup["revision"], "--profile", str(setup["profile"])]


@pytest.mark.parametrize("extra", [[], ["--dry-run"]])
def test_cli_report_json_zero_write(setup, extra):
    before = files(setup["source"].parent)
    completed = subprocess.run(cli_args(setup) + extra, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert len(json.loads(completed.stdout)["entries"]) == 6
    assert files(setup["source"].parent) == before


def test_cli_validation_error_is_nonzero_json(setup):
    setup["profile"].write_bytes(b"schema_version: wrong")
    completed = subprocess.run(cli_args(setup), capture_output=True, text=True)
    assert completed.returncode == 1 and json.loads(completed.stdout)["status"] == "error"
    assert not setup["transaction"].exists()


def test_claude_separate_fixture_uses_same_six_bytes(setup):
    m = module().report(setup["source"], setup["revision"], setup["profile"], setup["target"],
                        "claude", setup["transaction"])
    apply(setup, m)
    assert all((setup["target"] / ".claude/skills" / p).read_bytes() == (
        setup["source"] / ".claude/skills" / p).read_bytes() for p in PAYLOADS)


def test_reference_markdown_and_inline_positive_closure(setup):
    for index, reference, markup in [(1, "context-extraction.md", "`references/{} `"),
        (3, "user-facing-scratch-artifacts.md", "[read](references/{})")]:
        entry = setup["data"]["activation"]["skills"][index]
        path = setup["source"] / entry["path"]
        path.write_bytes(path.read_bytes() + markup.format(reference).encode())
        entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    setup["profile"].write_text(yaml.safe_dump(setup["data"]), encoding="utf-8")
    assert len(report(setup)["entries"]) == 6


def test_report_ignores_inherited_git_repository(setup, monkeypatch):
    other = setup["target"]
    subprocess.run(["git", "init", str(other)], check=True, capture_output=True)
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(other))
    assert report(setup)["source_revision"] == setup["revision"]


def test_report_rejects_source_subdirectory(setup):
    import shutil
    nested = setup["source"] / "nested"
    shutil.copytree(setup["source"] / ".claude", nested / ".claude")
    shutil.copytree(setup["source"] / "config", nested / "config")
    setup["source"] = nested
    setup["profile"] = nested / "config/skills/profiles/foundation.yaml"
    with pytest.raises(ValueError, match="top.level"):
        report(setup)


def test_target_index_cannot_be_redirected(setup, monkeypatch):
    target = setup["target"]
    subprocess.run(["git", "init", str(target)], check=True, capture_output=True)
    blob = subprocess.check_output(["git", "-C", str(target), "hash-object", "-w", "--stdin"],
                                   input=b"elsewhere").decode().strip()
    subprocess.run(["git", "-C", str(target), "update-index", "--add", "--cacheinfo",
                    f"120000,{blob},.agents/skills/unrelated"], check=True, capture_output=True)
    monkeypatch.setenv("GIT_INDEX_FILE", str(setup["source"] / ".git/index"))
    with pytest.raises(ValueError, match="indexed symlink"):
        report(setup)


def test_git_environment_is_subprocess_local(monkeypatch):
    import os
    schema = importlib.import_module("materialize_profile_schema")
    for name in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY", "GIT_INDEX_FILE",
                 "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0",
                 "GIT_CONFIG_VALUE_0", "GIT_WORK_TREE"):
        monkeypatch.setenv(name, "untrusted")
    monkeypatch.setenv("FOUNDATION_TEST_KEEP", "ordinary")
    before = dict(os.environ)
    cleaned = schema.git_environment()
    assert dict(os.environ) == before
    assert cleaned["FOUNDATION_TEST_KEEP"] == "ordinary"
    assert not any(k in cleaned for k in before if k.startswith("GIT_")
                   and k not in {"GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL"})


def test_report_ignores_injected_core_worktree(setup, monkeypatch):
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.worktree")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", str(setup["target"]))
    assert report(setup)["source_revision"] == setup["revision"]
