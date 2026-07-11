"""Tests for the fail-closed crontab transaction core (issue #2969 / F2)."""
import importlib.util
import sys
from pathlib import Path

# Load the module by file path (its dir is not a package).
_MODULE_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "cron" / "cron_transaction.py"
)
_spec = importlib.util.spec_from_file_location("cron_transaction", _MODULE_PATH)
ct = importlib.util.module_from_spec(_spec)
sys.modules["cron_transaction"] = ct
_spec.loader.exec_module(ct)


# --- helpers ---------------------------------------------------------------

def _begin(roles):
    return ct.marker_begin(roles)


# --- parse_crontab ---------------------------------------------------------

def test_parse_zero_markers_valid():
    text = "MAILTO=ops@x.com\n0 * * * * echo hi\n"
    p = ct.parse_crontab(text)
    assert p["error"] is None
    assert p["managed"] == []
    assert p["after"] == []
    assert p["before"] == ["MAILTO=ops@x.com", "0 * * * * echo hi"]
    assert p["roles"] is None


def test_parse_one_block_splits_correctly():
    text = "\n".join([
        "SHELL=/bin/bash",
        _begin(["a", "b"]),
        "0 1 * * * run-a",
        "0 2 * * * run-b",
        ct.MARKER_END,
        "0 9 * * * external-thing",
    ]) + "\n"
    p = ct.parse_crontab(text)
    assert p["error"] is None
    assert p["before"] == ["SHELL=/bin/bash"]
    assert p["managed"] == ["0 1 * * * run-a", "0 2 * * * run-b"]
    assert p["after"] == ["0 9 * * * external-thing"]
    assert p["roles"] == "a+b"


def test_parse_more_than_one_block_is_error():
    text = "\n".join([
        _begin(["a"]), "x", ct.MARKER_END,
        _begin(["b"]), "y", ct.MARKER_END,
    ]) + "\n"
    p = ct.parse_crontab(text)
    assert p["error"] is not None


def test_parse_begin_without_end_is_error():
    text = "\n".join([_begin(["a"]), "0 1 * * * run-a"]) + "\n"
    p = ct.parse_crontab(text)
    assert p["error"] is not None


def test_parse_end_without_begin_is_error():
    text = "\n".join(["0 1 * * * run-a", ct.MARKER_END]) + "\n"
    p = ct.parse_crontab(text)
    assert p["error"] is not None


def test_parse_end_before_begin_is_error():
    text = "\n".join([ct.MARKER_END, _begin(["a"])]) + "\n"
    p = ct.parse_crontab(text)
    assert p["error"] is not None


def test_parse_preserves_env_blank_comment_lines():
    text = "\n".join([
        "MAILTO=ops@x.com",
        "SHELL=/bin/bash",
        "PATH=/usr/bin:/bin",
        "",
        "# a comment",
        "0 5 * * * echo hi",
    ]) + "\n"
    p = ct.parse_crontab(text)
    assert p["error"] is None
    assert p["before"] == [
        "MAILTO=ops@x.com",
        "SHELL=/bin/bash",
        "PATH=/usr/bin:/bin",
        "",
        "# a comment",
        "0 5 * * * echo hi",
    ]


# --- match_fingerprint -----------------------------------------------------

def test_match_fingerprint_command_contains_list_all_must_match():
    line = "0 1 * * * cd /repo && uv run python3 scripts/foo.py"
    assert ct.match_fingerprint(line, {"command_contains": ["uv run", "foo.py"]})
    assert not ct.match_fingerprint(line, {"command_contains": ["uv run", "missing"]})


def test_match_fingerprint_command_contains_str():
    line = "0 1 * * * do-the-thing"
    assert ct.match_fingerprint(line, {"command_contains": "do-the-thing"})
    assert not ct.match_fingerprint(line, {"command_contains": "nope"})


def test_match_fingerprint_command_tokens_require_adjacent_shell_tokens():
    token = ".claude/skills/business-marketing/deckhand-api-presence-sync/catalog_delta.py"
    line = f"0 5 * * 0 uv run python {token} >> logs/out.log"

    fingerprint = {"command_tokens": ["python", token]}
    assert ct.match_fingerprint(line, fingerprint)
    assert not ct.match_fingerprint(line.replace(token, f"prefix{token}"), fingerprint)
    assert not ct.match_fingerprint(line.replace(token, f"{token}.bak"), fingerprint)
    assert not ct.match_fingerprint(f"0 * * * * echo --input={token}", fingerprint)
    assert not ct.match_fingerprint(f"0 * * * * printf x > {token}", fingerprint)


def test_match_fingerprint_cwd_and_basename():
    line = "30 7 * * * cd /mnt/x/deckhand && python3 scripts/member-audit-cron.py"
    assert ct.match_fingerprint(line, {"cwd_contains": "/deckhand"})
    assert ct.match_fingerprint(line, {"script_basename": "member-audit-cron.py"})
    assert ct.match_fingerprint(
        line, {"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}
    )


def test_match_fingerprint_empty_is_false():
    assert not ct.match_fingerprint("anything at all", {})


def test_match_fingerprint_partial_mismatch_is_false():
    line = "30 7 * * * cd /deckhand && python3 other.py"
    assert not ct.match_fingerprint(
        line, {"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}
    )


def test_match_fingerprint_owner_repo_like_command_contains():
    line = "0 1 * * * cd /mnt/local-analysis/deckhand && run"
    assert ct.match_fingerprint(line, {"owner_repo": "deckhand"})
    assert ct.match_fingerprint(line, {"owner_repo": ["deckhand", "run"]})
    assert not ct.match_fingerprint(line, {"owner_repo": ["deckhand", "absent"]})


# --- classify_line ---------------------------------------------------------

def test_classify_cataloged():
    line = "0 1 * * * /opt/wshub/run-task.sh foo"
    assert ct.classify_line(line, ["run-task.sh"], []) == "cataloged"


def test_classify_preserved_external():
    line = "30 7 * * * cd /deckhand && python3 scripts/member-audit-cron.py"
    fps = [{"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}]
    assert ct.classify_line(line, ["run-task.sh"], fps) == "preserved_external"


def test_classify_uncataloged():
    line = "0 3 * * * /some/unknown/thing --flag"
    assert ct.classify_line(line, ["run-task.sh"], []) == "uncataloged"


def test_catalog_fingerprint_requires_all_fields_not_bare_script_substring():
    fingerprint = [{
        "catalog_task_id": "repository-sync",
        "fingerprint": {
            "command_contains": "scripts/cron-repository-sync.sh",
            "cwd_contains": "/workspace-hub",
        },
    }]
    owned = "0 */4 * * * cd /srv/workspace-hub && bash scripts/cron-repository-sync.sh"
    external = "0 */4 * * * cd /srv/external && echo scripts/cron-repository-sync.sh"

    owned_detail = ct.classify_line_detail(
        owned, [], [], catalog_fingerprints=fingerprint
    )
    external_detail = ct.classify_line_detail(
        external, [], [], catalog_fingerprints=fingerprint
    )

    assert owned_detail["class"] == "cataloged"
    assert owned_detail["catalog_task_id"] == "repository-sync"
    assert external_detail["class"] == "uncataloged"


def test_catalog_cwd_regex_does_not_claim_similar_repo_name():
    fingerprint = [{
        "catalog_task_id": "repository-sync",
        "fingerprint": {
            "command_contains": "scripts/cron-repository-sync.sh",
            "cwd_basename": "workspace-hub",
        },
    }]
    owned = "0 * * * * cd /srv/workspace-hub && bash scripts/cron-repository-sync.sh"
    unrelated = "0 * * * * cd /tmp/not-workspace-hub && bash scripts/cron-repository-sync.sh"

    assert ct.classify_line_detail(owned, [], [], catalog_fingerprints=fingerprint)["class"] == "cataloged"
    assert ct.classify_line_detail(unrelated, [], [], catalog_fingerprints=fingerprint)["class"] == "uncataloged"


def test_plan_cutover_drops_only_explicitly_owned_stale_duplicate():
    fingerprint = [{
        "catalog_task_id": "hermes-claude-bridge",
        "fingerprint": {
            "command_contains": "scripts/memory/bridge-hermes-claude.sh",
            "cwd_contains": "/workspace-hub",
        },
    }]
    stale = "25 4 * * * cd /srv/workspace-hub && bash scripts/memory/bridge-hermes-claude.sh"
    task = {
        "id": "hermes-claude-bridge",
        "schedule": "25 4 * * *",
        "command": "cd /srv/workspace-hub && bash scripts/memory/bridge-hermes-claude.sh --commit",
    }

    plan = ct.plan_cutover(
        stale + "\n",
        [task],
        ["control-plane"],
        catalog_commands=[],
        external_fingerprints=[],
        catalog_fingerprints=fingerprint,
    )

    assert plan["abort_reason"] is None
    assert stale not in plan["new_text"].splitlines()
    assert "--commit" in plan["new_text"]


def test_classify_ignore_comment_blank_env():
    assert ct.classify_line("# comment", [], []) == "ignore"
    assert ct.classify_line("", [], []) == "ignore"
    assert ct.classify_line("   ", [], []) == "ignore"
    assert ct.classify_line("MAILTO=ops@x.com", [], []) == "ignore"
    assert ct.classify_line("PATH=/usr/bin", [], []) == "ignore"


# --- select_tasks ----------------------------------------------------------

def test_select_by_role_intersection():
    tasks = [{"id": "t1", "roles": ["worker", "db"]}]
    sel, conf = ct.select_tasks(tasks, ["worker"], "host1")
    assert [t["id"] for t in sel] == ["t1"]
    assert conf == []


def test_select_by_legacy_machine_pin():
    tasks = [{"id": "t1", "machines": ["host1", "host2"]}]
    sel, conf = ct.select_tasks(tasks, ["nope"], "host1")
    assert [t["id"] for t in sel] == ["t1"]


def test_select_dedupe_both_paths_single_emit():
    tasks = [{"id": "t1", "roles": ["worker"], "machines": ["host1"]}]
    sel, conf = ct.select_tasks(tasks, ["worker"], "host1")
    assert [t["id"] for t in sel] == ["t1"]
    assert len(sel) == 1


def test_select_conflict_roles_authoritative_true_roles_win():
    tasks = [{
        "id": "t1", "roles": ["worker"],
        "machines": ["host2"], "roles_authoritative": True,
    }]
    sel, conf = ct.select_tasks(tasks, ["worker"], "host1")
    assert [t["id"] for t in sel] == ["t1"]
    assert len(conf) == 1
    assert conf[0]["id"] == "t1"


def test_select_conflict_roles_authoritative_false_legacy_wins():
    tasks = [{
        "id": "t1", "roles": ["worker"], "machines": ["host2"],
    }]
    sel, conf = ct.select_tasks(tasks, ["worker"], "host1")
    assert sel == []
    assert len(conf) == 1
    assert conf[0]["id"] == "t1"


def test_select_sorted_by_id():
    tasks = [
        {"id": "zeta", "roles": ["w"]},
        {"id": "alpha", "roles": ["w"]},
        {"id": "mid", "roles": ["w"]},
    ]
    sel, _ = ct.select_tasks(tasks, ["w"], "host1")
    assert [t["id"] for t in sel] == ["alpha", "mid", "zeta"]


def test_select_accepts_machine_token_set_and_filters_non_cron_schedulers():
    tasks = [
        {"id": "cron-pinned", "machines": ["alias-one"], "scheduler": "cron"},
        {
            "id": "windows-role",
            "roles": ["w"],
            "machines": ["alias-one"],
            "scheduler": "windows-task-scheduler",
        },
    ]
    sel, conf = ct.select_tasks(tasks, ["w"], {"host1", "alias-one"})
    assert [t["id"] for t in sel] == ["cron-pinned"]
    assert conf == []


# --- render_block ----------------------------------------------------------

def test_render_block_sorted_and_markers():
    tasks = [
        {"id": "b", "schedule": "0 2 * * *", "command": "run-b"},
        {"id": "a", "schedule": "0 1 * * *", "command": "run-a"},
    ]
    block = ct.render_block(tasks, ["x", "y"])
    assert ct.MARKER_BEGIN_RE.match(block[0])
    assert "role: x+y" in block[0]
    assert block[1] == "0 1 * * * run-a"
    assert block[2] == "0 2 * * * run-b"
    assert block[-1] == ct.MARKER_END


def test_render_block_deterministic():
    tasks = [{"id": "a", "schedule": "0 1 * * *", "command": "run-a"}]
    assert ct.render_block(tasks, ["r"]) == ct.render_block(tasks, ["r"])


# --- plan_cutover ----------------------------------------------------------

EXTERNAL_LINE = (
    "30 7 * * * PATH=/snap/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin; "
    "cd /mnt/local-analysis/deckhand && uv run --with telethon python3 "
    "scripts/deckhand/member-audit-cron.py >> $HOME/.hermes/logs/member-audit.log 2>&1"
)
EXTERNAL_FP = {"cwd_contains": "/deckhand", "script_basename": "member-audit-cron.py"}


def test_plan_cutover_preserves_external_line_verbatim_outside_block():
    current = EXTERNAL_LINE + "\n"
    tasks = [{"id": "t1", "schedule": "0 1 * * *", "command": "run-a"}]
    plan = ct.plan_cutover(
        current, tasks, ["worker"],
        catalog_commands=["run-a"], external_fingerprints=[EXTERNAL_FP],
    )
    assert plan["abort_reason"] is None
    assert EXTERNAL_LINE in plan["new_text"]
    # It must survive OUTSIDE the managed block.
    p = ct.parse_crontab(plan["new_text"])
    assert EXTERNAL_LINE in (p["before"] + p["after"])
    assert EXTERNAL_LINE not in p["managed"]
    # And the task is inside the block.
    assert "0 1 * * * run-a" in p["managed"]


def test_plan_cutover_aborts_on_uncataloged_line():
    current = "0 3 * * * /unknown/thing --flag\n"
    tasks = [{"id": "t1", "schedule": "0 1 * * *", "command": "run-a"}]
    plan = ct.plan_cutover(
        current, tasks, ["worker"],
        catalog_commands=["run-a"], external_fingerprints=[],
    )
    assert plan["abort_reason"] is not None
    assert plan["new_text"] is None
    assert "/unknown/thing --flag" in plan["uncataloged"][0]


def test_plan_cutover_aborts_on_parse_error():
    current = "\n".join([ct.marker_begin(["a"]), "x"]) + "\n"  # begin w/o end
    plan = ct.plan_cutover(
        current, [], ["worker"], catalog_commands=[], external_fingerprints=[],
    )
    assert plan["abort_reason"] is not None
    assert plan["new_text"] is None


def test_plan_cutover_idempotent():
    current = "\n".join([
        "MAILTO=ops@x.com",
        EXTERNAL_LINE,
    ]) + "\n"
    tasks = [
        {"id": "b", "schedule": "0 2 * * *", "command": "run-b"},
        {"id": "a", "schedule": "0 1 * * *", "command": "run-a"},
    ]
    catalog = ["run-a", "run-b"]
    plan1 = ct.plan_cutover(
        current, tasks, ["worker"],
        catalog_commands=catalog, external_fingerprints=[EXTERNAL_FP],
    )
    assert plan1["abort_reason"] is None
    plan2 = ct.plan_cutover(
        plan1["new_text"], tasks, ["worker"],
        catalog_commands=catalog, external_fingerprints=[EXTERNAL_FP],
    )
    assert plan2["abort_reason"] is None
    assert plan1["new_text"] == plan2["new_text"]


def test_plan_cutover_existing_block_replaced_in_place():
    current = "\n".join([
        "MAILTO=ops@x.com",
        ct.marker_begin(["old"]),
        "0 9 * * * stale-run-a",
        ct.MARKER_END,
        EXTERNAL_LINE,
    ]) + "\n"
    tasks = [{"id": "a", "schedule": "0 1 * * *", "command": "run-a fresh"}]
    plan = ct.plan_cutover(
        current, tasks, ["worker"],
        catalog_commands=["run-a"], external_fingerprints=[EXTERNAL_FP],
    )
    assert plan["abort_reason"] is None
    p = ct.parse_crontab(plan["new_text"])
    assert p["managed"] == ["0 1 * * * run-a fresh"]
    assert "MAILTO=ops@x.com" in p["before"]
    assert EXTERNAL_LINE in p["after"]
    # Stale cataloged line is gone.
    assert "0 9 * * * stale-run-a" not in plan["new_text"]


def test_plan_cutover_accepts_existing_five_argument_callers_after_selected_task_ids_extension():
    plan = ct.plan_cutover(
        "",
        [{"id": "a", "schedule": "0 1 * * *", "command": "run-a"}],
        ["worker"],
        ["run-a"],
        [],
    )
    assert plan["abort_reason"] is None
    assert "0 1 * * * run-a" in plan["new_text"]


def test_plan_cutover_preserves_workspace_hub_and_log_env_lines_verbatim():
    current = "\n".join(
        [
            "WORKSPACE_HUB=/custom/workspace-hub",
            "LOG=/tmp/custom-cron.log",
            "",
        ]
    )
    plan = ct.plan_cutover(
        current,
        [{"id": "a", "schedule": "0 1 * * *", "command": "run-a"}],
        ["worker"],
        ["run-a"],
        [],
    )
    assert plan["abort_reason"] is None
    assert plan["new_text"].splitlines()[:2] == [
        "WORKSPACE_HUB=/custom/workspace-hub",
        "LOG=/tmp/custom-cron.log",
    ]


def test_preserved_fingerprint_entries_retain_catalog_task_id_metadata():
    line = (
        "30 4 * * * cd /mnt/local-analysis/workspace-hub && "
        'find logs/notifications/ -name "*.jsonl" -mtime +7 -delete 2>/dev/null || true'
    )
    entries = [
        {
            "owner": "ace-linux-1",
            "catalog_task_id": "notification-purge",
            "fingerprint": {
                "command_contains": ["find logs/notifications/", "-delete"],
            },
        }
    ]

    normalized = ct.normalize_preserved_entries(entries)
    assert normalized[0]["catalog_task_id"] == "notification-purge"
    detail = ct.classify_line_detail(
        line,
        catalog_commands=[],
        external_fingerprints=entries,
        selected_task_ids={"notification-purge"},
    )
    assert detail["class"] == "cataloged"
    assert detail["catalog_task_id"] == "notification-purge"


def test_all_fallback_catalog_keys_are_unique_nonempty_and_full_command_based():
    long_command = "printf '" + ("x" * 90) + "' >> /tmp/no-script-path.log 2>&1"
    tasks = [
        {"id": "a", "command": "echo    one    two"},
        {"id": "b", "command": long_command},
        {"id": "c", "command": "bash scripts/cron/example-task.sh --flag"},
    ]
    keys = ct.catalog_command_keys(tasks)
    assert len(keys) == len(set(keys))
    assert all(keys)
    assert "echo one two" in keys
    assert long_command in keys
    assert "scripts/cron/example-task.sh" in keys
    assert all(len(key) > 60 for key in keys if key.startswith("printf"))
