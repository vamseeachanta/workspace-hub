#!/usr/bin/env python3
"""Regressions for exact ownership of legacy ace-linux-1 cron lines (#2988, #3384).

The tests load the real catalog and state classes, build ownership exactly as cron_apply.py does,
and prove externally owned lines remain preserved while catalog-owned legacy variants are
deduplicated into the generated managed block.

Run: uv run --no-project --with pyyaml pytest tests/cron/test_a1_preserved.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]


def _load_module(name: str, rel: str):
    """Import a module by file path; register in sys.modules BEFORE exec so that
    dataclasses / intra-module references resolve safely (cron_apply imports cron_transaction)."""
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# cron_transaction must be registered first — cron_apply imports it by that name.
ct = _load_module("cron_transaction", "scripts/cron/cron_transaction.py")
ca = _load_module("cron_apply", "scripts/cron/cron_apply.py")

# The 2 real a1 uncataloged live lines from the cutover block.
A1_LLM_WIKI_LINE = (
    "0 */6 * * * /bin/bash /mnt/local-analysis/llm-wiki/scripts/ingest/cron_ingest.sh "
    "# llm-wiki-corpus-ingest-campaign"
)
A1_NOTIFICATION_PURGE_LINE = (
    "30 4 * * * cd /mnt/local-analysis/workspace-hub && "
    'find logs/notifications/ -name "*.jsonl" -mtime +7 -delete 2>/dev/null || true'
)
A1_SESSION_CURATION_LINE = (
    "47 */6 * * * mkdir -p $WORKSPACE_HUB/logs/monitoring && "
    "PATH=$HOME/.local/bin:$PATH; cd /mnt/local-analysis/workspace-hub && "
    "bash scripts/curation/curate-session-memory.sh >> "
    "/mnt/local-analysis/workspace-hub/logs/monitoring/"
    "session-curation-$(date +\\%Y-\\%m-\\%d).log 2>&1"
)
A1_EQUALITY_REFRESH_LINE = (
    "50 */6 * * * PATH=$HOME/.local/bin:$PATH; "
    "cd /mnt/local-analysis/workspace-hub && "
    "bash scripts/readiness/equality-matrix-cron.sh >> "
    "/mnt/local-analysis/workspace-hub/logs/quality/"
    "equality-refresh-$(date +\\%Y-\\%m-\\%d).log 2>&1"
)


def _classify(line: str) -> str:
    catalog = yaml.safe_load((REPO / "config" / "scheduled-tasks" / "schedule-tasks.yaml").read_text())
    classes = yaml.safe_load((REPO / "config" / "workstations" / "harness-state-classes.yaml").read_text())
    registry = yaml.safe_load((REPO / "config" / "workstations" / "registry.yaml").read_text())
    ownership = ca.build_ownership_context(catalog, registry, classes, "dev-primary")
    return ct.classify_line_detail(line, ownership_context=ownership)["class"]


def _classify_detail(line: str) -> dict:
    catalog = yaml.safe_load((REPO / "config" / "scheduled-tasks" / "schedule-tasks.yaml").read_text())
    classes = yaml.safe_load((REPO / "config" / "workstations" / "harness-state-classes.yaml").read_text())
    registry = yaml.safe_load((REPO / "config" / "workstations" / "registry.yaml").read_text())
    ownership = ca.build_ownership_context(catalog, registry, classes, "dev-primary")
    return ct.classify_line_detail(line, ownership_context=ownership)


def test_llm_wiki_corpus_ingest_is_preserved():
    assert _classify(A1_LLM_WIKI_LINE) == "preserved_external"


def test_notification_purge_local_is_exactly_cataloged():
    assert _classify(A1_NOTIFICATION_PURGE_LINE) == "cataloged"


def test_duplicated_notification_purge_line_also_cataloged():
    # The a1 crontab has this line twice; both instances must classify the same.
    assert _classify(A1_NOTIFICATION_PURGE_LINE) == "cataloged"


def test_recent_a1_catalog_duplicates_are_exactly_owned():
    for line, task_id in (
        (A1_SESSION_CURATION_LINE, "session-curation"),
        (A1_EQUALITY_REFRESH_LINE, "equality-matrix-refresh"),
    ):
        assert _classify_detail(line) == {
            "line": line,
            "class": "cataloged",
            "reason": "legacy-exact-line",
            "catalog_task_id": task_id,
            "variant_id": "ace-linux-1-pre-managed-block",
        }


def test_recent_a1_catalog_duplicates_are_deduped_into_managed_block():
    live = A1_SESSION_CURATION_LINE + "\n" + A1_EQUALITY_REFRESH_LINE + "\n"
    result = ca.run_cutover(
        "dev-primary", apply=False, ts="recent-a1-duplicates", _read=lambda: live
    )

    assert result["status"] == "dry-run"
    assert result["new_text"].count("curate-session-memory.sh") == 1
    assert result["new_text"].count("equality-refresh-$(date") == 1
    assert A1_SESSION_CURATION_LINE not in result["new_text"]
    assert A1_EQUALITY_REFRESH_LINE not in result["new_text"]

    rerun = ca.run_cutover(
        "dev-primary", apply=False, ts="recent-a1-idempotent", _read=lambda: result["new_text"]
    )
    assert rerun["status"] == "dry-run"
    assert rerun["new_text"] == result["new_text"]


def test_notification_purge_catalog_owned_line_is_deduped_without_apply_rollback(monkeypatch, tmp_path):
    monkeypatch.setattr(ca, "BACKUP_DIR", tmp_path / "bk")
    state = {"crontab": A1_NOTIFICATION_PURGE_LINE + "\n" + A1_NOTIFICATION_PURGE_LINE + "\n"}
    res = ca.run_cutover(
        "dev-primary",
        apply=True,
        ts="notification-purge",
        _read=lambda: state["crontab"],
        _write=lambda txt: state.update(crontab=txt),
        _daemons=lambda pat: False,
    )
    assert res["status"] == "applied"
    assert state["crontab"].count("find logs/notifications/") == 1
    assert "rolled-back" not in res["status"]


def test_state_classes_still_parses_with_expected_counts():
    classes = yaml.safe_load((REPO / "config" / "workstations" / "harness-state-classes.yaml").read_text())
    # 5 classes unchanged
    assert set(classes["classes"]) == {
        "role-managed", "git-managed", "machine-private", "secret", "intentionally-divergent",
    }
    # 2 hooks_known unchanged
    assert len(classes["hooks_known"]) == 2
    owners_ext = [e["owner"] for e in classes["preserved_external"]]
    assert owners_ext.count("deckhand") >= 3
    assert "llm-wiki" in owners_ext
    assert any(
        entry.get("catalog_task_id") == "notification-purge"
        for entry in classes.get("preserved_local", [])
    )
    # preserved_local: 2 a2 + 3 a1 catalog-owned legacy variants = 5
    assert len(classes["preserved_local"]) == 5
    owners_loc = [e["owner"] for e in classes["preserved_local"]]
    assert owners_loc.count("ace-linux-2") == 2
    assert owners_loc.count("ace-linux-1") == 3
    catalog_ids = {e.get("catalog_task_id") for e in classes["preserved_local"]}
    assert {"notification-purge", "session-curation", "equality-matrix-refresh"} <= catalog_ids
