"""Synthetic, hand-authored acceptance examples; source: issues/2185.

Expected labels are authored independently of the classifier. Counts below are
hand tallies of the listed rows, not values calculated by the implementation.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts" / "analysis" / "unresolved_read_classifier.py"
)
spec = importlib.util.spec_from_file_location("unresolved_read_classifier", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def row(evidence=None, *, provider="alpha", target="docs/example.md"):
    return {"provider": provider, "target": target, "evidence": evidence or {}}


# issues/2185 reason buckets, with explicit positive and negative observations.
TRUTH_TABLE = [
    ({"alias_resolves": False}, "alias-gap", "ALIAS_GAP"),
    ({"registry_entry_present": False}, "missing-registry-entry", "MISSING_REGISTRY_ENTRY"),
    ({"target_accessible": False}, "inaccessible-target", "INACCESSIBLE_TARGET"),
    ({"provenance_complete": False}, "provenance-gap", "PROVENANCE_GAP"),
    ({"publication_matches": False}, "publication-drift", "PUBLICATION_DRIFT"),
    ({"target_state": "stale"}, "stale-deleted-target", "STALE_DELETED_TARGET"),
    ({"target_state": "deleted"}, "stale-deleted-target", "STALE_DELETED_TARGET"),
    (
        {"suppression_policy_matches": True, "suppression_basis": "documented exception"},
        "suppression-eligible", "SUPPRESSION_ELIGIBLE",
    ),
    ({}, "unknown-needs-review", "UNKNOWN_NEEDS_REVIEW"),
    (
        {"alias_resolves": True, "registry_entry_present": True,
         "target_accessible": True, "provenance_complete": True,
         "publication_matches": True, "target_state": "present",
         "suppression_policy_matches": False},
        "unknown-needs-review", "UNKNOWN_NEEDS_REVIEW",
    ),
    (
        {"alias_resolves": False, "registry_entry_present": True,
         "target_accessible": True, "target_state": "present"},
        "alias-gap", "ALIAS_GAP",
    ),
    (
        {"alias_resolves": False, "suppression_policy_matches": True},
        "alias-gap", "ALIAS_GAP",
    ),
]


@pytest.mark.parametrize("evidence,bucket,reason_code", TRUTH_TABLE)
def test_unresolved_bucket_truth_table(evidence, bucket, reason_code):
    original = row(evidence)
    snapshot = json.loads(json.dumps(original))
    assert module.classify_read(original) == {
        "provider": "alpha", "target": "docs/example.md",
        "bucket": bucket, "reason_code": reason_code,
    }
    assert original == snapshot


@pytest.mark.parametrize("evidence", [
    {}, {"target_state": "unknown"}, {"alias_resolves": None},
    {"alias_resolves": "false"}, {"alias_resolves": 0},
    {"target_state": "absent"}, {"alias_resolves": False, "unexpected": True},
    {"target_state": "deleted", "target_accessible": True},
    {"registry_entry_present": False, "provenance_complete": False},
    {"alias_resolves": False, "suppression_policy_matches": True,
     "suppression_basis": "documented exception"},
    {"target_accessible": False, "suppression_basis": []},
    [], "unstructured evidence",
])
def test_missing_or_conflicting_evidence_is_unknown(evidence):
    candidate = row()
    candidate["evidence"] = evidence
    assert module.classify_read(candidate)["reason_code"] == "UNKNOWN_NEEDS_REVIEW"


def test_every_pair_of_diagnostic_causes_is_unknown():
    # Hand-authored causes from issues/2185; no cause outranks another.
    causes = [
        {"alias_resolves": False}, {"registry_entry_present": False},
        {"target_accessible": False}, {"provenance_complete": False},
        {"publication_matches": False}, {"target_state": "stale"},
    ]
    for left, right in itertools.combinations(causes, 2):
        assert module.classify_read(row(left | right))["bucket"] == "unknown-needs-review"


@pytest.mark.parametrize("evidence", [
    {}, {"suppression_policy_matches": True},
    {"suppression_basis": "documented exception"},
    {"suppression_policy_matches": False, "suppression_basis": "documented exception"},
    {"suppression_policy_matches": True, "suppression_basis": "  "},
    {"suppression_policy_matches": "true", "suppression_basis": "documented exception"},
])
def test_suppression_requires_explicit_evidence(evidence):
    assert module.classify_read(row(evidence))["bucket"] == "unknown-needs-review"


def test_complete_suppression_evidence_only_reports_eligibility():
    candidate = row({"suppression_policy_matches": True,
                     "suppression_basis": "documented exception"})
    result = module.classify_rows([candidate])
    assert result["rows"] == [{"provider": "alpha", "target": "docs/example.md",
                               "bucket": "suppression-eligible",
                               "reason_code": "SUPPRESSION_ELIGIBLE"}]
    assert candidate["evidence"]["suppression_basis"] == "documented exception"


def test_bucket_counts_and_cli_order_are_deterministic(tmp_path):
    # Independent hand tally: alpha has two alias gaps and one unknown;
    # beta has one inaccessible target. Duplicate rows represent separate reads.
    rows = [row({"alias_resolves": False}), row(),
            row({"target_accessible": False}, provider="beta"),
            row({"alias_resolves": False})]
    expected_counts = {
        "alpha": {"alias-gap": 2, "unknown-needs-review": 1},
        "beta": {"inaccessible-target": 1},
    }
    expected_rows = [
        {"provider": "alpha", "target": "docs/example.md",
         "bucket": "alias-gap", "reason_code": "ALIAS_GAP"},
        {"provider": "alpha", "target": "docs/example.md",
         "bucket": "alias-gap", "reason_code": "ALIAS_GAP"},
        {"provider": "alpha", "target": "docs/example.md",
         "bucket": "unknown-needs-review", "reason_code": "UNKNOWN_NEEDS_REVIEW"},
        {"provider": "beta", "target": "docs/example.md",
         "bucket": "inaccessible-target", "reason_code": "INACCESSIBLE_TARGET"},
    ]
    expected = {"rows": expected_rows, "bucket_counts": expected_counts}
    assert module.classify_rows([]) == {"rows": [], "bucket_counts": {}}
    assert module.classify_rows(rows) == expected
    assert module.classify_rows(list(reversed(rows))) == expected
    outputs = []
    for ordered in (rows, list(reversed(rows))):
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH)], input=json.dumps(ordered),
            text=True, capture_output=True, check=True, cwd=tmp_path,
        )
        assert completed.stderr == ""
        assert json.loads(completed.stdout) == expected
        outputs.append(completed.stdout)
    assert outputs[0] == outputs[1]


def test_target_order_and_evidence_key_order_do_not_change_output():
    # Independent ordering expectation: lexical target order within one provider.
    rows = [row({"alias_resolves": False, "target_state": "present"}, target="z.md"),
            row({"target_state": "present", "alias_resolves": False}, target="a.md")]
    result = module.classify_rows(rows)
    assert [item["target"] for item in result["rows"]] == ["a.md", "z.md"]
    assert module.classify_rows(list(reversed(rows))) == result


@pytest.mark.parametrize("payload", [
    "{", "{}", '[{"target":"docs/example.md"}]',
    '[{"provider":"alpha","target":"docs/example.md","evidence":{"alias_resolves":NaN}}]',
    '[{"provider":"alpha","provider":"beta","target":"docs/example.md"}]',
    '[{"provider":"alpha","target":"docs/example.md",'
    '"evidence":{"alias_resolves":false,"alias_resolves":true}}]',
])
def test_cli_rejects_invalid_input_without_partial_output(payload, tmp_path):
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH)], input=payload,
        text=True, capture_output=True, cwd=tmp_path,
    )
    assert completed.returncode != 0
    assert completed.stdout == ""
    assert completed.stderr == "Invalid input: expected a JSON array of read rows.\n"


@pytest.mark.parametrize("number", ["1e999", "-1e999"])
@pytest.mark.parametrize("value_template", [
    "NUMBER", '{"nested":NUMBER}', '[NUMBER]', '{"nested":[NUMBER]}',
])
def test_cli_rejects_numeric_overflow_at_any_depth(number, value_template, tmp_path):
    value = value_template.replace("NUMBER", number)
    payload = ('[{"provider":"alpha","target":"docs/example.md",'
               '"evidence":{"alias_resolves":' + value + '}}]')
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH)], input=payload,
        text=True, capture_output=True, cwd=tmp_path,
    )
    assert completed.returncode != 0
    assert completed.stdout == ""
    assert completed.stderr == "Invalid input: expected a JSON array of read rows.\n"


@pytest.mark.parametrize("number", ["1e308", "-1e308", "1e-999", "-1e-999"])
def test_cli_keeps_finite_numbers_as_invalid_evidence(number, tmp_path):
    payload = ('[{"provider":"alpha","target":"docs/example.md",'
               '"evidence":{"alias_resolves":' + number + '}}]')
    completed = subprocess.run(
        [sys.executable, str(MODULE_PATH)], input=payload,
        text=True, capture_output=True, cwd=tmp_path,
    )
    assert completed.returncode == 0
    assert completed.stderr == ""
    assert json.loads(completed.stdout) == {
        "rows": [{"provider": "alpha", "target": "docs/example.md",
                  "bucket": "unknown-needs-review", "reason_code": "UNKNOWN_NEEDS_REVIEW"}],
        "bucket_counts": {"alpha": {"unknown-needs-review": 1}},
    }


@pytest.mark.parametrize("candidate", [
    None, {}, {"provider": "", "target": "docs/example.md"},
    {"provider": "alpha", "target": None},
    {"provider": "alpha", "target": "docs/example.md", "extra": True},
])
def test_invalid_row_schema_is_rejected(candidate):
    with pytest.raises(ValueError):
        module.classify_rows([candidate])


@pytest.mark.parametrize("evidence", [None, {}, {"target_state": None}])
def test_null_and_missing_evidence_remain_unknown(evidence):
    candidate = {"provider": "alpha", "target": "docs/example.md"}
    assert module.classify_read(candidate)["bucket"] == "unknown-needs-review"
    candidate["evidence"] = evidence
    assert module.classify_read(candidate)["bucket"] == "unknown-needs-review"


def test_classifier_never_probes_target(tmp_path, monkeypatch):
    target = tmp_path / "unobserved.md"

    def forbidden(*args, **kwargs):
        raise AssertionError("target probe attempted")

    monkeypatch.setattr(Path, "exists", forbidden)
    monkeypatch.setattr(Path, "stat", forbidden)
    monkeypatch.setattr(Path, "open", forbidden)
    assert module.classify_read(row(target=str(target)))["bucket"] == "unknown-needs-review"
