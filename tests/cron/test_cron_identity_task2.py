"""Task 2 regressions for exact destructive cron identity."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fixture_context():
    catalog = {
        "tasks": [{
            "id": "owned", "scheduler": "cron", "schedule": "0 1 * * *",
            "command": "cd $WORKSPACE_HUB && echo 'a|b' >> $LOG",
            "machines": ["linux-a"], "roles": [],
        }]
    }
    registry = {
        "machines": {
            "linux-a": {
                "hostname": "host-a", "hostname_aliases": ["alias-a"],
                "os": "linux", "workspace_root": "/repo",
                "harness_profile": {"roles": []},
            }
        }
    }
    classes = {
        "preserved_local": [{
            "owner": "linux-a", "catalog_task_id": "owned",
            "legacy_exact_lines": [{"id": "old", "line": "0 1 * * * cd /old && echo 'a|b' >> /tmp/log"}],
        }],
        "preserved_external": [{
            "owner": "external", "fingerprint": {"command_contains": "echo"},
        }],
    }
    return catalog, registry, classes


def test_exact_identity_requires_complete_line_bytes():
    ct = load("cron_transaction_task2", "scripts/cron/cron_transaction.py")
    catalog, registry, classes = fixture_context()
    context = ct.build_ownership_context(
        catalog, registry, classes, "linux-a", workspace_hub="/repo"
    )
    canonical = next(iter(context["canonical_exact_lines"].values()))[0]
    exact = ct.classify_line_detail(canonical, ownership_context=context)
    assert exact["class"] == "cataloged"
    assert exact["reason"] == "canonical-exact-line"
    assert exact["catalog_task_id"] == "owned"
    for near in (
        canonical.replace("0 1", "1 1", 1),
        canonical.replace("'a|b'", "a|b"),
        canonical + " 2>&1",
        canonical.replace("/repo", "/repo-copy"),
    ):
        assert ct.classify_line_detail(near, ownership_context=context)["class"] == "preserved_external"


def test_legacy_identity_is_exact_and_preservation_never_promotes():
    ct = load("cron_transaction_legacy_task2", "scripts/cron/cron_transaction.py")
    catalog, registry, classes = fixture_context()
    context = ct.build_ownership_context(catalog, registry, classes, "linux-a")
    legacy = "0 1 * * * cd /old && echo 'a|b' >> /tmp/log"
    detail = ct.classify_line_detail(legacy, ownership_context=context)
    assert (detail["class"], detail["reason"], detail["catalog_task_id"]) == (
        "cataloged", "legacy-exact-line", "owned"
    )
    assert ct.classify_line_detail(legacy + " 2>&1", ownership_context=context)["class"] == "preserved_external"


def test_apply_and_audit_build_identical_ownership_context():
    apply = load("cron_apply_task2", "scripts/cron/cron_apply.py")
    audit = load("cron_audit_task2", "scripts/cron/cron-audit.py")
    catalog, registry, classes = fixture_context()
    expected = apply.build_ownership_context(catalog, registry, classes, "linux-a")
    assert audit.build_ownership_context(catalog, registry, classes, "linux-a") == expected


def test_audit_preserves_full_shared_classification_detail():
    ct = load("cron_transaction_parity_task2", "scripts/cron/cron_transaction.py")
    audit = load("cron_audit_parity_task2", "scripts/cron/cron-audit.py")
    catalog, registry, classes = fixture_context()
    context = ct.build_ownership_context(catalog, registry, classes, "linux-a")
    line = "0 1 * * * cd /old && echo 'a|b' >> /tmp/log"
    expected = ct.classify_line_detail(line, ownership_context=context)
    result = audit.audit_crontab(
        line, [], [], ct.classify_line_detail, ownership_context=context
    )
    assert result["lines"] == [expected]
