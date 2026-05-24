from __future__ import annotations

import importlib.util
from pathlib import Path


def load_checker():
    path = Path(__file__).resolve().parents[2] / "scripts" / "readiness" / "check-sibling-sso-flow.py"
    spec = importlib.util.spec_from_file_location("sibling_sso_checker", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_intxlnk_classified_as_corrupted_symlink(tmp_path):
    checker = load_checker()
    p = tmp_path / "skills"
    p.write_bytes(b"IntxLNK\x01.\x00.\x00/\x00.\x00")

    result = checker.classify_provider_skill_path(p, "../../workspace-hub/.claude/skills", {tmp_path / "workspace-hub" / ".claude" / "skills"})

    assert result["status"] == "fail"
    assert result["kind"] == "corrupted_ntfs_symlink"
    assert result["repair_action"] == "unlink_then_recreate"


def test_provider_symlink_broken_target_fails(tmp_path):
    checker = load_checker()
    path = tmp_path / "repo" / ".codex"
    path.mkdir(parents=True)
    link = path / "skills"
    link.symlink_to("../../.claude/skills")

    result = checker.classify_provider_skill_path(link, "../../workspace-hub/.claude/skills", {tmp_path / "workspace-hub" / ".claude" / "skills"})

    assert result["status"] == "fail"
    assert result["kind"] == "broken_symlink"


def test_provider_symlink_canonical_sibling_target_passes(tmp_path):
    checker = load_checker()
    central = tmp_path / "workspace-hub" / ".claude" / "skills"
    central.mkdir(parents=True)
    (central / "SKILL.md").write_text("---\nname: central\n---\n")
    provider = tmp_path / "digitalmodel" / ".codex"
    provider.mkdir(parents=True)
    link = provider / "skills"
    link.symlink_to("../../workspace-hub/.claude/skills")

    result = checker.classify_provider_skill_path(link, "../../workspace-hub/.claude/skills", {central})

    assert result["status"] == "pass"
    assert result["target"] == "../../workspace-hub/.claude/skills"


def test_workspace_hub_self_skill_symlink_passes(tmp_path):
    checker = load_checker()
    central = tmp_path / "workspace-hub" / ".claude" / "skills"
    central.mkdir(parents=True)
    (central / "SKILL.md").write_text("---\nname: central\n---\n")
    provider = tmp_path / "workspace-hub" / ".codex"
    provider.mkdir(parents=True)
    link = provider / "skills"
    link.symlink_to("../.claude/skills")

    result = checker.classify_provider_skill_path(link, "../.claude/skills", {central})

    assert result["status"] == "pass"


def test_present_repo_missing_provider_skill_link_fails(tmp_path):
    checker = load_checker()
    central = tmp_path / "workspace-hub" / ".claude" / "skills"
    central.mkdir(parents=True)
    (central / "SKILL.md").write_text("---\nname: central\n---\n")
    repo = tmp_path / "digitalmodel"
    repo.mkdir()

    result = checker.check_skills(tmp_path / "workspace-hub", tmp_path, ["digitalmodel"])

    assert result["status"] == "fail"
    assert result["repos"]["digitalmodel"][".codex"]["status"] == "fail"
    assert result["repos"]["digitalmodel"][".codex"]["kind"] == "missing"


def test_checker_json_report_has_four_flow_statuses(tmp_path):
    checker = load_checker()
    report = checker.empty_report()

    assert set(report) == {"memory", "skills", "harness_contracts", "registry"}
    for section in report.values():
        assert section["status"] in {"pass", "fail", "not_present"}
        assert "evidence_paths" in section


def test_resolve_machine_accepts_registry_key_hostname_and_alias(tmp_path):
    checker = load_checker()
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        """
machines:
  dev-primary:
    hostname: ace-linux-1
    hostname_aliases: [vamsee-linux1]
  dev-secondary:
    hostname: ace-linux-2
""".lstrip()
    )

    assert checker.resolve_machine(registry, "dev-primary")[0] == "dev-primary"
    assert checker.resolve_machine(registry, "ace-linux-1")[0] == "dev-primary"
    assert checker.resolve_machine(registry, "vamsee-linux1")[0] == "dev-primary"
