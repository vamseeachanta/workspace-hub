import copy
import json
from pathlib import Path

import yaml

from src.deckhand.pipeline import dry_run_executor, evaluate, load_config


REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_CONFIG_DIR = REPO_ROOT / "config" / "deckhand"


def clock() -> str:
    return "2026-06-01T12:00:00Z"


def read_ndjson(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def real_context(**overrides):
    base = {
        "operator_id": "tg-100",
        "platform": "telegram",
        "scope_name": "acma",
        "repo": "vamseeachanta/llm-wiki-acma",
        "target_repos": ["vamseeachanta/llm-wiki-acma"],
        "origin": {"is_dm": True, "channel_id": "dm-100"},
        "change": {"files_deleted": 0, "touches_protected": False},
    }
    base.update(overrides)
    return base


def authorized_real_config() -> dict:
    config = copy.deepcopy(load_config(REAL_CONFIG_DIR))
    config["scopes"]["scopes"]["acma"]["operators"] = ["tg-100"]
    return config


def test_real_committed_config_is_fail_closed_for_writes_with_empty_operators(tmp_path):
    config = load_config(REAL_CONFIG_DIR)
    assert {name: scope["operators"] for name, scope in config["scopes"]["scopes"].items()} == {
        "acma": [],
        "doris": [],
        "ecosystem": [],
    }

    audit_path = tmp_path / "audit.ndjson"
    outcome = evaluate(
        "git push origin main",
        cwd=REPO_ROOT,
        request_context=real_context(),
        config_dir=REAL_CONFIG_DIR,
        clock=clock,
        rate_store={},
        audit_path=audit_path,
    )

    assert outcome["allow"] is False
    assert outcome["dry_run"] is True
    assert outcome["would_execute"] is None
    assert outcome["reason"] == "unknown operator"
    records = read_ndjson(audit_path)
    assert [record["status"] for record in records] == ["DENY"]
    assert records[0]["decision"] == "DENY"


def test_authorized_real_config_allows_write_through_dry_run_and_audits_pending_final(tmp_path):
    audit_path = tmp_path / "audit.ndjson"

    outcome = evaluate(
        "git push origin main",
        cwd=REPO_ROOT,
        request_context=real_context(),
        config_dir=authorized_real_config(),
        clock=clock,
        rate_store={},
        audit_path=audit_path,
    )

    assert outcome["allow"] is True
    assert outcome["reason"] == "allowed"
    assert outcome["dry_run"] is True
    assert outcome["would_execute"] == {"action_count": 1, "git_or_gh": True, "write": True}
    assert outcome["audit_decision_id"]
    records = read_ndjson(audit_path)
    assert [record["status"] for record in records] == ["PENDING", "FINAL"]
    assert [record["decision"] for record in records] == ["ALLOW", "ALLOW"]
    assert {record["decision_id"] for record in records} == {outcome["audit_decision_id"]}
    assert records[1]["result"]["would_execute"] == outcome["would_execute"]


def test_destructive_commands_deny_even_when_operator_is_authorized(tmp_path):
    audit_path = tmp_path / "audit.ndjson"
    config = authorized_real_config()

    for command in ["git push --force", "gh api repos/o/r/git/refs/heads/main -X DELETE"]:
        outcome = evaluate(
            command,
            cwd=REPO_ROOT,
            request_context=real_context(),
            config_dir=config,
            clock=clock,
            rate_store={},
            audit_path=audit_path,
        )

        assert outcome["allow"] is False
        assert outcome["would_execute"] is None

    records = read_ndjson(audit_path)
    assert [record["status"] for record in records] == ["DENY", "DENY"]
    assert all(record["decision"] == "DENY" for record in records)


def test_suspicious_command_denies_and_audits_deny(tmp_path):
    audit_path = tmp_path / "audit.ndjson"

    outcome = evaluate(
        "git push $F",
        cwd=REPO_ROOT,
        request_context=real_context(),
        config_dir=authorized_real_config(),
        clock=clock,
        rate_store={},
        audit_path=audit_path,
    )

    assert outcome["allow"] is False
    assert "fail-closed: suspicious" in outcome["reason"]
    assert outcome["would_execute"] is None
    records = read_ndjson(audit_path)
    assert [record["status"] for record in records] == ["DENY"]
    assert records[0]["action_class"] == "unparseable_suspicious"


def test_custom_dry_run_executor_spy_is_called_without_real_git_or_gh_execution(tmp_path):
    audit_path = tmp_path / "audit.ndjson"
    calls = []

    def spy_executor(request):
        calls.append(request)
        return {"dry_run": True, "would_execute": {"action_count": 99, "git_or_gh": True, "write": True}}

    outcome = evaluate(
        "git push origin main",
        cwd=REPO_ROOT,
        request_context=real_context(),
        config_dir=authorized_real_config(),
        executor=spy_executor,
        clock=clock,
        rate_store={},
        audit_path=audit_path,
    )

    assert len(calls) == 1
    assert calls[0]["action_class"] == "write"
    assert calls[0]["target_repos"] == ["vamseeachanta/llm-wiki-acma"]
    assert outcome["dry_run"] is True
    assert outcome["would_execute"] == {"action_count": 99, "git_or_gh": True, "write": True}


def test_dry_run_executor_returns_marker_and_does_not_require_subprocess():
    result = dry_run_executor(
        {
            "action_class": "write",
            "actions": [{"tool": "git", "action_class": "write", "argv": ["git", "push"]}],
        }
    )

    assert result == {"dry_run": True, "would_execute": {"action_count": 1, "git_or_gh": True, "write": True}}


def test_load_config_accepts_relative_config_dir_from_repo_root():
    config = load_config("config/deckhand", repo_root=REPO_ROOT)

    assert config["policy"]["schema_version"] == 1
    assert yaml.safe_load((REAL_CONFIG_DIR / "scopes.yml").read_text(encoding="utf-8")) == config["scopes"]
