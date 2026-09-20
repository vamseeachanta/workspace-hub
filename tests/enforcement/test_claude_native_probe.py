"""Probe parser tests use synthetic CLI output, never provider readiness claims."""
import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def probe():
    path = Path(__file__).resolve().parents[2] / "scripts/agents/claude_native_probe.py"
    spec = importlib.util.spec_from_file_location("probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def events(**overrides):
    init = {"type": "system", "subtype": "init", "tools": [], "mcp_servers": [],
            "plugins": [{"name": "agents-md", "source": "agents-md@builtin"}]}
    init.update(overrides)
    result = {"type": "result", "is_error": False,
              "result": json.dumps({"global_token": "g", "project_token": "p"})}
    return [init, result]


def test_exact_tokens_and_builtin_required(probe):
    assert probe.validate_events(events(), "g", "p")["status"] == "PASS"


@pytest.mark.parametrize("override", [{"plugins": []}, {"tools": ["Read"]},
                                      {"mcp_servers": [{"name": "unexpected"}]}])
def test_unsafe_or_non_native_context_rejected(probe, override):
    with pytest.raises(ValueError):
        probe.validate_events(events(**override), "g", "p")


def test_wrong_response_is_not_provider_unavailable(probe):
    with pytest.raises(ValueError):
        probe.validate_events(events(), "NOT_LOADED", "p")


def test_tool_attempt_invalidates_trial(probe):
    data = events()
    data.insert(1, {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Read", "input": {"file_path": "fixture"}}]}})
    with pytest.raises(ValueError):
        probe.validate_events(data, "g", "p")


def test_protected_configuration_change_visible(probe, tmp_path):
    user = tmp_path / ".claude"
    user.mkdir()
    (user / "settings.json").write_text("{}")
    before = probe.protected_state(tmp_path)
    (user / "settings.json").write_text('{"changed":true}')
    assert probe.protected_state(tmp_path) != before


def test_probe_links_are_excluded_but_other_rules_preserved(probe, tmp_path):
    rules = tmp_path / ".claude/rules"
    rules.mkdir(parents=True)
    (rules / "workspace-soul.md").write_text("trial")
    before = probe.protected_state(tmp_path)
    (rules / "unrelated.md").write_text("policy")
    assert probe.protected_state(tmp_path) != before


def test_canonical_prompt_does_not_leak_expected_answers(probe):
    prompt = probe.probe_prompt("canonical", "repository")
    assert "feedback_edit_tool_freshness_window_after_writes" not in prompt
    assert "docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md" not in prompt
    assert "Edit tool freshness" in prompt


def test_negative_sentinel_exempt_for_both_fields(probe):
    probe.check_prompt("Use NOT_LOADED if absent", "NOT_LOADED", "NOT_LOADED")


def test_read_prompt_has_no_contradictory_tool_ban(probe):
    prompt = probe.probe_prompt("canonical", "lazy", allow_read=True)
    assert "Do not use tools" not in prompt
    assert "exactly one Read" in prompt


def lazy_events(path):
    data = events(tools=["Read"])
    data[1:1] = [
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "one",
         "name": "Read", "input": {"file_path": str(path)}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "one",
         "content": "harmless"}]}}]
    return data


def test_lazy_exact_read_and_native_result_required(probe, tmp_path):
    path = tmp_path / "harmless.txt"
    assert probe.validate_events(lazy_events(path), "g", "p", read_path=path)["status"] == "PASS"


@pytest.mark.parametrize("mutation", ["other-path", "extra-tool", "denial", "missing-result"])
def test_lazy_invalid_read_blocks(probe, tmp_path, mutation):
    path = tmp_path / "harmless.txt"
    data = lazy_events(path)
    if mutation == "other-path":
        data[1]["message"]["content"][0]["input"]["file_path"] = str(tmp_path / "other")
    elif mutation == "extra-tool":
        data[1]["message"]["content"].append({"type": "tool_use", "name": "Bash", "input": {}})
    elif mutation == "denial":
        data[-1]["permission_denials"] = [{"tool_name": "Read"}]
    else:
        del data[2]
    with pytest.raises(ValueError):
        probe.validate_events(data, "g", "p", read_path=path)


def test_hook_audit_binds_exact_tool_call(probe, tmp_path):
    target, audit = tmp_path / "harmless.txt", tmp_path / "audit.jsonl"
    row = {"tool_use_id": "one", "tool_name": "Read", "decision": "allow", "requested_path": str(target)}
    audit.write_text(json.dumps(row) + "\n")
    probe.validate_audit(audit, lazy_events(target), target, "allow")
    row["tool_use_id"] = "unrelated"
    audit.write_text(json.dumps(row) + "\n")
    with pytest.raises(ValueError, match="enforcement"):
        probe.validate_audit(audit, lazy_events(target), target, "allow")


def test_denial_control_requires_failed_tool_result(probe, tmp_path):
    target = tmp_path / "denied.txt"
    data = lazy_events(target)
    with pytest.raises(ValueError):
        probe.validate_read(data, target, denied=True)
    data[2]["message"]["content"][0]["is_error"] = True
    probe.validate_read(data, target, denied=True)


def test_guard_settings_uses_arguments_without_shell(probe, tmp_path):
    target = tmp_path / "harmless.txt"
    target.write_text("no canary")
    hook = probe.guard_settings(target, tmp_path / "audit")["hooks"]["PreToolUse"][0]["hooks"][0]
    assert hook["type"] == "command" and Path(hook["command"]).is_absolute()
    assert hook["args"][:2] == ["-I", "-B"]
    assert str(target) in hook["args"]


def test_credential_refresh_changes_full_but_not_admission(probe, tmp_path):
    user = tmp_path / ".claude"
    user.mkdir()
    credential = user / ".credentials.json"
    credential.write_text('{"synthetic":"before"}')
    full, stable = probe.protected_state(tmp_path), probe.protected_admission_state(tmp_path)
    credential.write_text('{"synthetic":"after"}')
    assert probe.protected_state(tmp_path) != full
    assert probe.protected_admission_state(tmp_path) == stable
    record = next(row for row in stable if row["path"] == ".credentials.json")
    assert "sha256" not in record and record["type"] == "regular"
    credential.unlink()
    assert probe.protected_admission_state(tmp_path) != stable


def test_admission_does_not_read_credentials_and_preserves_rule_gate(probe, tmp_path, monkeypatch):
    user = tmp_path / ".claude"
    (user / "rules").mkdir(parents=True)
    (user / ".credentials.json").write_text("synthetic")
    original = probe.sha
    def deny_credentials(path):
        if path.name == ".credentials.json":
            pytest.fail("admission read volatile credentials")
        return original(path)
    monkeypatch.setattr(probe, "sha", deny_credentials)
    before = probe.protected_admission_state(tmp_path)
    (user / "rules/new.md").write_text("new policy")
    assert probe.protected_admission_state(tmp_path) != before
