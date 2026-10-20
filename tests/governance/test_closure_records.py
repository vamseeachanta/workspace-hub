"""Draft expectations follow issue-closing-procedure sections A.4, C.3 and C.4.

All issue identities and body text below are synthetic. Expected decisions are
derived by hand from the cited rules, independently of the draft builder.
"""
from __future__ import annotations

import csv
import importlib
import io
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/governance"))
records = importlib.import_module("closure_records")


def issue(number, **fields):
    return {"repository_slug": "example/tools", "number": number,
            "state": "closed", "state_reason": "DUPLICATE", **fields}


def packet(**fields):
    return {"issues": [], "successors": {}, "recoveries": [],
            "retired": [], **fields}


def test_open_successor_and_missing_successor():
    """A.4: open successor routes one record; no successor requires reopening."""
    data = packet(issues=[issue(1), issue(2, state="open"), issue(3)],
                  successors={"example/tools#1": "example/tools#2"})
    result = records.build_drafts(data)
    assert [(r["issue"], r["successor"], r["status"]) for r in result["successors"]] == [
        ("example/tools#1", "example/tools#2", "open"),
        ("example/tools#3", "none: reopen", "unresolved"),
    ]
    assert len(result["decisions"]) == 2


def test_closed_completed_alone_is_not_proper_closure():
    """A.4 requires evidence, so a COMPLETED flag alone cannot qualify."""
    result = records.build_drafts(packet(
        issues=[issue(1), issue(2, state_reason="COMPLETED")],
        successors={"example/tools#1": "example/tools#2"}))
    assert result["successors"][0]["successor"] == "none: reopen"


def test_properly_closed_successor_requires_all_checker_rules():
    """A/B/E: delivered scope, reviewed head, paths and test evidence agree."""
    delivered = issue(
        2, state_reason="COMPLETED", closer_type="merged_pr", body="- [x] Delivered",
        comments=[{"closing_evidence": True, "body":
                   "Merged PR #4 at abcdef1. Path scripts/example.py. Tests: pytest - 1 passed."}],
        pull_requests=[{"number": 4, "merged": True, "head_sha": "abcdef1",
                        "review_head_sha": "abcdef1", "reviewer": "reviewer",
                        "merge_commit_sha": "abcdef1"}],
        default_branch_shas=["abcdef1"], paths_at_refs={"scripts/example.py": True},
        body_edited_after_close=False)
    result = records.build_drafts(packet(issues=[issue(1), delivered],
                                        successors={"example/tools#1": "example/tools#2"}))
    assert result["successors"][0]["status"] == "properly closed"


def test_reopened_successor_needs_scope_assessment():
    result = records.build_drafts(packet(
        issues=[issue(1), issue(2, state="open", reopened=True)],
        successors={"example/tools#1": "example/tools#2"}))
    assert result["successors"][0]["status"] == "unresolved"


def test_self_reference_and_cycles_do_not_qualify():
    """A.4: a cycle never reaches an open or evidenced completed record."""
    for mapping in ({"example/tools#1": "example/tools#1"},
                    {"example/tools#1": "example/tools#2",
                     "example/tools#2": "example/tools#1"}):
        result = records.build_drafts(packet(issues=[issue(1), issue(2)], successors=mapping))
        assert all(row["successor"] == "none: reopen" for row in result["successors"])


def test_cross_repository_number_collision_is_not_a_successor():
    result = records.build_drafts(packet(
        issues=[issue(1), issue(2, repository_slug="example/other", state="open")],
        successors={"example/tools#1": "example/tools#2"}))
    assert result["successors"][0]["successor"] == "none: reopen"


def test_recovery_never_turns_edit_summary_into_original_body():
    """C.4: only a separately verified original can populate a restore draft."""
    result = records.build_drafts(packet(issues=[issue(1)], recoveries=[{
        "issue": "example/tools#1", "edit_summary": "possibly original",
        "replacing_scope": "Separate replacement work"}]))
    recovery = result["recoveries"][0]
    assert recovery["status"] == "NOT_EVALUATED"
    assert recovery["restore_body"] is None
    assert "Separate replacement work" in recovery["new_issue_body"]


def test_verified_original_is_preserved_exactly_and_scopes_separate():
    original = "Original scope.\r\n- [ ] Keep this criterion.\r\n"
    result = records.build_drafts(packet(issues=[issue(1)], recoveries=[{
        "issue": "example/tools#1", "original_body": original,
        "original_source": "verified archival revision",
        "original_verified": True, "replacing_scope": "Replacement scope."}]))
    assert result["recoveries"][0]["restore_body"] == original
    assert "Replacement scope." not in result["recoveries"][0]["restore_body"]
    assert len(result["decisions"]) == 3  # successor, restore, separate replacement


def test_import_is_proposal_not_delivery_claim():
    """C.3/E.9: elapsed time = 30 s, below the procedure's 60 s limit."""
    result = records.build_drafts(packet(issues=[issue(
        1, state_reason="COMPLETED", created_at="2026-01-01T00:00:00Z",
        closed_at="2026-01-01T00:00:30Z", comments=[])]))
    assert result["imports"][0]["proposed_label"] == "closure:unverified"
    assert "not established" in result["imports"][0]["draft_comment"]


def test_delivered_import_is_not_proposed_as_undelivered(monkeypatch):
    monkeypatch.setattr(records.checker, "evidence_status", lambda item: (True, True, []))
    result = records.build_drafts(packet(issues=[issue(
        1, state_reason="COMPLETED", created_at="2026-01-01T00:00:00Z",
        closed_at="2026-01-01T00:00:30Z", comments=[])]))
    assert result["imports"] == []


def test_retired_issue_requires_retirement_reference_or_move_target():
    result = records.build_drafts(packet(issues=[issue(1, state="open")], retired=[{
        "issue": "example/tools#1", "action": "close", "reason": "Tool retired"}]))
    assert result["retired"][0]["status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("entry", [
    {"action": "close", "retirement_reference": "example/tools#2"},
    {"action": "move", "destination": "example/tools#2"},
])
def test_retired_issue_has_reason_and_resolving_reference(entry):
    result = records.build_drafts(packet(
        issues=[issue(1, state="open"), issue(2, state="open")],
        retired=[{"issue": "example/tools#1", "reason": "Scope retained elsewhere", **entry}]))
    assert result["retired"][0]["status"] == "proposed"


def test_duplicate_identities_are_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        records.build_drafts(packet(issues=[issue(1), issue(1)]))


def test_live_validation_deduplicates_and_rejects_pull_requests():
    calls = []

    def read(repository, number):
        calls.append((repository, number))
        return {"number": number, "pull_request": {"url": "ignored"}}

    result = records.verify_references(["example/tools#1", "example/tools#1"], read)
    assert calls == [("example/tools", 1)]
    assert result["example/tools#1"]["status"] == "FAIL"


def test_live_validation_failure_is_explicit():
    def read(repository, number):
        raise RuntimeError("API unavailable")

    result = records.verify_references(["example/tools#1"], read)
    assert result["example/tools#1"]["status"] == "NOT_EVALUATED"


def test_all_embedded_issue_references_are_enumerated():
    result = records.build_drafts(packet(issues=[issue(
        1, body="Related #8 and example/other#9.")], recoveries=[{
            "issue": "example/tools#1", "original_body": "Follow #10.",
            "original_source": "verified revision", "original_verified": True}]))
    assert result["references"] == ["example/other#9", "example/tools#1",
                                     "example/tools#10", "example/tools#8"]


def test_live_validation_checks_canonical_identity():
    result = records.verify_references(["example/tools#1"], lambda repo, num: {
        "number": num, "state": "open", "html_url": "https://github.com/example/other/issues/1"})
    assert result["example/tools#1"]["status"] == "FAIL"


def test_unknown_state_does_not_qualify_as_open():
    result = records.build_drafts(packet(issues=[issue(1), issue(2, state="unknown")],
                                        successors={"example/tools#1": "example/tools#2"}))
    assert result["successors"][0]["status"] == "unresolved"


def test_csv_quotes_multiline_draft_text():
    row = {"issue": "example/tools#1", "successor": "none: reopen",
           "status": "unresolved", "draft_comment": "First, line\nSecond line"}
    output = io.StringIO()
    records.write_successor_csv([row], output)
    assert list(csv.DictReader(io.StringIO(output.getvalue()))) == [row]


def test_cli_is_offline_by_default_and_prints_drafts(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(packet())))
    assert records.main([]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["draft_only"] is True
    assert result["reference_validation"] == "NOT_EVALUATED"


def test_documented_example_matches_independent_answers():
    """Hand count from the procedure: 1 successor + 1 import + 2 recovery + 1 move."""
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / "docs/governance/examples/closure-records.json").read_text())
    result = records.build_drafts(data)
    assert result["successors"][0]["successor"] == "example/tools#2"
    assert len(result["imports"]) == 1
    assert result["recoveries"][0]["restore_body"] == data["recoveries"][0]["original_body"]
    assert result["retired"][0]["status"] == "proposed"
    assert len(result["decisions"]) == 5
    expected_csv = (root / "docs/governance/examples/closure-successors.csv").read_text()
    output = io.StringIO()
    records.write_successor_csv(result["successors"], output)
    assert output.getvalue() == expected_csv


def test_cli_live_reads_are_only_get_requests(monkeypatch, capsys):
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        return type("Response", (), {"returncode": 0, "stdout": json.dumps({
            "number": 1, "state": "closed", "html_url": "https://github.com/example/tools/issues/1"})})()

    monkeypatch.setattr(records.subprocess, "run", run)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(packet(issues=[issue(1)]))))
    assert records.main(["--verify-live"]) == 0
    assert calls == [["gh", "api", "--method", "GET", "repos/example/tools/issues/1"]]
    assert json.loads(capsys.readouterr().out)["reference_validation"]["example/tools#1"]["status"] == "PASS"


def test_cli_returns_failure_when_reference_cannot_be_verified(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(packet(issues=[issue(1)]))))
    monkeypatch.setattr(records, "verify_references", lambda refs: {
        "example/tools#1": {"status": "NOT_EVALUATED", "state": None}})
    assert records.main(["--verify-live"]) == 1
    assert json.loads(capsys.readouterr().out)["draft_only"] is True


def test_reference_mismatch_fails_without_leaking_response():
    result = records.verify_references(["example/tools#1"], lambda repo, num: {
        "number": 2, "html_url": "https://github.com/example/tools/issues/2"})
    assert result == {"example/tools#1": {"status": "FAIL", "state": None}}


def test_api_retries_only_transient_server_errors(monkeypatch):
    """Operational retry counts and delays follow the supplied server-error rule."""
    calls, delays = [], []

    def run(args, **kwargs):
        calls.append(args)
        if len(calls) == 1:
            return type("Response", (), {"returncode": 1, "stderr": "HTTP 503"})()
        return type("Response", (), {"returncode": 0, "stdout": '{"number":1}'})()

    monkeypatch.setattr(records.subprocess, "run", run)
    monkeypatch.setattr(records.time, "sleep", delays.append)
    assert records.read_issue("example/tools", 1) == {"number": 1}
    assert len(calls) == 2
    assert delays == [60]
