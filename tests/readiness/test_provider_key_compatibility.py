"""Reader-only dual-read contract from issue #3579; display keys stay legacy.

Schema versions follow provider_row_verdict; statuses and the divergence reason
follow provider_capability_verdict / EXPECTED_DIVERGENCE_REASONS. Skill counts
are hand-counted: one canonical family, zero differences, or one differing family.
The provenance has zero commits of skew and zero hours of age (is_stale policy).
Fixtures are synthetic; YAML and rendered output live only in pytest's temp tree.
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest
import yaml

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts/readiness/build-equality-matrix.py"
spec = importlib.util.spec_from_file_location("provider_key_matrix", MODULE_PATH)
assert spec is not None and spec.loader is not None
bem = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bem)

CAPABILITIES = ("memory:read", "skills:invoke", "workflow:gates")
OTHER_PROVIDERS = ("claude", "codex", "hermes")


def _report(family):
    """Build old, replacement, split-field, or equivalent-duplicate evidence."""
    capable = {"present": True, **{cap: {"status": "present"} for cap in CAPABILITIES}}
    target = deepcopy(capable)
    target["skills:invoke"] = {
        "status": "expected_divergence", "reason": "gemini_skill_dispatch_unsupported"}
    presence = {provider: "present" for provider in OTHER_PROVIDERS}
    providers = {provider: deepcopy(capable) for provider in OTHER_PROVIDERS}
    skills = {"audited_at": "2026-10-15T00:00:00Z", "canonical_count": 1,
              "index_dangling": 0}
    if family in ("legacy", "mixed", "duplicates"):
        presence["gemini"] = "present"
        providers["gemini"] = deepcopy(target)
        skills["gemini_present"] = True
    if family in ("legacy", "duplicates"):
        skills.update(gemini_unexpected=0, gemini_expected=0)
    if family in ("replacement", "mixed", "duplicates"):
        presence["agy"] = "present"
        target["skills:invoke"]["reason"] = "agy_skill_dispatch_unsupported"
        providers["agy"] = target
        skills.update(agy_unexpected=0, agy_expected=0)
    if family in ("replacement", "duplicates"):
        skills["agy_present"] = True
    return {
        "schema_version": 4,
        "provenance": {"dirty": False, "behind_main": 0, "ahead_main": 0,
                       "origin_ref_age_h": 0},
        "dimensions": {"harness": {"providers": presence},
                       "provider_harness": {"schema_version": 1, "providers": providers},
                       "skill_currency": skills},
    }


@pytest.fixture(params=("legacy", "replacement", "mixed", "duplicates"))
def report(request):
    return _report(request.param)


def _verdict(dim, report):
    return bem.verdict_for(dim, "sample", {"sample": report}, {},
                           {"sample": {"status": "active"}}, [])


def test_legacy_and_replacement_keys_match(report):
    # Three capabilities: two present, one explicitly allowlisted divergence.
    assert [_verdict(f"harness:gemini:{cap}", report) for cap in CAPABILITIES] == [
        "PARITY", "EXPECTED-DIVERGENCE", "PARITY"]
    assert _verdict("skill_currency", report) == "SKILLS-CURRENT"
    assert bem.extract_value("harness", report) == (
        '{"claude": "present", "codex": "present", "gemini": "present", "hermes": "present"}')
    for provider in OTHER_PROVIDERS:
        for cap in CAPABILITIES:
            assert _verdict(f"harness:{provider}:{cap}", report) == "PARITY"


@pytest.mark.parametrize("field,value,verdict", [
    ("unexpected", 1, "SKILLS-DRIFTED"),
    ("expected", 1, "EXPECTED-DIVERGENCE"),
    ("unexpected", "invalid", "MISSING-EVIDENCE"),
    ("unexpected", True, "MISSING-EVIDENCE"),
])
def test_replacement_skill_counts_use_existing_policy(field, value, verdict):
    report = _report("replacement")
    report["dimensions"]["skill_currency"][f"agy_{field}"] = value
    assert bem.skill_currency_verdict(report) == verdict


@pytest.mark.parametrize("field,value", [
    ("present", False), ("unexpected", 1), ("expected", 1),
    ("unexpected", False), ("expected", False), ("present", 1),
    ("unexpected", None),
])
def test_conflicting_key_families_are_not_conforming(field, value):
    report = _report("duplicates")
    report["dimensions"]["skill_currency"][f"agy_{field}"] = value
    assert bem.skill_currency_verdict(report) == "MISSING-EVIDENCE"
    assert _verdict("skill_currency", report) == "MISSING-EVIDENCE"
    assert _verdict("harness:codex:memory:read", report) == "PARITY"


@pytest.mark.parametrize("change", ["presence", "capability", "reason", "type", "missing"])
def test_conflicting_provider_records_are_missing_evidence(change):
    report = _report("duplicates")
    replacement = report["dimensions"]["provider_harness"]["providers"]["agy"]
    if change == "presence":
        replacement["present"] = False
    elif change == "capability":
        replacement["memory:read"]["status"] = "absent"
    elif change == "reason":
        replacement["skills:invoke"]["reason"] = "unrecognized"
    elif change == "type":
        replacement["present"] = 1
    else:
        del replacement["workflow:gates"]
    for cap in CAPABILITIES:
        assert _verdict(f"harness:gemini:{cap}", report) == "MISSING-EVIDENCE"
        assert _verdict(f"harness:codex:{cap}", report) == "PARITY"


def test_conflicting_presence_cannot_join_uniform_consensus():
    report = _report("duplicates")
    report["dimensions"]["harness"]["providers"]["agy"] = "absent"
    assert bem.extract_value("harness", report) is None
    reports = {"sample": report, "first": _report("legacy"), "second": _report("replacement")}
    roster = {key: {"status": "active"} for key in reports}
    assert bem.verdict_for("harness", "sample", reports, {}, roster, []) == "MISSING-EVIDENCE"
    assert bem.verdict_for("harness", "first", reports, {}, roster, []) == "EQUAL"


def test_normalization_preserves_input(report):
    original = deepcopy(report)
    test_legacy_and_replacement_keys_match(report)
    assert report == original


def test_conflict_detection_preserves_input():
    report = _report("duplicates")
    report["dimensions"]["skill_currency"]["agy_unexpected"] = 1
    report["dimensions"]["harness"]["providers"]["agy"] = "absent"
    report["dimensions"]["provider_harness"]["providers"]["agy"]["present"] = False
    original = deepcopy(report)
    for dim in ("skill_currency", "harness", "harness:gemini:memory:read"):
        assert _verdict(dim, report) == "MISSING-EVIDENCE"
    assert report == original


def test_missing_optional_skill_fields_keep_legacy_behavior():
    report = _report("replacement")
    skills = report["dimensions"]["skill_currency"]
    del skills["agy_present"]
    del skills["agy_unexpected"]
    del skills["agy_expected"]
    assert bem.skill_currency_verdict(report) == "SKILLS-CURRENT"


@pytest.mark.parametrize("present,expected", [(False, "ABSENT"), (True, "PARITY")])
def test_replacement_provider_presence(present, expected):
    report = _report("replacement")
    report["dimensions"]["provider_harness"]["providers"]["agy"]["present"] = present
    assert _verdict("harness:gemini:memory:read", report) == expected


def test_unrecognized_replacement_reason_is_not_allowlisted():
    report = _report("replacement")
    record = report["dimensions"]["provider_harness"]["providers"]["agy"]
    record["skills:invoke"]["reason"] = "unrecognized"
    assert _verdict("harness:gemini:skills:invoke", report) == "DIVERGES"


def test_yaml_reports_render_with_legacy_display_keys(tmp_path, monkeypatch):
    state = tmp_path / "state"
    state.mkdir()
    config = tmp_path / "config.yaml"
    # Hand-counted fixture roster: one report for each of the four key layouts.
    layouts = ("legacy", "replacement", "mixed", "duplicates")
    roster = {key: {"status": "active"} for key in layouts}
    config.write_text(yaml.safe_dump({"workstations": roster, "tier1_repos": []}))
    for key in layouts:
        (state / f"equality-{key}.yaml").write_text(yaml.safe_dump(_report("legacy")))
    monkeypatch.setattr(bem, "STATE", state)
    monkeypatch.setattr(bem, "CONFIG", config)
    monkeypatch.setattr(bem, "REPORTS", tmp_path / "reports")
    monkeypatch.setattr(bem.sys, "argv", ["build-equality-matrix.py"])
    bem.main()
    output = tmp_path / "reports" / "machine-equality-matrix.html"
    legacy_html = output.read_text()
    for key in layouts:
        (state / f"equality-{key}.yaml").write_text(yaml.safe_dump(_report(key)))
    bem.main()
    html = output.read_text()
    assert html == legacy_html
    assert "harness:agy:" not in html
    for cap in CAPABILITIES:
        assert f"<th>harness:gemini:{cap}</th>" in html
    for key in layouts:
        assert _verdict("skill_currency", bem.load_reports()[key]) == "SKILLS-CURRENT"
        assert _verdict("harness:gemini:skills:invoke", bem.load_reports()[key]) == "EXPECTED-DIVERGENCE"
