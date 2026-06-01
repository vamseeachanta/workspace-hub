import json
from pathlib import Path

from src.deckhand.runtime import handle


def config(rate_limits=None):
    return {
        "policy": {
            "destructive_ops": ["repo_delete"],
            "action_policy_defaults": {
                "diff_risk_gate": {
                    "enabled": True,
                    "mass_deletion_file_threshold": 3,
                }
            },
            "audit": {
                "redact": [
                    "repo_names",
                    "pr_urls",
                    "branch_names",
                    "operator_ids",
                    "error_specifics",
                ]
            },
            "kill_switches": {
                "disable_all_writes": False,
                "disabled_scopes": [],
                "disabled_operators": [],
                "disabled_platforms": [],
            },
            "elevation": {"approvers": ["internal-admin"]},
            "rate_limits": rate_limits
            or {
                "per_operator_writes_per_hour": 2,
                "per_scope_writes_per_hour": 3,
                "duplicate_request_window_seconds": 10,
            },
        },
        "scopes": {
            "scopes": {
                "acma": {
                    "sensitivity": "private",
                    "repositories": ["owner/acma"],
                    "operators": ["tg-100"],
                    "channel_repo_bindings": [],
                }
            },
            "origin_bound_default": {"enabled": False},
        },
    }


def request(**overrides):
    base = {
        "operator_id": "tg-100",
        "platform": "telegram",
        "scope_name": "acma",
        "target_repos": ["owner/acma"],
        "action_class": "write",
        "origin": {"is_dm": True, "channel_id": "dm-100"},
        "change": {"files_deleted": 0, "touches_protected": False},
        "elevation_token": None,
    }
    base.update(overrides)
    return base


class SequenceClock:
    def __init__(self, *values: str):
        self.values = list(values)

    def __call__(self) -> str:
        if len(self.values) == 1:
            return self.values[0]
        return self.values.pop(0)


def read_ndjson(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_allow_path_calls_executor_once_and_persists_pending_then_final(tmp_path):
    audit_path = tmp_path / "audit.ndjson"
    calls = []

    def executor(received):
        calls.append(received)
        return {
            "ok": True,
            "pr_url": "https://github.com/owner/acma/pull/1",
            "branch": "feature/secret-client",
        }

    outcome = handle(
        request(),
        config=config(),
        executor=executor,
        clock=SequenceClock("2026-06-01T12:00:00Z"),
        rate_store={},
        audit_path=audit_path,
    )

    assert calls == [request()]
    assert outcome["executed"] is True
    assert outcome["decision"]["allow"] is True
    assert outcome["result"] == {"ok": True}
    assert "pr_url" not in json.dumps(outcome, sort_keys=True)
    records = read_ndjson(audit_path)
    assert [record["status"] for record in records] == ["PENDING", "FINAL"]
    assert [record["decision"] for record in records] == ["ALLOW", "ALLOW"]
    assert {record["decision_id"] for record in records} == {outcome["decision_id"]}
    assert records[1]["result"] == {"ok": True}


def test_deny_path_never_calls_executor_and_persists_one_deny_record(tmp_path):
    audit_path = tmp_path / "audit.ndjson"

    def executor(_received):
        raise AssertionError("executor should not be called")

    outcome = handle(
        request(target_repos=["owner/not-in-scope"]),
        config=config(),
        executor=executor,
        clock=SequenceClock("2026-06-01T12:00:00Z"),
        rate_store={},
        audit_path=audit_path,
    )

    assert outcome["executed"] is False
    assert outcome["decision"]["allow"] is False
    assert "repo outside scope allowlist" in outcome["decision"]["reason"]
    records = read_ndjson(audit_path)
    assert len(records) == 1
    assert records[0]["status"] == "DENY"
    assert records[0]["decision"] == "DENY"


def test_rate_limit_exceeded_never_calls_executor_and_persists_deny_rate(tmp_path):
    audit_path = tmp_path / "audit.ndjson"
    rate_store = {
        "write_events": {
            "operator:tg-100": ["2026-06-01T12:00:00Z", "2026-06-01T12:10:00Z"],
            "scope:acma": [],
        },
        "duplicate_requests": {},
    }

    def executor(_received):
        raise AssertionError("executor should not be called")

    outcome = handle(
        request(),
        config=config(rate_limits={"per_operator_writes_per_hour": 2}),
        executor=executor,
        clock=SequenceClock("2026-06-01T12:30:00Z"),
        rate_store=rate_store,
        audit_path=audit_path,
    )

    assert outcome["executed"] is False
    assert outcome["decision"]["allow"] is False
    assert outcome["decision"]["reason"] == "rate limit exceeded: operator writes per hour"
    records = read_ndjson(audit_path)
    assert len(records) == 1
    assert records[0]["status"] == "DENY-rate"
    assert records[0]["reason"] == "rate limit exceeded: operator writes per hour"


def test_executor_exception_persists_final_error_and_returns_error_outcome(tmp_path):
    audit_path = tmp_path / "audit.ndjson"

    def executor(_received):
        raise RuntimeError("secret client detail should not escape")

    outcome = handle(
        request(),
        config=config(),
        executor=executor,
        clock=SequenceClock("2026-06-01T12:00:00Z"),
        rate_store={},
        audit_path=audit_path,
    )

    assert outcome["executed"] is False
    assert outcome["error"] == {"type": "RuntimeError"}
    assert "secret client detail" not in json.dumps(outcome, sort_keys=True)
    records = read_ndjson(audit_path)
    assert [record["status"] for record in records] == ["PENDING", "FINAL"]
    assert records[1]["error"] == {"type": "RuntimeError"}
    assert {record["decision_id"] for record in records} == {outcome["decision_id"]}


def test_duplicate_request_window_suppresses_repeated_identical_request(tmp_path):
    audit_path = tmp_path / "audit.ndjson"
    calls = []
    rate_store = {}
    first_clock = SequenceClock("2026-06-01T12:00:00Z")
    second_clock = SequenceClock("2026-06-01T12:00:05Z")

    def executor(received):
        calls.append(received)
        return {"ok": True}

    first = handle(
        request(),
        config=config(),
        executor=executor,
        clock=first_clock,
        rate_store=rate_store,
        audit_path=audit_path,
    )
    second = handle(
        request(),
        config=config(),
        executor=executor,
        clock=second_clock,
        rate_store=rate_store,
        audit_path=audit_path,
    )

    assert first["executed"] is True
    assert second["executed"] is False
    assert second["decision"]["reason"] == "duplicate request suppressed"
    assert calls == [request()]
    records = read_ndjson(audit_path)
    assert [record["status"] for record in records] == ["PENDING", "FINAL", "DENY-rate"]
    assert records[-1]["reason"] == "duplicate request suppressed"
