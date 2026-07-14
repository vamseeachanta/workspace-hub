from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))
from rule_authority import codec, protection  # noqa: E402


def test_normalized_environment_and_ruleset_readback_matches_preview():
    fixture = ROOT / "scripts/legal/tests/fixtures"
    preview = codec.parse_canonical(
        (fixture / "rule-authority-protection-preview.json").read_bytes()
    )
    environment = codec.parse_canonical(
        (fixture / "rule-authority-environment-response.json").read_bytes()
    )
    ruleset = codec.parse_canonical(
        (fixture / "rule-authority-ruleset-response.json").read_bytes()
    )
    assert protection.verify_readback(preview, environment, ruleset)
    ruleset["bypass_actors"] = [{"actor_id": 1}]
    with pytest.raises(codec.AuthorityError, match="integrity"):
        protection.verify_readback(preview, environment, ruleset)


def test_ruleset_fixture_uses_official_normalized_rest_shapes():
    fixture = ROOT / "scripts/legal/tests/fixtures"
    ruleset = codec.parse_canonical(
        (fixture / "rule-authority-ruleset-response.json").read_bytes()
    )
    required_workflows = next(
        rule for rule in ruleset["rules"] if rule["type"] == "required_workflows"
    )
    assert "parameters" not in required_workflows
    workflow = required_workflows["workflows"][0]
    assert isinstance(workflow["repository_id"], int)
    checks = next(
        rule for rule in ruleset["rules"] if rule["type"] == "required_status_checks"
    )["parameters"]["required_status_checks"]
    assert isinstance(checks[0]["integration_id"], int)


@pytest.mark.parametrize("field", ["repository_id", "integration_id"])
def test_ruleset_readback_rejects_non_integer_rest_ids(field):
    fixture = ROOT / "scripts/legal/tests/fixtures"
    preview = codec.parse_canonical(
        (fixture / "rule-authority-protection-preview.json").read_bytes()
    )
    environment = codec.parse_canonical(
        (fixture / "rule-authority-environment-response.json").read_bytes()
    )
    ruleset = codec.parse_canonical(
        (fixture / "rule-authority-ruleset-response.json").read_bytes()
    )
    if field == "repository_id":
        preview["ruleset"]["required_workflow"][field] = "123456789"
    else:
        preview["ruleset"]["required_integration_id"] = "15368"
    with pytest.raises(codec.AuthorityError, match="integrity"):
        protection.verify_readback(preview, environment, ruleset)
