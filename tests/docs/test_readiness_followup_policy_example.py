"""Offline conformance cases from docs/examples/readiness-followup-policy.md.

All labels and expected keys are independently enumerated from its fixture table.
"""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/readiness/followup_policy.py"
spec = importlib.util.spec_from_file_location("followup_policy", EXAMPLE)
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)

# Literal fixture policy and gap A, cited in the documentation's fixture tables.
POLICY = {"context-budget": "high", "truncation-safety": "medium"}
GAP = {
    "repository": "example-repository",
    "release": "example-release",
    "dimension": "context-budget",
    "surface": "adapter-guide",
    "gap_id": "missing-budget",
    "severity": "medium",
    "summary": "Read budget is absent",
    "evidence": "fixture:missing-budget",
    "responsible_role": "documentation-maintainer",
    "accountable_role": "release-maintainer",
    "action": "Document the intended read budget",
    "acceptance": "The guide states its intended read budget",
}
# Hand enumeration: namespace, repository, release, dimension, surface, gap_id.
KEY_A = (
    '["readiness-followup","example-repository","example-release",'
    '"context-budget","adapter-guide","missing-budget"]'
)
KEY_B = (
    '["readiness-followup","example-repository","example-release",'
    '"context-budget","adapter-guide","missing-budget-note"]'
)


def test_duplicate_gap_is_idempotent():
    original = copy.deepcopy(GAP)
    drafts = example.propose([GAP, copy.deepcopy(GAP)], POLICY, [])
    assert [draft["duplicate_key"] for draft in drafts] == [KEY_A]
    assert example.propose([GAP], POLICY, drafts) == []
    assert GAP == original


def test_distinct_gap_is_distinct():
    other = {**GAP, "gap_id": "missing-budget-note"}
    drafts = example.propose([GAP, other], POLICY, [])
    assert {draft["duplicate_key"] for draft in drafts} == {KEY_A, KEY_B}


def test_below_threshold_is_draft_only():
    (draft,) = example.propose([GAP], POLICY, [])
    assert draft["duplicate_key"] == KEY_A
    assert draft["status"] == "draft"
    assert draft["threshold_met"] is False
    assert draft["title"] == "Readiness follow-up: Read budget is absent"
    assert draft["body"] == (
        "Dimension: context-budget\nSurface: adapter-guide\n"
        "Evidence: fixture:missing-budget\n"
        "Responsible role: documentation-maintainer\n"
        "Accountable role: release-maintainer\n"
        "Action: Document the intended read budget\n"
        "Acceptance: The guide states its intended read budget"
    )


@pytest.mark.parametrize("field", ["responsible_role", "accountable_role"])
@pytest.mark.parametrize("value", ["absent", None, "", " "])
def test_missing_ownership_is_rejected(field, value):
    gap = {**GAP, field: value}
    if value == "absent":
        del gap[field]
    with pytest.raises(ValueError, match=field):
        example.propose([gap], POLICY, [])


@pytest.mark.parametrize("severity", ["high", "critical"])
def test_at_or_above_threshold_stays_draft(severity):
    (draft,) = example.propose([{**GAP, "severity": severity}], POLICY, [])
    assert draft["status"] == "draft"
    assert draft["threshold_met"] is True


@pytest.mark.parametrize("field", ["repository", "release", "dimension", "surface", "gap_id"])
def test_identity_components_are_independent(field):
    changed = {**GAP, field: "truncation-safety" if field == "dimension" else "different"}
    expected_parts = [
        "readiness-followup", "example-repository", "example-release",
        "context-budget", "adapter-guide", "missing-budget",
    ]
    fields = ["namespace", "repository", "release", "dimension", "surface", "gap_id"]
    expected_parts[fields.index(field)] = changed[field]
    (draft,) = example.propose([changed], POLICY, [])
    assert json.loads(draft["duplicate_key"]) == expected_parts


def test_input_order_does_not_change_json():
    other = {**GAP, "gap_id": "missing-budget-note"}
    assert example.propose([GAP, other], POLICY, []) == example.propose([other, GAP], POLICY, [])


def test_key_encoding_does_not_confuse_delimiters():
    left = {**GAP, "surface": "guide:note", "gap_id": "missing"}
    right = {**GAP, "surface": "guide", "gap_id": "note:missing"}
    keys = {draft["duplicate_key"] for draft in example.propose([left, right], POLICY, [])}
    assert keys == {
        '["readiness-followup","example-repository","example-release",'
        '"context-budget","guide:note","missing"]',
        '["readiness-followup","example-repository","example-release",'
        '"context-budget","guide","note:missing"]',
    }


@pytest.mark.parametrize("field", ["severity", "summary", "evidence", "action", "acceptance"])
def test_required_metadata_is_rejected_when_absent(field):
    gap = dict(GAP)
    del gap[field]
    with pytest.raises(ValueError, match=field):
        example.propose([gap], POLICY, [])


@pytest.mark.parametrize("policy", [{}, {"context-budget": "unknown"}, {"context-budget": True}])
def test_policy_is_explicit_and_validated(policy):
    with pytest.raises(ValueError, match="policy"):
        example.propose([GAP], policy, [])


@pytest.mark.parametrize("severity", ["unknown", True, None])
def test_unknown_severity_is_rejected(severity):
    with pytest.raises(ValueError, match="severity"):
        example.propose([{**GAP, "severity": severity}], POLICY, [])


@pytest.mark.parametrize("extra", [{"create_now": True}, {"publication_authorized": True}])
def test_publication_flags_are_not_inputs(extra):
    with pytest.raises(ValueError, match="fields"):
        example.propose([{**GAP, **extra}], POLICY, [])


def test_conflicting_duplicate_is_rejected():
    changed = {**GAP, "evidence": "fixture:updated-evidence"}
    with pytest.raises(ValueError, match="conflicting"):
        example.propose([GAP, changed], POLICY, [])
    existing = example.propose([GAP], POLICY, [])
    snapshot = copy.deepcopy(existing)
    with pytest.raises(ValueError, match="conflicting"):
        example.propose([changed], POLICY, existing)
    assert existing == snapshot


def test_existing_proposal_key_is_checked():
    existing = example.propose([GAP], POLICY, [])
    (draft,) = existing
    draft["duplicate_key"] = KEY_B
    with pytest.raises(ValueError, match="existing"):
        example.propose([GAP], POLICY, existing)


def test_existing_non_draft_is_rejected():
    existing = example.propose([GAP], POLICY, [])
    (draft,) = existing
    draft["status"] = "created"
    with pytest.raises(ValueError, match="existing"):
        example.propose([GAP], POLICY, existing)


def test_documented_command_emits_deterministic_json_offline(tmp_path):
    # A fresh interpreter and an unrelated working directory exercise the CLI.
    command = [sys.executable, str(EXAMPLE)]
    first = subprocess.run(command, cwd=tmp_path, check=True, capture_output=True, text=True)
    second = subprocess.run(command, cwd=tmp_path, check=True, capture_output=True, text=True)
    assert first.stdout == second.stdout
    assert first.stderr == second.stderr == ""
    drafts = json.loads(first.stdout)
    assert [draft["duplicate_key"] for draft in drafts] == [KEY_A, KEY_B]
    assert {draft["status"] for draft in drafts} == {"draft"}


@pytest.mark.parametrize("value", [" leading", "trailing ", "two\nlines", "two\rlines", True])
def test_invalid_metadata_is_rejected(value):
    with pytest.raises(ValueError, match="evidence"):
        example.propose([{**GAP, "evidence": value}], POLICY, [])


def test_changed_policy_does_not_silently_reuse_a_draft():
    existing = example.propose([GAP], POLICY, [])
    with pytest.raises(ValueError, match="existing"):
        example.propose([GAP], {"context-budget": "medium"}, existing)


def test_second_fixture_dimension_uses_its_own_threshold():
    (draft,) = example.propose([{**GAP, "dimension": "truncation-safety"}], POLICY, [])
    assert draft["threshold_met"] is True
    assert draft["status"] == "draft"


def test_existing_conflicts_are_rejected_even_without_new_gaps():
    first = example.propose([GAP], POLICY, [])
    changed = example.propose([{**GAP, "action": "Review the intended budget"}], POLICY, [])
    with pytest.raises(ValueError, match="conflicting"):
        example.propose([], POLICY, first + changed)


def test_reordered_fields_and_iterables_keep_the_same_result():
    reordered = dict(reversed(list(GAP.items())))
    policy_snapshot = dict(POLICY)
    assert example.propose(iter([reordered]), POLICY, iter([])) == example.propose([GAP], POLICY, [])
    assert POLICY == policy_snapshot


def test_output_is_independent_of_mutable_inputs():
    gap = dict(GAP)
    (draft,) = example.propose([gap], POLICY, [])
    gap["action"] = "Review the intended budget"
    assert draft["gap"]["action"] == "Document the intended read budget"


def test_existing_threshold_flag_requires_a_boolean():
    existing = example.propose([GAP], POLICY, [])
    (draft,) = existing
    # Documentation: "Proposal minimums" requires a JSON boolean. Independent
    # Python calculation: int(False) equals False but serializes as a number.
    draft["threshold_met"] = int(False)
    with pytest.raises(ValueError, match="existing"):
        example.propose([GAP], POLICY, existing)
