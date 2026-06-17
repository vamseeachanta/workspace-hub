"""Validation for #3191 gated workflow templates.

Run: uv run --group dev pytest tests/workflow/test_gated_workflow_templates.py -v
(jsonschema is a dev-group dependency.)

These templates are Level-0/1 DATA, not enforcement — this suite checks they parse,
conform to schema/workflow.schema.json (scoped by `kind: gated-workflow`, so legacy
dialects are untouched), and satisfy the gate-chain invariants.
"""
import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WF_DIR = REPO_ROOT / ".claude" / "workflows"
SCHEMA_PATH = WF_DIR / "schema" / "workflow.schema.json"

CANONICAL_STATUS_LABELS = {"status:plan-review", "status:plan-approved", "status:completeness-verified"}
CLAUDE_ONLY_TOKENS = ("tool: Task", "subagent_type", "@.claude/agent-library")


def _load_yaml(p):
    with open(p) as fh:
        return yaml.safe_load(fh)


def _gated_files():
    out = []
    for p in sorted(WF_DIR.glob("*.yaml")):
        try:
            doc = _load_yaml(p)
        except yaml.YAMLError:
            continue
        if isinstance(doc, dict) and doc.get("kind") == "gated-workflow":
            out.append(p)
    return out


GATED = _gated_files()


def test_gated_files_present():
    names = {p.name for p in GATED}
    assert {"issue-gate-chain.yaml", "tdd-implementation.yaml",
            "cross-provider-review-workflow.yaml"} <= names


@pytest.mark.parametrize("path", GATED, ids=lambda p: p.name)
def test_matches_schema(path):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.Draft7Validator(schema).validate(_load_yaml(path))


@pytest.mark.parametrize("path", GATED, ids=lambda p: p.name)
def test_has_source_citation(path):
    assert _load_yaml(path).get("source"), f"{path.name} missing inline `source:` citation"


@pytest.mark.parametrize("path", GATED, ids=lambda p: p.name)
def test_provider_neutral(path):
    text = path.read_text()
    for tok in CLAUDE_ONLY_TOKENS:
        assert tok not in text, f"{path.name} contains Claude-only token {tok!r}"


@pytest.mark.parametrize("path", GATED, ids=lambda p: p.name)
def test_status_labels_canonical(path):
    for g in _load_yaml(path)["gates"]:
        lbl = g.get("status_label")
        if lbl:
            assert lbl in CANONICAL_STATUS_LABELS, f"{path.name}: non-canonical status_label {lbl!r}"


@pytest.mark.parametrize("path", GATED, ids=lambda p: p.name)
def test_tier_review_depths(path):
    tiers = _load_yaml(path).get("tiers")
    if tiers:
        assert len(tiers["T1"]["review_providers"]) == 1
        assert len(tiers["T2"]["review_providers"]) == 2
        assert len(tiers["T3"]["review_providers"]) == 3


def _gates(name):
    return _load_yaml(WF_DIR / name)["gates"]


def test_issue_gate_chain_ordered():
    ids = [g["id"] for g in _gates("issue-gate-chain.yaml")]
    assert ids == ["issue", "resource_intel", "plan", "adversarial_review_plan",
                   "user_approval", "implement", "adversarial_review_code",
                   "completeness_gate", "close"]


def test_user_approval_is_user_only():
    ua = next(g for g in _gates("issue-gate-chain.yaml") if g["id"] == "user_approval")
    assert ua["actor"] == "USER_ONLY"
    assert ua["self_approve"] == "forbidden"


def test_tdd_tests_before_implement():
    ids = [g["id"] for g in _gates("tdd-implementation.yaml")]
    assert ids.index("test_first") < ids.index("implement")


def test_review_workflow_references_real_fanout():
    runners = [g.get("runner") for g in _gates("cross-provider-review-workflow.yaml") if g.get("runner")]
    fanout = "scripts/review/plan-review-fanout.sh"
    assert fanout in runners, "review workflow must reference the real fanout runner"
    assert (REPO_ROOT / fanout).exists(), f"{fanout} not found on disk"


def test_review_workflow_degradation_and_default_three():
    dispatch = next(g for g in _gates("cross-provider-review-workflow.yaml") if g["id"] == "dispatch_review")
    assert dispatch["on_provider_unavailable"] == "continue_and_record"
    assert dispatch["default_providers"] == ["claude", "codex", "gemini"]
