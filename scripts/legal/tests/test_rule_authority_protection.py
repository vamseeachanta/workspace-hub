from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))
from rule_authority import codec, protection  # noqa: E402

FIXTURE = ROOT / "scripts/legal/tests/fixtures"
PREVIEW = (
    ROOT / "docs/plans/evidence/2026-07-14-issue-3522-phase-a-protection-preview.json"
)


def _load(path: Path):
    return codec.parse_canonical(path.read_bytes())


def test_canonical_preview_is_the_normalized_rest_contract():
    preview = _load(PREVIEW)
    ruleset = preview["ruleset"]
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


def test_normalized_environment_and_ruleset_readback_matches_canonical_preview():
    preview = _load(PREVIEW)
    environment = _load(FIXTURE / "rule-authority-environment-response.json")
    ruleset = _load(FIXTURE / "rule-authority-ruleset-response.json")
    assert protection.verify_readback(preview, environment, ruleset)
    ruleset["bypass_actors"] = [{"actor_id": 1}]
    with pytest.raises(codec.AuthorityError, match="integrity"):
        protection.verify_readback(preview, environment, ruleset)


@pytest.mark.parametrize(
    ("document", "mutation"),
    [
        ("preview", lambda value: value.pop("environment")),
        ("preview", lambda value: value.pop("ruleset")),
        ("preview", lambda value: value["ruleset"].update(rules=None)),
        ("ruleset", lambda value: value.pop("rules")),
        ("ruleset", lambda value: value.update(rules=None)),
        ("environment", lambda value: value.update(protection_rules=None)),
    ],
)
def test_invalid_or_missing_shapes_raise_authority_error(document, mutation):
    values = {
        "preview": _load(PREVIEW),
        "environment": _load(FIXTURE / "rule-authority-environment-response.json"),
        "ruleset": _load(FIXTURE / "rule-authority-ruleset-response.json"),
    }
    mutation(values[document])
    with pytest.raises(codec.AuthorityError, match="integrity"):
        protection.verify_readback(
            values["preview"], values["environment"], values["ruleset"]
        )


@pytest.mark.parametrize("field", ["repository_id", "integration_id"])
def test_canonical_preview_rejects_non_integer_rest_ids(field):
    preview = _load(PREVIEW)
    environment = _load(FIXTURE / "rule-authority-environment-response.json")
    ruleset = _load(FIXTURE / "rule-authority-ruleset-response.json")
    preview = copy.deepcopy(preview)
    if field == "repository_id":
        workflow_rule = next(
            rule
            for rule in preview["ruleset"]["rules"]
            if rule["type"] == "required_workflows"
        )
        workflow_rule["workflows"][0][field] = "123456789"
    else:
        checks_rule = next(
            rule
            for rule in preview["ruleset"]["rules"]
            if rule["type"] == "required_status_checks"
        )
        checks_rule["parameters"]["required_status_checks"][0][field] = "15368"
    with pytest.raises(codec.AuthorityError, match="integrity"):
        protection.verify_readback(preview, environment, ruleset)
