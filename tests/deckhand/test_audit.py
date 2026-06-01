import json
from pathlib import Path

import pytest

from src.deckhand.audit import append_raw, redacted_summary, render_summary_html


def fixed_clock() -> str:
    return "2026-06-01T12:00:00Z"


def sample_record(**overrides):
    record = {
        "ts_placeholder": "PENDING_TS",
        "operator": "tg-sensitive-operator",
        "platform": "telegram",
        "scope": "client-alpha",
        "scope_sensitivity": "private",
        "repos": ["client-alpha/private-repo"],
        "pr_url": "https://github.com/client-alpha/private-repo/pull/7",
        "branch": "feature/client-alpha-secret",
        "action_class": "write",
        "decision": "DENY",
        "reason": "repo outside scope allowlist: client-alpha/private-repo",
        "error": "trace includes client-alpha/private-repo",
    }
    record.update(overrides)
    return record


def read_ndjson(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_append_raw_creates_parent_file_and_appends_one_json_line(tmp_path):
    path = tmp_path / "audit" / "decisions.ndjson"

    persisted = append_raw(sample_record(decision="ALLOW", reason="allowed"), path=path, clock=fixed_clock)

    assert path.exists()
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    decoded = json.loads(lines[0])
    assert decoded == persisted
    assert decoded["ts"] == "2026-06-01T12:00:00Z"
    assert isinstance(decoded["decision_id"], str)
    assert decoded["decision_id"]
    assert "ts_placeholder" not in decoded
    assert decoded["operator"] == "tg-sensitive-operator"
    assert decoded["repos"] == ["client-alpha/private-repo"]


def test_append_raw_never_truncates_existing_lines(tmp_path):
    path = tmp_path / "decisions.ndjson"
    path.write_text('{"existing": true}\n', encoding="utf-8")

    append_raw(sample_record(decision="ALLOW", reason="allowed"), path=path, clock=fixed_clock)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"existing": True}
    assert json.loads(lines[1])["decision"] == "ALLOW"


def test_pending_before_final_flow_uses_same_decision_id_and_survives_crash_gap(tmp_path):
    path = tmp_path / "decisions.ndjson"
    decision_id = "decision-123"

    pending = append_raw(
        sample_record(status="PENDING"),
        path=path,
        clock=fixed_clock,
        decision_id=decision_id,
    )

    assert read_ndjson(path) == [pending]
    assert pending["status"] == "PENDING"
    assert pending["decision_id"] == decision_id

    final = append_raw(
        sample_record(status="FINAL", decision="ALLOW", reason="allowed"),
        path=path,
        clock=fixed_clock,
        decision_id=decision_id,
    )

    records = read_ndjson(path)
    assert records == [pending, final]
    assert {record["status"] for record in records} == {"PENDING", "FINAL"}
    assert {record["decision_id"] for record in records} == {decision_id}


def test_raw_store_preserves_sensitive_full_fidelity_fields(tmp_path):
    path = tmp_path / "decisions.ndjson"

    append_raw(sample_record(), path=path, clock=fixed_clock, decision_id="decision-raw")

    raw = read_ndjson(path)[0]
    assert raw["operator"] == "tg-sensitive-operator"
    assert raw["scope"] == "client-alpha"
    assert raw["repos"] == ["client-alpha/private-repo"]
    assert raw["pr_url"] == "https://github.com/client-alpha/private-repo/pull/7"
    assert raw["branch"] == "feature/client-alpha-secret"
    assert raw["reason"] == "repo outside scope allowlist: client-alpha/private-repo"


def test_redacted_summary_aggregates_without_sensitive_fields_or_values():
    sensitive_values = [
        "tg-sensitive-operator",
        "client-alpha",
        "client-alpha/private-repo",
        "https://github.com/client-alpha/private-repo/pull/7",
        "feature/client-alpha-secret",
        "repo outside scope allowlist: client-alpha/private-repo",
        "trace includes client-alpha/private-repo",
    ]
    records = [
        sample_record(),
        sample_record(
            operator="tg-other",
            scope="client-beta",
            scope_sensitivity="internal",
            repos=["client-beta/repo"],
            pr_url="https://github.com/client-beta/repo/pull/8",
            branch="fix/client-beta",
            decision="ALLOW",
            reason="allowed",
            error="client-beta detail",
        ),
    ]
    policy = {"audit": {"redact": ["repo_names", "pr_urls", "branch_names", "operator_ids", "error_specifics"]}}

    summary = redacted_summary(records, policy=policy)

    assert summary == {
        "total": 2,
        "allow": 1,
        "deny": 1,
        "deny_reasons": {"redacted": 1},
        "sensitivity_counts": {
            "private": {"total": 1, "allow": 0, "deny": 1},
            "internal": {"total": 1, "allow": 1, "deny": 0},
        },
    }
    summary_text = json.dumps(summary, sort_keys=True)
    for value in sensitive_values:
        assert value not in summary_text
    for forbidden_key in ("operator", "repos", "pr_url", "branch", "error"):
        assert forbidden_key not in summary_text


def test_redacted_summary_can_bucket_safe_deny_reasons_when_error_specifics_not_redacted():
    records = [
        sample_record(reason="unknown operator"),
        sample_record(reason="unknown operator"),
        sample_record(reason="writes disabled"),
    ]

    summary = redacted_summary(records, policy={"audit": {"redact": []}})

    assert summary["deny_reasons"] == {"unknown operator": 2, "writes disabled": 1}


def test_render_summary_html_returns_self_contained_escaped_html():
    summary = {
        "total": 1,
        "allow": 0,
        "deny": 1,
        "deny_reasons": {"redacted <reason>": 1},
        "sensitivity_counts": {"private": {"total": 1, "allow": 0, "deny": 1}},
    }

    html = render_summary_html(summary)

    assert html.startswith("<!doctype html>")
    assert "<html" in html
    assert "</html>" in html
    assert "redacted &lt;reason&gt;" in html
    assert "<script" not in html.lower()


def test_append_raw_fails_closed_for_unwritable_path_under_file(tmp_path):
    parent_file = tmp_path / "not-a-directory"
    parent_file.write_text("blocking file", encoding="utf-8")

    with pytest.raises(OSError, match="failed to append audit record"):
        append_raw(sample_record(), path=parent_file / "decisions.ndjson", clock=fixed_clock)
