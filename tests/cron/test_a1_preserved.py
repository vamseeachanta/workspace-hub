#!/usr/bin/env python3
"""Regression: the 2 a1 uncataloged live cron lines must classify as preserved (#2988 F2).

The F2 cron cutover on ace-linux-1 fail-closed-blocked on 2 live cron lines that no class
in harness-state-classes.yaml + the role catalog (schedule-tasks.yaml) recognised. This test
loads the REAL catalog + REAL state-classes, builds catalog_commands + fingerprints exactly as
cron_apply.py does, and asserts both lines classify as "preserved_external" (the keep-verbatim
return value of classify_line) — NOT "uncataloged".

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


def _classify(line: str) -> str:
    catalog = yaml.safe_load((REPO / "config" / "scheduled-tasks" / "schedule-tasks.yaml").read_text())
    classes = yaml.safe_load((REPO / "config" / "workstations" / "harness-state-classes.yaml").read_text())
    cat_cmds = ca.catalog_commands(catalog)
    ext_fps = ca.external_fingerprints(classes)
    return ct.classify_line(line, cat_cmds, ext_fps)


def test_llm_wiki_corpus_ingest_is_preserved():
    assert _classify(A1_LLM_WIKI_LINE) == "preserved_external"


def test_notification_purge_local_is_preserved():
    # Sanity: without the new entry this would be "uncataloged" (the absolute-path cd
    # defeats the 60-char `cd $WORKSPACE_HUB && find ...` catalog key).
    assert _classify(A1_NOTIFICATION_PURGE_LINE) == "preserved_external"


def test_duplicated_notification_purge_line_also_preserved():
    # The a1 crontab has this line twice; both instances must classify the same.
    assert _classify(A1_NOTIFICATION_PURGE_LINE) == "preserved_external"
    assert _classify(A1_NOTIFICATION_PURGE_LINE) == "preserved_external"


def test_state_classes_still_parses_with_expected_counts():
    classes = yaml.safe_load((REPO / "config" / "workstations" / "harness-state-classes.yaml").read_text())
    # 5 classes unchanged
    assert set(classes["classes"]) == {
        "role-managed", "git-managed", "machine-private", "secret", "intentionally-divergent",
    }
    # 2 hooks_known unchanged
    assert len(classes["hooks_known"]) == 2
    # preserved_external: 3 deckhand + 1 new llm-wiki = 4
    assert len(classes["preserved_external"]) == 4
    owners_ext = [e["owner"] for e in classes["preserved_external"]]
    assert owners_ext.count("deckhand") == 3
    assert "llm-wiki" in owners_ext
    # preserved_local: 2 a2 + 1 new a1 = 3
    assert len(classes["preserved_local"]) == 3
    owners_loc = [e["owner"] for e in classes["preserved_local"]]
    assert owners_loc.count("ace-linux-2") == 2
    assert "ace-linux-1" in owners_loc
