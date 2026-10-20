"""Tests for scripts/cron/cron-audit.py (#2969, F2).

cron-audit.py carries a hyphen, so it is imported by file path. It in turn
imports the pure core cron_transaction.py (also by path). These tests exercise
the three required classifications end-to-end through the real loaders + the
real classify_line: an external line -> preserved_external, a catalog line ->
cataloged, a random line -> uncataloged.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = REPO_ROOT / "scripts" / "cron" / "cron-audit.py"
CRON_TX_PATH = REPO_ROOT / "scripts" / "cron" / "cron_transaction.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def audit():
    return _load_module("cron_audit_under_test", AUDIT_PATH)


@pytest.fixture(scope="module")
def ct():
    return _load_module("cron_transaction_under_test", CRON_TX_PATH)


# Active external ingestion is preserved across wrapper and logging changes.
EXTERNAL_INGEST = (
    "0 */6 * * * bash /srv/llm-wiki/scripts/ingest/cron_ingest.sh >> /tmp/ingest.log 2>&1"
)


def test_external_line_is_preserved(audit, ct):
    fps = audit.load_external_fingerprints()
    assert ct.classify_line(EXTERNAL_INGEST, [], fps) == "preserved_external"


def test_external_match_survives_path_log_and_wrapper_changes(audit, ct):
    fps = audit.load_external_fingerprints()
    mutated = "0 */6 * * * /bin/bash /opt/llm-wiki/cron_ingest.sh >> /var/log/ingest.log 2>&1"
    assert ct.classify_line(mutated, [], fps) == "preserved_external"


def test_catalog_line_is_cataloged(audit, ct):
    context = audit.build_audit_context("ace-linux-1")["ownership_context"]
    line = context["canonical_exact_lines"]["benchmark-regression"][0]
    assert ct.classify_line_detail(line, ownership_context=context)["class"] == "cataloged"


def test_random_line_is_uncataloged(audit, ct):
    cmds = audit.load_catalog_commands()
    fps = audit.load_external_fingerprints()
    line = "0 3 * * * /usr/local/bin/some-rando-thing --do-stuff >> /tmp/x.log 2>&1"
    assert ct.classify_line(line, cmds, fps) == "uncataloged"


def test_audit_context_uses_exact_lines_for_sensitive_tasks(audit):
    context = audit.build_audit_context("ace-linux-1")
    exact = context["ownership_context"]["canonical_exact_lines"]
    assert exact["hermes-claude-bridge"]
    assert exact["repository-sync"]
    ids = {entry["catalog_task_id"] for entry in context["catalog_fingerprints"]}
    assert not {"hermes-claude-bridge", "repository-sync"} & ids


def test_audit_crontab_fails_closed_on_uncataloged(audit, ct):
    cmds = audit.load_catalog_commands()
    fps = audit.load_external_fingerprints()
    text = "\n".join(
        [
            "# a comment",
            "MAILTO=ops@example.com",
            EXTERNAL_INGEST,
            "0 3 * * * /usr/local/bin/some-rando-thing >> /tmp/x.log 2>&1",
        ]
    )
    result = audit.audit_crontab(text, cmds, fps, ct.classify_line)
    assert result["counts"]["preserved_external"] == 1
    assert result["counts"]["uncataloged"] == 1
    assert result["counts"]["ignore"] == 2  # comment + MAILTO env line
    assert len(result["uncataloged"]) == 1


def test_stable_command_fragment_prefers_script_path(audit):
    cmd = (
        "PATH=$HOME/.local/bin:$PATH; cd $WORKSPACE_HUB && "
        "bash scripts/testing/run-benchmarks.sh >> $WORKSPACE_HUB/logs/x.log 2>&1"
    )
    assert audit.stable_command_fragment(cmd) == "scripts/testing/run-benchmarks.sh"


# ── #2988: preserved_local merges into the keep-verbatim bucket ──────────────
def test_preserved_local_merged_into_fingerprints(tmp_path):
    import importlib.util as _u, sys as _s
    spec = _u.spec_from_file_location("cron_audit_x", REPO_ROOT / "scripts" / "cron" / "cron-audit.py") \
        if "REPO_ROOT" in dir() else None
    # load module fresh by path
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[2]
    spec = _u.spec_from_file_location("cron_audit_x", root / "scripts" / "cron" / "cron-audit.py")
    m = _u.module_from_spec(spec); _s.modules["cron_audit_x"] = m; spec.loader.exec_module(m)
    classes = tmp_path / "hsc.yaml"
    classes.write_text(
        "preserved_external:\n  - fingerprint: {cwd_contains: /external-repo}\n"
        "preserved_local:\n  - fingerprint: {command_contains: scripts/maintenance/update-model-ids.sh}\n"
    )
    fps = m.load_external_fingerprints(classes)
    assert len(fps) == 2
    assert any(fp.get("command_contains") == "scripts/maintenance/update-model-ids.sh" for fp in fps)


def test_cron_audit_and_cron_apply_share_rendered_catalog_keys_and_fingerprint_metadata(tmp_path):
    import importlib.util as _u, sys as _s

    root = Path(__file__).resolve().parents[2]
    audit_spec = _u.spec_from_file_location("cron_audit_shared", root / "scripts" / "cron" / "cron-audit.py")
    audit_mod = _u.module_from_spec(audit_spec)
    _s.modules["cron_audit_shared"] = audit_mod
    audit_spec.loader.exec_module(audit_mod)

    apply_spec = _u.spec_from_file_location("cron_apply_shared", root / "scripts" / "cron" / "cron_apply.py")
    apply_mod = _u.module_from_spec(apply_spec)
    _s.modules["cron_apply_shared"] = apply_mod
    apply_spec.loader.exec_module(apply_mod)

    catalog = {
        "tasks": [
            {
                "id": "fallback-log",
                "schedule": "0 1 * * *",
                "machines": ["m1"],
                "roles": ["worker"],
                "command": "echo $WORKSPACE_HUB >> $LOG 2>&1",
            }
        ]
    }
    registry = {
        "machines": {
            "m1": {
                "hostname": "host-one",
                "hostname_aliases": ["alias-one"],
                "schedule_variant": "contribute",
                "workspace_root": str(root),
                "harness_profile": {"roles": ["worker"]},
            }
        }
    }
    classes = {
        "preserved_local": [
            {
                "owner": "m1",
                "catalog_task_id": "fallback-log",
                "fingerprint": {"command_contains": "echo "},
            }
        ]
    }

    catalog_path = tmp_path / "schedule-tasks.yaml"
    registry_path = tmp_path / "registry.yaml"
    classes_path = tmp_path / "classes.yaml"
    catalog_path.write_text(__import__("yaml").safe_dump(catalog), encoding="utf-8")
    registry_path.write_text(__import__("yaml").safe_dump(registry), encoding="utf-8")
    classes_path.write_text(__import__("yaml").safe_dump(classes), encoding="utf-8")

    audit_keys = audit_mod.load_catalog_commands(
        catalog_path, registry_path=registry_path, machine_id="alias-one"
    )
    apply_keys = apply_mod.catalog_commands(
        catalog, registry=registry, machine_id="alias-one"
    )
    audit_fps = audit_mod.load_external_fingerprints(classes_path)
    apply_fps = apply_mod.external_fingerprints(classes)

    assert audit_keys == apply_keys
    assert "echo $WORKSPACE_HUB >> $LOG 2>&1" in audit_keys
    assert f"echo {root} >> /tmp/workspace-hub-cron.log 2>&1" in audit_keys
    assert audit_fps == apply_fps
    assert audit_fps[0]["catalog_task_id"] == "fallback-log"


def test_cron_audit_json_cli_smoke_uses_shared_classifier(monkeypatch, capsys, audit):
    line = (
        "30 4 * * * cd /mnt/local-analysis/workspace-hub && "
        'find logs/notifications/ -name "*.jsonl" -mtime +7 -delete 2>/dev/null || true'
    )
    identity = {line: {"catalog_task_id": "notification-purge",
                       "source": "legacy-exact-line", "variant_id": "a1"}}
    monkeypatch.setattr(audit, "read_live_crontab", lambda: line + "\n")
    monkeypatch.setattr(
        audit,
        "build_audit_context",
        lambda machine_id=None: {
            "machine": "dev-primary",
            "catalog_commands": [],
            "external_fingerprints": [],
            "selected_task_ids": {"notification-purge"},
            "ownership_context": {"line_identities": identity,
                                  "preservation_fingerprints": []},
        },
        raising=False,
    )

    rc = audit.main(["--machine", "dev-primary", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert rc == 0
    assert payload["ok"] is True
    assert payload["lines"][0]["class"] == "cataloged"
    assert payload["lines"][0]["catalog_task_id"] == "notification-purge"


def test_cron_audit_json_default_machine_uses_selected_task_ids(monkeypatch, capsys, audit):
    line = (
        "30 4 * * * cd /mnt/local-analysis/workspace-hub && "
        'find logs/notifications/ -name "*.jsonl" -mtime +7 -delete 2>/dev/null || true'
    )
    identity = {line: {"catalog_task_id": "notification-purge",
                       "source": "legacy-exact-line", "variant_id": "a1"}}

    class FakeRender:
        @staticmethod
        def build_context(machine_id=None, registry=None):
            assert machine_id is None
            return {"machine_id": "dev-primary"}

    monkeypatch.setattr(audit, "load_cron_render", lambda: FakeRender())
    monkeypatch.setattr(
        audit,
        "_selected_for_machine",
        lambda catalog, registry, machine_id: {
            "context": {"machine_id": machine_id},
            "selected_raw": [],
            "selected": [],
            "selected_task_ids": {"notification-purge"},
            "conflicts": [],
        },
    )
    monkeypatch.setattr(audit, "load_external_fingerprints", lambda path=audit.CLASSES_PATH: [])
    monkeypatch.setattr(
        audit, "build_ownership_context",
        lambda catalog, registry, classes, machine: {
            "line_identities": identity, "preservation_fingerprints": []
        },
    )
    monkeypatch.setattr(audit, "read_live_crontab", lambda: line + "\n")

    rc = audit.main(["--json"])
    payload = json.loads(capsys.readouterr().out)

    assert rc == 0
    assert payload["machine"] == "dev-primary"
    assert payload["lines"][0]["class"] == "cataloged"
    assert payload["lines"][0]["catalog_task_id"] == "notification-purge"


def test_catalog_owned_fingerprint_unselected_machine_remains_preserved_external(tmp_path, ct):
    import importlib.util as _u, sys as _s

    root = Path(__file__).resolve().parents[2]
    audit_spec = _u.spec_from_file_location("cron_audit_unselected", root / "scripts" / "cron" / "cron-audit.py")
    audit_mod = _u.module_from_spec(audit_spec)
    _s.modules["cron_audit_unselected"] = audit_mod
    audit_spec.loader.exec_module(audit_mod)

    apply_spec = _u.spec_from_file_location("cron_apply_unselected", root / "scripts" / "cron" / "cron_apply.py")
    apply_mod = _u.module_from_spec(apply_spec)
    _s.modules["cron_apply_unselected"] = apply_mod
    apply_spec.loader.exec_module(apply_mod)

    entry = {
        "owner": "ace-linux-1",
        "catalog_task_id": "notification-purge",
        "fingerprint": {"command_contains": ["find logs/notifications/", "-delete"]},
    }
    classes = {"preserved_local": [entry]}
    classes_path = tmp_path / "classes.yaml"
    classes_path.write_text(__import__("yaml").safe_dump(classes), encoding="utf-8")
    line = (
        "30 4 * * * cd /mnt/local-analysis/workspace-hub && "
        'find logs/notifications/ -name "*.jsonl" -mtime +7 -delete 2>/dev/null || true'
    )

    audit_fps = audit_mod.load_external_fingerprints(classes_path)
    apply_fps = apply_mod.external_fingerprints(classes)

    assert ct.classify_line_detail(line, [], audit_fps, selected_task_ids=set())["class"] == "preserved_external"
    assert ct.classify_line_detail(line, [], apply_fps, selected_task_ids=set())["class"] == "preserved_external"


def test_cron_audit_fails_closed_on_unreadable_crontab(monkeypatch, capsys, audit):
    class Proc:
        returncode = 1
        stdout = ""
        stderr = "crontab: permission denied"

    monkeypatch.setattr(audit.subprocess, "run", lambda *a, **k: Proc())
    rc = audit.main(["--json"])
    payload = json.loads(capsys.readouterr().out)

    assert rc != 0
    assert payload["ok"] is False
    assert "permission denied" in payload["stderr"]
