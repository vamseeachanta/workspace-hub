"""Advisory workflow contract, from issue #4228 and workflow syntax docs.

https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
(accessed 2026-10-22). Expected matrices are literal synthetic family sets.
"""

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def workflow_module(tmp_path):
    spec = importlib.util.spec_from_file_location("hub_workflow", ROOT / "scripts/ci/hub_test_workflow.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matrix_excludes_unreviewed_and_failed_families(workflow_module, tmp_path):
    """Only A both collects and has reviewed bodies: {A,B,C} intersect {A}."""
    health = {"families": {
        "A": {"collection_status": "COLLECTABLE", "body_status": "EVALUATED"},
        "B": {"collection_status": "NOT_GATING", "body_status": "EVALUATED"},
        "C": {"collection_status": "COLLECTABLE", "body_status": "NOT_EVALUATED"},
    }}
    policy = {"body_evaluated": ["A", "B"]}
    result = workflow_module.matrix_plan(["A", "B", "C"], health, policy)
    assert result["matrix"] == {"include": [{"family": "A"}]}
    assert result["required"] is True
    assert set(result["excluded"]) == {"B", "C"}


def test_empty_and_unknown_families_are_explicit(workflow_module, tmp_path):
    result = workflow_module.matrix_plan(["unknown"], {"families": {}}, {"body_evaluated": []})
    assert result["required"] is False
    assert result["matrix"] == {"include": []}
    assert "unknown" in result["excluded"]


@pytest.mark.parametrize("discover", ["failure", "cancelled", "skipped"])
def test_aggregate_rejects_missing_discovery(workflow_module, tmp_path, discover):
    assert not workflow_module.aggregate_ok(discover, "skipped", False)


@pytest.mark.parametrize("family", ["failure", "cancelled", "skipped"])
def test_aggregate_rejects_missing_required_work(workflow_module, tmp_path, family):
    assert not workflow_module.aggregate_ok("success", family, True)


def test_aggregate_allows_only_intentional_empty_selection(workflow_module, tmp_path):
    assert workflow_module.aggregate_ok("success", "skipped", False)
    assert workflow_module.aggregate_ok("success", "success", True)
    assert not workflow_module.aggregate_ok("success", "cancelled", False)


def test_workflow_safety_properties(tmp_path):
    target = tmp_path / "workflow.yml"
    target.write_bytes((ROOT / ".github/workflows/hub-tests-by-family.yml").read_bytes())
    workflow = yaml.safe_load(target.read_text())
    trigger = workflow.get("on", workflow.get(True))
    assert "pull_request" in trigger
    assert "ready_for_review" in trigger["pull_request"]["types"]
    assert workflow["permissions"] == {"contents": "read"}
    assert "pull_request.number" in workflow["concurrency"]["group"]
    assert workflow["concurrency"]["cancel-in-progress"] is True
    jobs = workflow["jobs"]
    for job in jobs.values():
        assert job["timeout-minutes"] > 0
        assert not job.get("continue-on-error", False)
    assert "draft" in jobs["discover"]["if"]
    aggregate = jobs["aggregate"]
    assert aggregate["name"] == "Hub test aggregate"
    assert "always()" in aggregate["if"]
    assert "draft" in aggregate["if"]
    assert set(aggregate["needs"]) == {"discover", "test-family"}
    assert jobs["test-family"]["strategy"]["fail-fast"] is False
    assert "required == 'true'" in jobs["test-family"]["if"]
    for job in jobs.values():
        for step in job.get("steps", []):
            assert not step.get("continue-on-error", False)


def test_invalid_status_cannot_pass(workflow_module, tmp_path):
    assert not workflow_module.aggregate_ok("success", "unexpected", False)


def test_all_inventory_families_have_rule_witness(tmp_path):
    """Build a synthetic map with the actual family ids, one witness per id."""
    spec = importlib.util.spec_from_file_location("hub_select", ROOT / "scripts/ci/hub_test_select.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ids = json.loads((ROOT / "config/ci/hub-test-families.json").read_text())["families"]
    families = {}
    for name in ids:
        if name == "tests/root":
            path = "tests/test_synthetic.py"
        else:
            path = f"{name}/test_synthetic.py"
        families[name] = [path]
    rules_path = tmp_path / "rules.json"
    rules_path.write_bytes((ROOT / "config/ci/hub-test-rules.json").read_bytes())
    rules = module.load_rules(rules_path)
    for name, files in families.items():
        selection = module.select([("M", files[0])], families, rules)
        assert name in selection["families"]
        assert selection["paths"][0]["rule"] != "unmapped-code"
