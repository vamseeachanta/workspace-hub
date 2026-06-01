from pathlib import Path

import pytest

from src.deckhand import decide


def write_config(
    tmp_path: Path,
    *,
    policy_overrides: str = "",
    scope_overrides: str = "",
    acma_repository_flags: str = "      owner/acma-archive: { read_only: true }\n",
) -> Path:
    config_dir = tmp_path / "deckhand"
    config_dir.mkdir(exist_ok=True)
    (config_dir / "policy.yml").write_text(
        f"""
schema_version: 1
fail_closed: true
destructive_ops:
  - repo_delete
  - branch_delete
  - tag_delete
  - release_delete
  - force_push
  - reset_hard
  - git_clean
action_policy_defaults:
  diff_risk_gate:
    mass_deletion_file_threshold: 3
reply_clearance:
  full_detail_requires: [dm, cleared_channel]
identity:
  require_stable_platform_id: true
audit:
  record_allows: true
  record_denies: true
kill_switches:
  disable_all_writes: false
  disable_external_operators: false
  disabled_scopes: []
  disabled_operators: []
  disabled_platforms: []
elevation:
  required_for: [protected_paths, mass_deletion]
  approvers: [internal-admin]
  grant_ttl_seconds: 3600
{policy_overrides}
""",
        encoding="utf-8",
    )
    (config_dir / "scopes.yml").write_text(
        f"""
schema_version: 2
scopes:
  acma:
    sensitivity: private
    permission: write
    pat_env: DECKHAND_PAT_ACMA
    repositories:
      - owner/acma
      - owner/acma-archive
    repository_flags:
{acma_repository_flags}    operators: [tg-100, internal-admin]
    channel_repo_bindings:
      - platform: telegram
        channel_id: acma-room
        repo: owner/acma
  doris:
    sensitivity: private
    permission: write
    pat_env: DECKHAND_PAT_DORIS
    repositories:
      - owner/doris
    operators: [tg-200]
    channel_repo_bindings: []
  ecosystem:
    sensitivity: internal
    permission: write
    pat_env: DECKHAND_PAT_ECOSYSTEM
    repositories:
      - owner/ecosystem
    operators: [internal-admin]
    external_disabled: true
    channel_repo_bindings: []
origin_bound_default:
  enabled: true
  resolve_from: channel_repo_binding
  permission: write
  destructive_denied: true
  require_containment: true
poc_external_scope_allowlist: [acma, doris]
{scope_overrides}
""",
        encoding="utf-8",
    )
    return config_dir


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


def assert_denied(decision, reason_fragment: str) -> None:
    assert decision["allow"] is False
    assert reason_fragment in decision["reason"]
    assert decision["audit"]["decision"] == "DENY"
    assert decision["audit"]["reason"] == decision["reason"]


def test_allows_named_scope_write_when_operator_repo_and_action_are_authorized(tmp_path):
    decision = decide(request(), config=write_config(tmp_path))

    assert decision["allow"] is True
    assert decision["reason"] == "allowed"
    assert decision["scope_resolved"] == "acma"
    assert decision["reply_visibility"] == "full"
    assert decision["audit"] == {
        "ts_placeholder": "PENDING_TS",
        "operator": "tg-100",
        "platform": "telegram",
        "scope": "acma",
        "repos": ["owner/acma"],
        "action_class": "write",
        "decision": "ALLOW",
        "reason": "allowed",
    }


@pytest.mark.parametrize(
    ("config_mutation", "reason_fragment"),
    [
        (lambda path: path / "missing", "config unavailable"),
        (lambda path: (path / "policy.yml").write_text(":: bad: [", encoding="utf-8"), "config unavailable"),
    ],
)
def test_fail_closed_denies_missing_or_unparseable_config(tmp_path, config_mutation, reason_fragment):
    config_dir = write_config(tmp_path)
    mutated = config_mutation(config_dir)
    decision = decide(request(), config=mutated if isinstance(mutated, Path) else config_dir)

    assert_denied(decision, reason_fragment)


@pytest.mark.parametrize(
    ("overrides", "reason_fragment"),
    [
        ({"scope_name": "unknown"}, "unknown scope"),
        ({"target_repos": ["owner/not-in-scope"]}, "repo outside scope allowlist"),
        ({"operator_id": "tg-missing"}, "unknown operator"),
    ],
)
def test_fail_closed_denies_unknown_scope_repo_or_operator(tmp_path, overrides, reason_fragment):
    decision = decide(request(**overrides), config=write_config(tmp_path))

    assert_denied(decision, reason_fragment)


@pytest.mark.parametrize(
    ("policy_overrides", "request_overrides", "reason_fragment"),
    [
        ("kill_switches:\n  disable_all_writes: true\n", {}, "writes disabled"),
        ("kill_switches:\n  disabled_scopes: [acma]\n", {}, "scope disabled"),
        ("kill_switches:\n  disabled_operators: [tg-100]\n", {}, "operator disabled"),
        ("kill_switches:\n  disabled_platforms: [telegram]\n", {}, "platform disabled"),
    ],
)
def test_kill_switches_deny_affected_requests(tmp_path, policy_overrides, request_overrides, reason_fragment):
    decision = decide(
        request(**request_overrides),
        config=write_config(tmp_path, policy_overrides=policy_overrides),
    )

    assert_denied(decision, reason_fragment)


def test_disable_all_writes_does_not_deny_reads(tmp_path):
    decision = decide(
        request(action_class="read", change=None),
        config=write_config(tmp_path, policy_overrides="kill_switches:\n  disable_all_writes: true\n"),
    )

    assert decision["allow"] is True


def test_operator_must_be_authorized_for_resolved_scope(tmp_path):
    decision = decide(
        request(operator_id="tg-200", scope_name="acma"),
        config=write_config(tmp_path),
    )

    assert_denied(decision, "operator not authorized for scope")


def test_external_operator_denied_from_external_disabled_ecosystem_scope(tmp_path):
    decision = decide(
        request(
            operator_id="external-1",
            scope_name="ecosystem",
            target_repos=["owner/ecosystem"],
            origin={"is_dm": True, "channel_id": "dm-ext"},
        ),
        config=write_config(
            tmp_path,
            scope_overrides="""
scopes:
  ecosystem:
    sensitivity: internal
    permission: write
    repositories: [owner/ecosystem]
    operators: [external-1]
    external_disabled: true
""",
        ),
    )

    assert_denied(decision, "external operators disabled for scope")


def test_origin_bound_default_resolves_scope_only_from_channel_binding(tmp_path):
    decision = decide(
        request(scope_name=None, target_repos=["owner/acma"], origin={"is_dm": False, "channel_id": "acma-room"}),
        config=write_config(tmp_path),
    )

    assert decision["allow"] is True
    assert decision["scope_resolved"] == "acma"


def test_origin_bound_default_without_binding_denies_write_and_requires_explicit_scope(tmp_path):
    decision = decide(
        request(scope_name=None, target_repos=["owner/acma"], origin={"is_dm": False, "channel_id": "unbound-room"}),
        config=write_config(tmp_path),
    )

    assert_denied(decision, "explicit scope required")


def test_origin_bound_default_requires_origin_repo_containment_in_authorized_scope(tmp_path):
    decision = decide(
        request(
            operator_id="tg-200",
            scope_name=None,
            target_repos=["owner/acma"],
            origin={"is_dm": False, "channel_id": "acma-room"},
        ),
        config=write_config(tmp_path),
    )

    assert_denied(decision, "operator not authorized for origin scope")


@pytest.mark.parametrize("action_class", ["repo_delete", "branch_delete", "force_push", "reset_hard"])
def test_destructive_actions_are_denied_for_every_scope(tmp_path, action_class):
    decision = decide(request(action_class=action_class), config=write_config(tmp_path))

    assert_denied(decision, "destructive action denied")


@pytest.mark.parametrize(
    ("change", "reason_fragment"),
    [
        ({"files_deleted": 3, "touches_protected": False}, "mass deletion requires elevation"),
        ({"files_deleted": 0, "touches_protected": True}, "protected change requires elevation"),
    ],
)
def test_diff_risk_gate_denies_write_without_valid_elevation(tmp_path, change, reason_fragment):
    decision = decide(request(change=change), config=write_config(tmp_path))

    assert_denied(decision, reason_fragment)


@pytest.mark.parametrize("elevation_token", ["internal-admin", {"approver": "internal-admin"}])
def test_diff_risk_gate_allows_write_with_valid_elevation(tmp_path, elevation_token):
    decision = decide(
        request(change={"files_deleted": 3, "touches_protected": True}, elevation_token=elevation_token),
        config=write_config(tmp_path),
    )

    assert decision["allow"] is True


def test_diff_risk_gate_denies_invalid_elevation_token(tmp_path):
    decision = decide(
        request(change={"files_deleted": 4, "touches_protected": False}, elevation_token="not-an-approver"),
        config=write_config(tmp_path),
    )

    assert_denied(decision, "mass deletion requires elevation")


def test_repository_read_only_flag_denies_writes_but_allows_reads(tmp_path):
    write_decision = decide(
        request(target_repos=["owner/acma-archive"]),
        config=write_config(tmp_path),
    )
    read_decision = decide(
        request(target_repos=["owner/acma-archive"], action_class="read", change=None),
        config=write_config(tmp_path),
    )

    assert_denied(write_decision, "repo is read-only")
    assert read_decision["allow"] is True


def test_private_scope_reply_visibility_is_generic_in_uncleared_channel(tmp_path):
    decision = decide(
        request(origin={"is_dm": False, "channel_id": "shared-room"}),
        config=write_config(tmp_path),
    )

    assert decision["allow"] is True
    assert decision["reply_visibility"] == "generic"


def test_private_scope_reply_visibility_is_full_in_cleared_channel(tmp_path):
    decision = decide(
        request(origin={"is_dm": False, "channel_id": "acma-room"}),
        config=write_config(tmp_path),
    )

    assert decision["allow"] is True
    assert decision["reply_visibility"] == "full"


def test_internal_scope_reply_visibility_is_full_in_channel(tmp_path):
    decision = decide(
        request(
            operator_id="internal-admin",
            scope_name="ecosystem",
            target_repos=["owner/ecosystem"],
            origin={"is_dm": False, "channel_id": "ops-room"},
        ),
        config=write_config(tmp_path),
    )

    assert decision["allow"] is True
    assert decision["reply_visibility"] == "full"


def test_denied_decision_still_returns_audit_record(tmp_path):
    decision = decide(request(scope_name="missing"), config=write_config(tmp_path))

    assert decision["audit"]["operator"] == "tg-100"
    assert decision["audit"]["platform"] == "telegram"
    assert decision["audit"]["scope"] == "missing"
    assert decision["audit"]["repos"] == ["owner/acma"]
    assert decision["audit"]["action_class"] == "write"
    assert decision["audit"]["decision"] == "DENY"
